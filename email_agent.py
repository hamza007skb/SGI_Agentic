from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from state import AgentState
from typing import Dict

from tools import fetch_email_tool, extract_email_info_tool, enquire_info_tool


workflow = StateGraph(AgentState)

def fetch_emails_node(state: AgentState):
    state["raw_email"] = fetch_email_tool.invoke({})
    return state

def extract_email_info_node(state: AgentState):
    # print(state["raw_email"])
    result = extract_email_info_tool.invoke(state)
    state["nic"] = result["nic"]
    state["client_name"] = result["client_name"]
    state["contact_number"] = result["contact_number"]
    state["senders_email"] = result["senders_email"]
    state["address"] = result["address"]
    return state

# {"nic":state["nic"], "client_name":state["client_name"], "contact_number":state["contact_number"]}

def enquire_info_node(state: AgentState):
    result = enquire_info_tool.invoke({
        "data": state
    })
    return {**state, **result}


workflow.add_node("fetch_emails_node", fetch_emails_node)
workflow.add_node("extract_email_info_node", extract_email_info_node)
workflow.add_node("enquire_info_node", enquire_info_node)

workflow.set_entry_point("fetch_emails_node")
workflow.add_edge("fetch_emails_node", "extract_email_info_node")
workflow.add_edge("extract_email_info_node", "enquire_info_node")
workflow.add_edge("enquire_info_node", END)

# Compile the graph
app = workflow.compile()

# Run the graph
result = app.invoke({})
print(result)
