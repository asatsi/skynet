from typing import TypedDict, Annotated, Optional
import operator

class LoanState(TypedDict):
    messages:             Annotated[list, operator.add]
    intent:               str
    entities:             dict
    selected_agents:      list
    tool_calls:           Annotated[list, operator.add]
    tool_results:         dict
    # MCP Gateway metadata (new)
    gateway_tools_count:  int
    selected_tool_names:  list   # tools Ollama chose OR fallback chose
    # HITL
    requires_hitl:        bool
    hitl_step_id:         Optional[int]
    hitl_context:         Optional[dict]
    hitl_decision:        Optional[str]
    final_response:       str
