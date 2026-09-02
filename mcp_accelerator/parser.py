import json
import os
import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Tuple, Any

import yaml

from mcp_accelerator.models import MicroserviceMetadata, ToolEndpoint, ToolParameter

class SpringBootParser:
    def __init__(self, root_dir: str):
        self.root_dir = os.path.abspath(root_dir)

    def scan_workspace(self) -> List[MicroserviceMetadata]:
        services: List[MicroserviceMetadata] = []
        for dirpath, dirnames, filenames in os.walk(self.root_dir):
            if "pom.xml" in filenames or "build.gradle" in filenames:
                # Exclude build output directories
                if any(part in dirpath for part in ["target", "build", ".venv", "node_modules"]):
                    continue
                service = self._parse_microservice(dirpath)
                if service:
                    services.append(service)
        return services

    def _parse_microservice(self, service_dir: str) -> Optional[MicroserviceMetadata]:
        service_name = os.path.basename(service_dir)
        port = 8080
        
        # Check pom.xml for artifactId
        pom_path = os.path.join(service_dir, "pom.xml")
        if os.path.exists(pom_path):
            try:
                tree = ET.parse(pom_path)
                root = tree.getroot()
                # Remove namespace if present
                ns = ""
                if root.tag.startswith("{"):
                    ns = root.tag.split("}")[0] + "}"
                artifact_id_elem = root.find(f"{ns}artifactId")
                if artifact_id_elem is not None and artifact_id_elem.text:
                    service_name = artifact_id_elem.text
            except Exception:
                pass

        # Check application.properties or application.yml for server.port
        prop_port, app_name = self._parse_config_files(service_dir)
        if prop_port:
            port = prop_port
        if app_name:
            service_name = app_name

        base_url = f"http://localhost:{port}"

        # Look for OpenAPI specification file
        openapi_file = self._find_openapi_spec(service_dir)
        tools: List[ToolEndpoint] = []
        has_openapi = False

        if openapi_file:
            has_openapi = True
            tools = self._parse_openapi_file(openapi_file, service_name, port, base_url)

        # Fallback: Parse Java Controller source files if no OpenAPI spec or 0 tools extracted
        if not tools:
            tools = self._parse_java_controllers(service_dir, service_name, port, base_url)

        if not tools and not has_openapi:
            return None

        # Infer domain category from service name
        domain = self._infer_domain(service_name)

        return MicroserviceMetadata(
            name=service_name,
            path=service_dir,
            port=port,
            domain=domain,
            has_openapi=has_openapi,
            openapi_spec_path=openapi_file,
            tools=tools
        )

    def _parse_config_files(self, service_dir: str) -> Tuple[Optional[int], Optional[str]]:
        port = None
        app_name = None
        
        # application.properties
        prop_path = os.path.join(service_dir, "src", "main", "resources", "application.properties")
        if os.path.exists(prop_path):
            with open(prop_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("server.port="):
                        try:
                            port = int(line.split("=")[1].strip())
                        except ValueError:
                            pass
                    elif line.startswith("spring.application.name="):
                        app_name = line.split("=")[1].strip()

        # application.yml / application.yaml
        for yml_name in ["application.yml", "application.yaml"]:
            yml_path = os.path.join(service_dir, "src", "main", "resources", yml_name)
            if os.path.exists(yml_path):
                try:
                    with open(yml_path, "r", encoding="utf-8", errors="ignore") as f:
                        data = yaml.safe_load(f)
                        if isinstance(data, dict):
                            p = data.get("server", {}).get("port")
                            if p:
                                port = int(p)
                            n = data.get("spring", {}).get("application", {}).get("name")
                            if n:
                                app_name = str(n)
                except Exception:
                    pass

        return port, app_name

    def _find_openapi_spec(self, service_dir: str) -> Optional[str]:
        # Check root or openapi/ folder for yaml/json
        candidates = [
            os.path.join(service_dir, "openapi.yaml"),
            os.path.join(service_dir, "openapi.yml"),
            os.path.join(service_dir, "openapi.json"),
            os.path.join(service_dir, "src", "main", "resources", "openapi.yaml"),
            os.path.join(service_dir, "src", "main", "resources", "openapi.json"),
        ]
        for c in candidates:
            if os.path.exists(c):
                return c
        return None

    def _parse_openapi_file(self, file_path: str, service_name: str, port: int, base_url: str) -> List[ToolEndpoint]:
        tools: List[ToolEndpoint] = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                if file_path.endswith(".json"):
                    spec = json.load(f)
                else:
                    spec = yaml.safe_load(f)

            paths = spec.get("paths", {})
            for path_str, methods in paths.items():
                if not isinstance(methods, dict):
                    continue
                for http_method, op in methods.items():
                    if http_method.lower() not in ["get", "post", "put", "delete", "patch"]:
                        continue
                    if not isinstance(op, dict):
                        continue

                    operation_id = op.get("operationId")
                    summary = op.get("summary") or op.get("description") or f"{http_method.upper()} {path_str}"
                    
                    # Generate clean tool name
                    if operation_id:
                        tool_name = self._to_snake_case(operation_id)
                    else:
                        tool_name = self._generate_tool_name(http_method, path_str)

                    # Extract parameters
                    parameters: List[ToolParameter] = []
                    for param in op.get("parameters", []):
                        p_name = param.get("name")
                        p_in = param.get("in")
                        p_required = param.get("required", False)
                        p_desc = param.get("description", "")
                        p_schema = param.get("schema", {})
                        p_type = p_schema.get("type", "string")

                        parameters.append(ToolParameter(
                            name=p_name,
                            param_type=p_type,
                            description=f"[{p_in}] {p_desc}",
                            required=p_required,
                            schema=p_schema
                        ))

                    # Extract request body schema
                    request_body_schema = {}
                    request_body = op.get("requestBody", {})
                    content = request_body.get("content", {})
                    json_media = content.get("application/json", {})
                    if "schema" in json_media:
                        req_schema = json_media["schema"]
                        if "$ref" in req_schema:
                            ref_path = req_schema["$ref"].split("/")
                            ref_schema = spec
                            for elem in ref_path:
                                if elem != "#":
                                    ref_schema = ref_schema.get(elem, {})
                            request_body_schema = ref_schema
                        else:
                            request_body_schema = req_schema

                    tools.append(ToolEndpoint(
                        name=tool_name,
                        description=summary,
                        path=path_str,
                        http_method=http_method.upper(),
                        service_name=service_name,
                        service_port=port,
                        base_url=base_url,
                        parameters=parameters,
                        request_body_schema=request_body_schema,
                        tags=op.get("tags", [])
                    ))
        except Exception as e:
            print(f"Warning: Failed to parse OpenAPI spec {file_path}: {e}")

        return tools

    def _parse_java_controllers(self, service_dir: str, service_name: str, port: int, base_url: str) -> List[ToolEndpoint]:
        tools: List[ToolEndpoint] = []
        java_src_dir = os.path.join(service_dir, "src", "main", "java")
        if not os.path.exists(java_src_dir):
            return tools

        for root, _, files in os.walk(java_src_dir):
            for file in files:
                if file.endswith("Controller.java"):
                    full_path = os.path.join(root, file)
                    controller_tools = self._parse_single_controller(full_path, service_name, port, base_url)
                    tools.extend(controller_tools)

        return tools

    def _parse_single_controller(self, file_path: str, service_name: str, port: int, base_url: str) -> List[ToolEndpoint]:
        tools: List[ToolEndpoint] = []
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            base_path = ""
            class_req_match = re.search(r'@RequestMapping\s*\(\s*["\']([^"\']+)["\']', content)
            if class_req_match:
                base_path = class_req_match.group(1)

            # Match method annotations: @GetMapping, @PostMapping, @PutMapping, @DeleteMapping
            method_pattern = re.compile(
                r'@(GetMapping|PostMapping|PutMapping|DeleteMapping)\s*(\(\s*["\']([^"\']*)["\']\s*\))?\s*\n\s*public\s+[\w<>]+\s+(\w+)\s*\(([^)]*)\)',
                re.MULTILINE
            )

            for match in method_pattern.finditer(content):
                annotation_type = match.group(1)
                sub_path = match.group(3) or ""
                method_name = match.group(4)
                params_str = match.group(5)

                http_method = {
                    "GetMapping": "GET",
                    "PostMapping": "POST",
                    "PutMapping": "PUT",
                    "DeleteMapping": "DELETE"
                }.get(annotation_type, "GET")

                full_endpoint_path = (base_path.rstrip("/") + "/" + sub_path.lstrip("/")).rstrip("/")
                if not full_endpoint_path:
                    full_endpoint_path = "/"

                tool_name = self._to_snake_case(method_name)
                description = f"Spring Controller operation: {method_name} ({http_method} {full_endpoint_path})"

                parameters: List[ToolParameter] = []
                if params_str:
                    for p in params_str.split(","):
                        p = p.strip()
                        if p:
                            p_parts = p.split()
                            if len(p_parts) >= 2:
                                p_type_str = p_parts[-2]
                                p_name_str = p_parts[-1]
                                parameters.append(ToolParameter(
                                    name=p_name_str,
                                    param_type=self._map_java_type_to_json_type(p_type_str),
                                    description=f"Parameter {p_name_str}",
                                    required=False
                                ))

                tools.append(ToolEndpoint(
                    name=tool_name,
                    description=description,
                    path=full_endpoint_path,
                    http_method=http_method,
                    service_name=service_name,
                    service_port=port,
                    base_url=base_url,
                    parameters=parameters
                ))
        except Exception:
            pass

        return tools

    def _infer_domain(self, service_name: str) -> str:
        s = service_name.lower()
        if any(k in s for k in ["patient", "ehr", "medical", "health", "clinical", "lab", "diagnosis"]):
            return "healthcare_domain"
        elif any(k in s for k in ["claim", "insurance", "billing", "payment", "invoice"]):
            return "insurance_domain"
        elif any(k in s for k in ["appointment", "schedule", "provider", "doctor", "booking"]):
            return "scheduling_domain"
        else:
            return "core_services_domain"

    def _to_snake_case(self, name: str) -> str:
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
        return re.sub(r'[^a-z0-9_]', '_', s2)

    def _generate_tool_name(self, method: str, path: str) -> str:
        clean_path = re.sub(r'\{[^}]+\}', '', path)
        parts = [p for p in clean_path.split("/") if p]
        return f"{method.lower()}_" + "_".join(parts)

    def _map_java_type_to_json_type(self, java_type: str) -> str:
        jt = java_type.lower()
        if jt in ["int", "integer", "long", "short", "byte"]:
            return "integer"
        elif jt in ["double", "float", "bigdecimal"]:
            return "number"
        elif jt in ["boolean", "bool"]:
            return "boolean"
        elif "list" in jt or "set" in jt or "collection" in jt or "[]" in jt:
            return "array"
        else:
            return "string"
