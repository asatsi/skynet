"""
SpringBootParser — scans Spring Boot microservices, auto-generates an OpenAPI 3.0
specification from Java controller source code when one is not already present,
then proceeds with normal MCP tool extraction.
"""
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

    # ─────────────────────────────────────────────────────────────────────────
    # Public entry-point
    # ─────────────────────────────────────────────────────────────────────────

    def scan_workspace(self) -> List[MicroserviceMetadata]:
        services: List[MicroserviceMetadata] = []
        for dirpath, dirnames, filenames in os.walk(self.root_dir):
            if "pom.xml" in filenames or "build.gradle" in filenames:
                if any(part in dirpath for part in
                       ["target", "build", ".venv", "node_modules"]):
                    continue
                service = self._parse_microservice(dirpath)
                if service:
                    services.append(service)
        return services

    # ─────────────────────────────────────────────────────────────────────────
    # Core microservice parser (modified to auto-generate OpenAPI when absent)
    # ─────────────────────────────────────────────────────────────────────────

    def _parse_microservice(self, service_dir: str) -> Optional[MicroserviceMetadata]:
        service_name = os.path.basename(service_dir)
        port = 8080

        # Read artifactId from pom.xml
        pom_path = os.path.join(service_dir, "pom.xml")
        if os.path.exists(pom_path):
            try:
                tree = ET.parse(pom_path)
                root = tree.getroot()
                ns = root.tag.split("}")[0] + "}" if root.tag.startswith("{") else ""
                elem = root.find(f"{ns}artifactId")
                if elem is not None and elem.text:
                    service_name = elem.text
            except Exception:
                pass

        prop_port, app_name = self._parse_config_files(service_dir)
        if prop_port:
            port = prop_port
        if app_name:
            service_name = app_name

        base_url = f"http://localhost:{port}"

        # ── Try to find an existing OpenAPI spec ──────────────────────────────
        openapi_file = self._find_openapi_spec(service_dir)
        tools: List[ToolEndpoint] = []
        has_openapi = False

        if openapi_file:
            print(f"  ✅ OpenAPI spec found for '{service_name}': {openapi_file}")
            has_openapi = True
            tools = self._parse_openapi_file(openapi_file, service_name, port, base_url)

        else:
            # ── No spec on disk: notify user and synthesise one from Java ─────
            print(f"\n  ⚠️  No OpenAPI specification file found for service '{service_name}'.")
            print(f"      Searched locations:")
            for candidate in self._openapi_candidate_paths(service_dir):
                print(f"        • {candidate}")
            print(f"      → Parsing Java controller source code to synthesize"
                  f" an OpenAPI 3.0 specification…")

            generated_path = self._generate_openapi_from_java(
                service_dir, service_name, port, base_url
            )

            if generated_path:
                print(f"      ✅ OpenAPI specification synthesized and saved to:")
                print(f"         {generated_path}")
                print(f"      → Proceeding with the generated specification.\n")
                openapi_file = generated_path
                has_openapi = True
                tools = self._parse_openapi_file(
                    generated_path, service_name, port, base_url
                )
            else:
                print(f"      ⚠️  No Java controllers found — cannot synthesize"
                      f" an OpenAPI spec for '{service_name}'.")
                print(f"      → Falling back to raw annotation scanning.\n")
                tools = self._parse_java_controllers(
                    service_dir, service_name, port, base_url
                )

        if not tools and not has_openapi:
            return None

        return MicroserviceMetadata(
            name=service_name,
            path=service_dir,
            port=port,
            domain=self._infer_domain(service_name),
            has_openapi=has_openapi,
            openapi_spec_path=openapi_file,
            tools=tools,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # OpenAPI spec discovery
    # ─────────────────────────────────────────────────────────────────────────

    def _openapi_candidate_paths(self, service_dir: str) -> List[str]:
        return [
            os.path.join(service_dir, "openapi.yaml"),
            os.path.join(service_dir, "openapi.yml"),
            os.path.join(service_dir, "openapi.json"),
            os.path.join(service_dir, "src", "main", "resources", "openapi.yaml"),
            os.path.join(service_dir, "src", "main", "resources", "openapi.json"),
        ]

    def _find_openapi_spec(self, service_dir: str) -> Optional[str]:
        for c in self._openapi_candidate_paths(service_dir):
            if os.path.exists(c):
                return c
        return None

    # ─────────────────────────────────────────────────────────────────────────
    # OpenAPI YAML / JSON parser
    # ─────────────────────────────────────────────────────────────────────────

    def _parse_openapi_file(
        self,
        file_path: str,
        service_name: str,
        port: int,
        base_url: str,
    ) -> List[ToolEndpoint]:
        tools: List[ToolEndpoint] = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                spec = json.load(f) if file_path.endswith(".json") else yaml.safe_load(f)

            paths = spec.get("paths", {})
            components = spec.get("components", {})
            all_schemas = components.get("schemas", {})

            for path_str, methods in paths.items():
                if not isinstance(methods, dict):
                    continue
                for http_method, op in methods.items():
                    if http_method.lower() not in \
                            ["get", "post", "put", "delete", "patch"]:
                        continue
                    if not isinstance(op, dict):
                        continue

                    op_id = op.get("operationId")
                    summary = (op.get("summary")
                               or op.get("description")
                               or f"{http_method.upper()} {path_str}")

                    tool_name = (self._to_snake_case(op_id) if op_id
                                 else self._generate_tool_name(http_method, path_str))

                    parameters: List[ToolParameter] = []
                    for param in op.get("parameters", []):
                        p_schema = param.get("schema", {})
                        parameters.append(ToolParameter(
                            name=param.get("name", ""),
                            param_type=p_schema.get("type", "string"),
                            description=f"[{param.get('in','')}] {param.get('description','')}",
                            required=param.get("required", False),
                            schema=p_schema,
                        ))

                    # Resolve $ref in requestBody
                    request_body_schema: Dict[str, Any] = {}
                    rb = op.get("requestBody", {})
                    json_media = rb.get("content", {}).get("application/json", {})
                    if "schema" in json_media:
                        raw = json_media["schema"]
                        if "$ref" in raw:
                            ref_name = raw["$ref"].split("/")[-1]
                            request_body_schema = all_schemas.get(ref_name, {})
                        else:
                            request_body_schema = raw

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
                        tags=op.get("tags", []),
                    ))
        except Exception as e:
            print(f"  Warning: Failed to parse OpenAPI spec {file_path}: {e}")

        return tools

    # ─────────────────────────────────────────────────────────────────────────
    # ════════════════════════════════════════════════════════════════════════
    #  NEW: Java source → OpenAPI 3.0 synthesiser
    # ════════════════════════════════════════════════════════════════════════
    # ─────────────────────────────────────────────────────────────────────────

    def _generate_openapi_from_java(
        self,
        service_dir: str,
        service_name: str,
        port: int,
        base_url: str,
    ) -> Optional[str]:
        """
        Walk every *Controller.java file in the service, extract HTTP endpoints
        with their path/query/body parameters and Javadoc descriptions, then
        write a valid OpenAPI 3.0 YAML file to <service_dir>/openapi.yaml.

        Returns the path of the saved file, or None if no endpoints were found.
        """
        java_src = os.path.join(service_dir, "src", "main", "java")
        if not os.path.exists(java_src):
            return None

        paths_doc:  Dict[str, Any] = {}
        schemas:    Dict[str, Any] = {}
        tags:       List[Dict[str, str]] = []
        ctrl_count  = 0

        for root, _, files in os.walk(java_src):
            for fname in sorted(files):
                if not fname.endswith("Controller.java"):
                    continue
                fpath = os.path.join(root, fname)
                tag_name = fname.replace("Controller.java", "")
                ctrl_paths, ctrl_schemas = self._extract_openapi_paths_from_controller(
                    fpath, tag_name
                )
                if ctrl_paths:
                    ctrl_count += 1
                    # Merge paths (same URL can appear in multiple controllers)
                    for url, methods in ctrl_paths.items():
                        paths_doc.setdefault(url, {}).update(methods)
                    schemas.update(ctrl_schemas)
                    if not any(t["name"] == tag_name for t in tags):
                        tags.append({
                            "name": tag_name,
                            "description": f"Operations from {tag_name}Controller",
                        })

        if not paths_doc:
            return None

        spec: Dict[str, Any] = {
            "openapi": "3.0.0",
            "info": {
                "title": f"{service_name} API",
                "description": (
                    f"OpenAPI 3.0 specification auto-generated by MCP Accelerator "
                    f"from Java source code ({ctrl_count} controller(s) parsed)."
                ),
                "version": "1.0.0",
            },
            "servers": [{"url": base_url, "description": "Local service instance"}],
            "tags": tags,
            "paths": paths_doc,
        }
        if schemas:
            spec["components"] = {"schemas": schemas}

        out_path = os.path.join(service_dir, "openapi.yaml")
        with open(out_path, "w", encoding="utf-8") as f:
            yaml.dump(
                spec, f,
                sort_keys=False,
                allow_unicode=True,
                default_flow_style=False,
            )
        return out_path

    # ── Per-controller extraction ─────────────────────────────────────────────

    def _extract_openapi_paths_from_controller(
        self,
        file_path: str,
        tag_name: str,
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Parse one *Controller.java and return:
          paths_doc  – OpenAPI "paths" fragment
          schemas    – OpenAPI "components/schemas" fragment (request-body DTOs)
        """
        paths_doc: Dict[str, Any] = {}
        schemas:   Dict[str, Any] = {}

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            return paths_doc, schemas

        # ── Class-level base path ─────────────────────────────────────────────
        base_path = self._extract_class_base_path(content)

        # ── Walk lines, detect mapping annotations ────────────────────────────
        lines = content.split("\n")
        i = 0
        while i < len(lines):
            stripped = lines[i].strip()

            mapping = self._match_mapping_annotation(stripped)
            if mapping is None:
                i += 1
                continue

            http_method, sub_path = mapping

            # Javadoc immediately preceding this annotation block
            javadoc = self._extract_javadoc_before(lines, i)

            # Method signature (may follow across several annotation lines)
            sig, params_str, next_i = self._find_method_signature(lines, i)
            if sig is None:
                i += 1
                continue

            method_name, _return_type = sig

            # Full endpoint URL
            full_path = (
                base_path.rstrip("/") + "/" + sub_path.lstrip("/")
            ).rstrip("/") or "/"
            # Normalise doubled slashes
            full_path = re.sub(r"//+", "/", full_path)

            # Parse parameters
            path_params, query_params, body_type = self._parse_method_parameters(
                params_str
            )

            operation_id = self._to_snake_case(method_name)
            summary      = (javadoc.splitlines()[0].strip()
                            if javadoc else
                            f"{http_method} {full_path}")
            description  = javadoc if javadoc else ""

            operation: Dict[str, Any] = {
                "operationId": operation_id,
                "summary":     summary,
                "tags":        [tag_name],
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {"schema": {"type": "object"}}
                        },
                    },
                    "400": {"description": "Bad request"},
                    "404": {"description": "Not found"},
                    "500": {"description": "Internal server error"},
                },
            }
            if description:
                operation["description"] = description

            # Parameters
            op_params: List[Dict[str, Any]] = []
            for pp in path_params:
                op_params.append({
                    "name":     pp["name"],
                    "in":       "path",
                    "required": True,
                    "description": pp.get("description", ""),
                    "schema":   {"type": pp.get("type", "string")},
                })
            for qp in query_params:
                op_params.append({
                    "name":     qp["name"],
                    "in":       "query",
                    "required": qp.get("required", False),
                    "description": qp.get("description", ""),
                    "schema":   {"type": qp.get("type", "string")},
                })
            if op_params:
                operation["parameters"] = op_params

            # Request body
            if body_type:
                clean_type = re.sub(r"<.*>", "", body_type)  # strip generics
                if clean_type and clean_type[0].isupper():
                    # Looks like a DTO class — add a schema stub
                    if clean_type not in schemas:
                        schemas[clean_type] = {
                            "type":        "object",
                            "description": f"Request body DTO: {clean_type}",
                        }
                    operation["requestBody"] = {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": f"#/components/schemas/{clean_type}"
                                }
                            }
                        },
                    }
                else:
                    operation["requestBody"] = {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"type": "object"}
                            }
                        },
                    }

            paths_doc.setdefault(full_path, {})[http_method.lower()] = operation
            i = next_i

        return paths_doc, schemas

    # ── Annotation helpers ────────────────────────────────────────────────────

    def _extract_class_base_path(self, content: str) -> str:
        """Return the value of the class-level @RequestMapping, or ''."""
        for pat in [
            r'@RequestMapping\s*\(\s*(?:value\s*=\s*|path\s*=\s*)?["\']([^"\']+)["\']',
            r'@RequestMapping\s*\([^)]*?(?:value|path)\s*=\s*["\']([^"\']+)["\']',
        ]:
            m = re.search(pat, content)
            if m:
                return m.group(1)
        return ""

    def _match_mapping_annotation(
        self, line: str
    ) -> Optional[Tuple[str, str]]:
        """
        Detect an HTTP mapping annotation on a single stripped source line.
        Returns (HTTP_METHOD, sub_path) or None.
        Handles:
          @GetMapping("/path")
          @PostMapping(value = "/path")
          @PutMapping(path = "/path/{id}")
          @GetMapping          (no path → root of class mapping)
          @RequestMapping(method = RequestMethod.GET, value = "/path")
        """
        # @{Verb}Mapping ...
        simple = re.match(
            r'@(Get|Post|Put|Delete|Patch)Mapping'
            r'\s*(?:\(\s*(?:(?:value|path)\s*=\s*)?["\']([^"\']*)["\'][^)]*\)'
            r'|\(\s*\)'   # empty parens
            r'|\s*$)',     # no parens at all
            line,
        )
        if simple:
            verb_map = {
                "Get": "GET", "Post": "POST", "Put": "PUT",
                "Delete": "DELETE", "Patch": "PATCH",
            }
            return verb_map[simple.group(1)], (simple.group(2) or "")

        # @RequestMapping(method = RequestMethod.GET, value = "/path")
        if re.match(r'@RequestMapping\s*\(', line):
            meth = re.search(r'method\s*=\s*RequestMethod\.(\w+)', line)
            path = re.search(r'(?:value|path)\s*=\s*["\']([^"\']*)["\']', line)
            if meth:
                return meth.group(1).upper(), (path.group(1) if path else "")

        return None

    # ── Javadoc extractor ─────────────────────────────────────────────────────

    def _extract_javadoc_before(self, lines: List[str], annotation_idx: int) -> str:
        """
        Walk backwards from annotation_idx to find the nearest /** ... */ block
        that precedes this annotation (skipping other @annotations in between).
        Returns the cleaned description text, or ''.
        """
        # Collect the 20 lines above (or fewer)
        start = max(0, annotation_idx - 20)
        chunk = "\n".join(lines[start:annotation_idx])

        matches = list(re.finditer(r"/\*\*(.*?)\*/", chunk, re.DOTALL))
        if not matches:
            return ""

        raw = matches[-1].group(1)
        # Remove leading " * " on each line
        cleaned_lines = []
        for ln in raw.splitlines():
            ln = re.sub(r"^\s*\*\s?", "", ln)
            # Drop @param, @return, @throws Javadoc tags
            if re.match(r"\s*@(param|return|throws|exception)\b", ln):
                continue
            cleaned_lines.append(ln)

        return "\n".join(cleaned_lines).strip()

    # ── Method signature finder ───────────────────────────────────────────────

    def _find_method_signature(
        self,
        lines: List[str],
        start_idx: int,
    ) -> Tuple[Optional[Tuple[str, str]], str, int]:
        """
        Scan forward from start_idx to find the next 'public … methodName(params)'.
        Handles multi-line signatures and intervening @annotations.
        Returns: ((method_name, return_type), params_str, next_line_index)
        """
        buffer = ""
        for j in range(start_idx, min(start_idx + 30, len(lines))):
            buffer += " " + lines[j]
            m = re.search(
                r"\bpublic\s+([\w<>\[\],\s]+?)\s+(\w+)\s*\(([^)]*)\)",
                buffer,
            )
            if m:
                return_type = m.group(1).strip()
                method_name = m.group(2)
                params_str  = m.group(3)
                return (method_name, return_type), params_str, j + 1

        return None, "", start_idx + 1

    # ── Parameter parser ──────────────────────────────────────────────────────

    def _parse_method_parameters(
        self, params_str: str
    ) -> Tuple[List[Dict], List[Dict], Optional[str]]:
        """
        Parse the raw parameter list string of a Java method and classify each
        parameter as path, query, or request-body.

        Handles:
          @PathVariable Long id
          @PathVariable("patientId") Long id
          @RequestParam String name
          @RequestParam(value="q", required=false) String query
          @RequestBody @Valid CreatePatientRequest body
          @Valid @RequestBody PatientDTO dto
          HttpServletRequest req   (ignored — framework type)
        """
        path_params:  List[Dict] = []
        query_params: List[Dict] = []
        body_type: Optional[str] = None

        if not params_str.strip():
            return path_params, query_params, body_type

        for param in self._split_java_params(params_str):
            param = param.strip()
            if not param:
                continue

            # Skip Spring / Servlet framework helper params
            if re.search(
                r'\b(HttpServletRequest|HttpServletResponse|Model|'
                r'BindingResult|Errors|Principal|Authentication|'
                r'UriComponentsBuilder)\b',
                param,
            ):
                continue

            # ── @PathVariable ─────────────────────────────────────────────
            pv = re.search(
                r'@PathVariable\s*(?:\(\s*(?:value\s*=\s*)?["\']([^"\']+)["\'][^)]*\))?\s*'
                r'([\w<>\[\]]+)\s+(\w+)',
                param,
            )
            if pv:
                # explicit name in annotation takes priority
                name      = pv.group(1) or pv.group(3)
                java_type = pv.group(2)
                path_params.append({
                    "name":        name,
                    "type":        self._map_java_type_to_json_type(java_type),
                    "required":    True,
                    "description": "",
                })
                continue

            # ── @RequestParam ─────────────────────────────────────────────
            rp = re.search(
                r'@RequestParam\s*(?:\([^)]*\))?\s*([\w<>\[\]]+)\s+(\w+)',
                param,
            )
            if rp:
                name_attr     = re.search(
                    r'@RequestParam\s*\(\s*(?:value\s*=\s*|name\s*=\s*)?["\']([^"\']+)["\']',
                    param,
                )
                required_attr = re.search(r'required\s*=\s*(true|false)', param, re.I)
                name      = name_attr.group(1) if name_attr else rp.group(2)
                java_type = rp.group(1)
                required  = (required_attr.group(1).lower() == "true"
                             if required_attr else True)
                defval    = re.search(r'defaultValue\s*=\s*["\']', param)
                if defval:
                    required = False  # has a default → optional
                query_params.append({
                    "name":        name,
                    "type":        self._map_java_type_to_json_type(java_type),
                    "required":    required,
                    "description": "",
                })
                continue

            # ── @RequestBody ──────────────────────────────────────────────
            rb = re.search(
                r'@RequestBody\s+(?:@\w+\s+)*([\w<>\[\]]+)\s+\w+',
                param,
            )
            if rb:
                body_type = rb.group(1)
                continue

            # ── Unannotated parameter — treat as query if it looks simple ─
            unannotated = re.match(r'^([\w<>\[\]]+)\s+(\w+)$', param.strip())
            if unannotated:
                java_type = unannotated.group(1)
                pname     = unannotated.group(2)
                if not any(c.isupper() for c in java_type) \
                        or java_type in ("String", "Integer", "Long",
                                          "Boolean", "Double", "Float"):
                    query_params.append({
                        "name":        pname,
                        "type":        self._map_java_type_to_json_type(java_type),
                        "required":    False,
                        "description": "",
                    })

        return path_params, query_params, body_type

    def _split_java_params(self, params_str: str) -> List[str]:
        """Split 'a, b, c' by commas, respecting angle-bracket depth."""
        parts: List[str] = []
        depth = 0
        current = ""
        for ch in params_str:
            if ch in "<(":
                depth += 1
                current += ch
            elif ch in ">)":
                depth -= 1
                current += ch
            elif ch == "," and depth == 0:
                parts.append(current)
                current = ""
            else:
                current += ch
        if current.strip():
            parts.append(current)
        return parts

    # ─────────────────────────────────────────────────────────────────────────
    # Legacy fallback: raw Java annotation scanner (unchanged)
    # ─────────────────────────────────────────────────────────────────────────

    def _parse_java_controllers(
        self,
        service_dir: str,
        service_name: str,
        port: int,
        base_url: str,
    ) -> List[ToolEndpoint]:
        tools: List[ToolEndpoint] = []
        java_src_dir = os.path.join(service_dir, "src", "main", "java")
        if not os.path.exists(java_src_dir):
            return tools
        for root, _, files in os.walk(java_src_dir):
            for file in files:
                if file.endswith("Controller.java"):
                    fp = os.path.join(root, file)
                    tools.extend(
                        self._parse_single_controller(
                            fp, service_name, port, base_url
                        )
                    )
        return tools

    def _parse_single_controller(
        self,
        file_path: str,
        service_name: str,
        port: int,
        base_url: str,
    ) -> List[ToolEndpoint]:
        tools: List[ToolEndpoint] = []
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            base_path = ""
            cls_rm = re.search(
                r'@RequestMapping\s*\(\s*["\']([^"\']+)["\']', content
            )
            if cls_rm:
                base_path = cls_rm.group(1)

            method_pattern = re.compile(
                r'@(GetMapping|PostMapping|PutMapping|DeleteMapping)\s*'
                r'(\(\s*["\']([^"\']*)["\']\s*\))?\s*\n\s*'
                r'public\s+[\w<>]+\s+(\w+)\s*\(([^)]*)\)',
                re.MULTILINE,
            )

            for match in method_pattern.finditer(content):
                annotation_type = match.group(1)
                sub_path    = match.group(3) or ""
                method_name = match.group(4)
                params_str  = match.group(5)

                http_method = {
                    "GetMapping":    "GET",
                    "PostMapping":   "POST",
                    "PutMapping":    "PUT",
                    "DeleteMapping": "DELETE",
                }.get(annotation_type, "GET")

                full_path = (
                    base_path.rstrip("/") + "/" + sub_path.lstrip("/")
                ).rstrip("/") or "/"

                tool_name   = self._to_snake_case(method_name)
                description = (
                    f"Spring Controller operation: "
                    f"{method_name} ({http_method} {full_path})"
                )

                parameters: List[ToolParameter] = []
                if params_str:
                    for p in params_str.split(","):
                        p = p.strip()
                        if p:
                            p_parts = p.split()
                            if len(p_parts) >= 2:
                                parameters.append(
                                    ToolParameter(
                                        name=p_parts[-1],
                                        param_type=self._map_java_type_to_json_type(
                                            p_parts[-2]
                                        ),
                                        description=f"Parameter {p_parts[-1]}",
                                        required=False,
                                    )
                                )

                tools.append(
                    ToolEndpoint(
                        name=tool_name,
                        description=description,
                        path=full_path,
                        http_method=http_method,
                        service_name=service_name,
                        service_port=port,
                        base_url=base_url,
                        parameters=parameters,
                    )
                )
        except Exception:
            pass
        return tools

    # ─────────────────────────────────────────────────────────────────────────
    # Config file helpers
    # ─────────────────────────────────────────────────────────────────────────

    def _parse_config_files(
        self, service_dir: str
    ) -> Tuple[Optional[int], Optional[str]]:
        port = None
        app_name = None

        prop_path = os.path.join(
            service_dir, "src", "main", "resources", "application.properties"
        )
        if os.path.exists(prop_path):
            with open(prop_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("server.port="):
                        try:
                            port = int(line.split("=", 1)[1].strip())
                        except ValueError:
                            pass
                    elif line.startswith("spring.application.name="):
                        app_name = line.split("=", 1)[1].strip()

        for yml_name in ["application.yml", "application.yaml"]:
            yml_path = os.path.join(
                service_dir, "src", "main", "resources", yml_name
            )
            if os.path.exists(yml_path):
                try:
                    with open(yml_path, "r", encoding="utf-8", errors="ignore") as f:
                        data = yaml.safe_load(f)
                    if isinstance(data, dict):
                        p = data.get("server", {}).get("port")
                        if p:
                            port = int(p)
                        n = (data.get("spring", {})
                             .get("application", {}).get("name"))
                        if n:
                            app_name = str(n)
                except Exception:
                    pass

        return port, app_name

    # ─────────────────────────────────────────────────────────────────────────
    # Utility helpers
    # ─────────────────────────────────────────────────────────────────────────

    def _infer_domain(self, service_name: str) -> str:
        s = service_name.lower()
        if any(k in s for k in
               ["patient", "ehr", "medical", "health", "clinical",
                "lab", "diagnosis"]):
            return "healthcare_domain"
        if any(k in s for k in
               ["claim", "insurance", "billing", "payment", "invoice"]):
            return "insurance_domain"
        if any(k in s for k in
               ["appointment", "schedule", "provider", "doctor", "booking"]):
            return "scheduling_domain"
        return "core_services_domain"

    def _to_snake_case(self, name: str) -> str:
        s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
        s2 = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
        return re.sub(r"[^a-z0-9_]", "_", s2)

    def _generate_tool_name(self, method: str, path: str) -> str:
        clean = re.sub(r"\{[^}]+\}", "", path)
        parts = [p for p in clean.split("/") if p]
        return f"{method.lower()}_" + "_".join(parts)

    def _map_java_type_to_json_type(self, java_type: str) -> str:
        jt = java_type.lower()
        if jt in ["int", "integer", "long", "short", "byte"]:
            return "integer"
        if jt in ["double", "float", "bigdecimal"]:
            return "number"
        if jt in ["boolean", "bool"]:
            return "boolean"
        if "list" in jt or "set" in jt or "collection" in jt or "[]" in jt:
            return "array"
        return "string"
