from typing import List, Dict
from mcp_accelerator.models import MicroserviceMetadata, DomainGroup, ToolEndpoint

class DomainClassifier:
    def categorize(self, services: List[MicroserviceMetadata]) -> List[DomainGroup]:
        domain_map: Dict[str, DomainGroup] = {}

        for service in services:
            domain_name = service.domain or "default_domain"
            
            if domain_name not in domain_map:
                readable_name = domain_name.replace("_", " ").title()
                domain_map[domain_name] = DomainGroup(
                    name=domain_name,
                    description=f"Domain server grouping tools for {readable_name}",
                    services=[],
                    tools=[]
                )
            
            domain_group = domain_map[domain_name]
            domain_group.services.append(service)
            
            existing_names = {t.name for t in domain_group.tools}
            for tool in service.tools:
                final_tool_name = tool.name
                if final_tool_name in existing_names:
                    prefix = service.name.replace("-", "_").replace(" ", "_").lower()
                    final_tool_name = f"{prefix}_{tool.name}"
                
                cloned_tool = ToolEndpoint(
                    name=final_tool_name,
                    description=tool.description,
                    path=tool.path,
                    http_method=tool.http_method,
                    service_name=tool.service_name,
                    service_port=tool.service_port,
                    base_url=tool.base_url,
                    parameters=tool.parameters,
                    request_body_schema=tool.request_body_schema,
                    tags=tool.tags
                )
                domain_group.tools.append(cloned_tool)
                existing_names.add(final_tool_name)

        return list(domain_map.values())
