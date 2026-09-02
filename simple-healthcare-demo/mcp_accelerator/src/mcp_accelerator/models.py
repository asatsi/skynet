from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

@dataclass
class ToolParameter:
    name: str
    param_type: str  # string, integer, number, boolean, object, array
    description: str = ""
    required: bool = False
    schema: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ToolEndpoint:
    name: str
    description: str
    path: str
    http_method: str  # GET, POST, PUT, DELETE
    service_name: str
    service_port: int
    base_url: str
    parameters: List[ToolParameter] = field(default_factory=list)
    request_body_schema: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

@dataclass
class MicroserviceMetadata:
    name: str
    path: str
    port: int = 8080
    domain: str = "default"
    has_openapi: bool = False
    openapi_spec_path: Optional[str] = None
    tools: List[ToolEndpoint] = field(default_factory=list)

@dataclass
class DomainGroup:
    name: str
    description: str
    services: List[MicroserviceMetadata] = field(default_factory=list)
    tools: List[ToolEndpoint] = field(default_factory=list)
