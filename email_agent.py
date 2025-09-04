from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from state import AgentState
from typing import Dict

from tools import fetch_email_tool, extract_email_info_tool_individual, enquire_info_tool, check_group_tool, extract_email_info_tool_group


workflow = StateGraph(AgentState)

def fetch_emails_node(state: AgentState):
    state["raw_email"] = fetch_email_tool.invoke({})
    return state

def extract_email_info_node_individual(state: AgentState):
    result = extract_email_info_tool_individual.invoke(state)
    state["nic"] = result["nic"]
    state["client_name"] = result["client_name"]
    state["contact_number"] = result["contact_number"]
    state["senders_email"] = result["senders_email"]
    state["address"] = result["address"]
    return state

def extract_email_info_node_group(state: AgentState):
    result = extract_email_info_tool_group.invoke(state)
    state["ntn"] = result["ntn"]
    state["client_name"] = result["client_name"]
    state["contact_number"] = result["contact_number"]
    state["senders_email"] = result["senders_email"]
    state["address"] = result["address"]
    return state


def enquire_info_node(state: AgentState):
    group = False
    if state["group"] == "Group":
        group = True
    result = enquire_info_tool.invoke({
        "data": state,
        "group": group,
    })
    return {**state, **result}

def check_group_node(state: AgentState):
    result = check_group_tool.invoke({"email_data": state["raw_email"]})
    print(result)
    state["group"] = result
    return state

def group_router(state: AgentState):
    if state["group"] == "Group":
        return "Group"
    elif state["group"] == "Individual":
        return "Individual"
    elif state["group"] == "Unknown":
        return "Unknown"

def unknown_group_error_node(state: AgentState):
    return "unknown client group!!!!!!"


workflow.add_node("fetch_emails_node", fetch_emails_node)
workflow.add_node("check_group_node", check_group_node)
workflow.add_node("extract_email_info_node_individual", extract_email_info_node_individual)
workflow.add_node("extract_email_info_node_group", extract_email_info_node_group)
workflow.add_node("enquire_info_node", enquire_info_node)
workflow.add_node("unknown_group_error_node", unknown_group_error_node)

workflow.set_entry_point("fetch_emails_node")
workflow.add_edge("fetch_emails_node", "check_group_node")
workflow.add_conditional_edges(
    "check_group_node",
    group_router,
    {
        "Group": "extract_email_info_node_group",
        "Individual": "extract_email_info_node_individual",
        "Unknown": "unknown_group_error_node"
    }
)
workflow.add_edge("extract_email_info_node_group","enquire_info_node")
workflow.add_edge("extract_email_info_node_individual","enquire_info_node")
workflow.add_edge("enquire_info_node", END)
workflow.add_edge("unknown_group_error_node",END)


# Compile the graph
app = workflow.compile()

# Run the graph
result = app.invoke({})
print(result)
