import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
import streamlit as st
import json
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

#from langchain_ollama import ChatOllama

#model = ChatOllama(model="llama3.2")
# Initialize chat history in session state

model = ChatOpenAI(model="gpt-4o")

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# Display previous chat messages
for msg in st.session_state["chat_history"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input via chat
user_input = st.chat_input("Ask me something...")

if user_input:
    # Append user message to chat history
    st.session_state["chat_history"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Async handler to get response from the MCP agent
    async def run_agent():
        async with MultiServerMCPClient(
            {
                "math": {
                    "url": "http://localhost:5000/sse",
                    "transport": "sse",
                },
                "weather": {
                    "url": "http://localhost:5001/sse",
                    "transport": "sse",
                },
                "file_system": {
                    "url": "http://localhost:5002/sse",
                    "transport": "sse",
                }
            }
        ) as client:
            agent = create_react_agent(model, client.get_tools())
            response = await agent.ainvoke({"messages": user_input})
            return response

    # Run the async agent and display response
    response = asyncio.run(run_agent())

    
    with st.chat_message("assistant"):
        for msg in response["messages"]:
            role = msg.__class__.__name__.replace("Message", "")
            if hasattr(msg, "content") and msg.content:
                st.markdown(f"**{role}**: {msg.content}")
                st.session_state["chat_history"].append({"role": "assistant", "content": msg})
