import streamlit as st
from google import genai
from google.genai import types
import os

st.set_page_config(page_title="MHD Chatbot", page_icon="🤖")

# Login Function
def login():
    st.title("🔐 MHD Chatbot Login")

    if "login_status" not in st.session_state:
        st.session_state.login_status = False

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == st.secrets["admin_username"] and password == st.secrets["admin_password"]:
            st.session_state.login_status = True
            st.success("Login successful! Please proceed.")
        else:
            st.error("Invalid credentials. Try again.")

# Main Chat Page
def page_1():
    st.logo("logo_mhdinfotech.png", size="large")
    client = genai.Client(api_key=st.secrets["gemini_key"])

    def generate_response(prompt):
        try:
            system_prompt = f"You are a helpful AI Assistant named MHD-LLM developed by MHD Infotech. You help the user with their questions and if required you refer to this KNOWLEDGE BASE for answering: {st.session_state.get('knowledge_base', '')}\nKNOWLEDGE BASE END\n\nUSER INPUT: {prompt}"
            response = client.models.generate_content(
                model="models/gemini-2.5-flash-lite-preview-06-17",
                contents=system_prompt,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=0)
                ),
            )
            return response.text
        except Exception as e:
            return f"❌ Error: {str(e)}"

    st.title("🤖 MHD Chatbot")

    if "history" not in st.session_state:
        st.session_state.history = []

    for message in st.session_state.history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_input = st.chat_input("Say something...")
    if user_input:
        st.session_state.history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                bot_response = generate_response(user_input)
                st.markdown(bot_response)
        st.session_state.history.append({"role": "assistant", "content": bot_response})

# Knowledge Base Update Page
def update_knowledge():
    st.title("Update Knowledge Base")
    st.write("You can update the knowledge base of the chatbot from here.")

    knowledge_base_file = "knowledge_base.txt"

    if "knowledge_base" not in st.session_state:
        if os.path.exists(knowledge_base_file):
            with open(knowledge_base_file, "r") as file:
                st.session_state.knowledge_base = file.read()
        else:
            st.session_state.knowledge_base = ""

    if "knowledge_input" not in st.session_state:
        st.session_state.knowledge_input = ""

    st.text_area("Enter or modify the knowledge base:", key="knowledge_input", height=200)

    if st.button("Overwrite Knowledge Base"):
        with open(knowledge_base_file, "w") as file:
            file.write(st.session_state.knowledge_input.strip())
        st.session_state.knowledge_base = st.session_state.knowledge_input.strip()
        st.session_state.success_message = "✅ Knowledge base overwritten successfully!"

    if st.button("Append to Knowledge Base"):
        new_content = st.session_state.knowledge_input.strip()
        with open(knowledge_base_file, "a") as file:
            file.write(f"\n{new_content}")
        st.session_state.knowledge_base += f"\n{new_content}"
        st.session_state.success_message = "✅ Knowledge base updated successfully!"

    if st.button("Clear Input"):
        st.session_state.knowledge_input = ""
        st.text_area("Enter or modify the knowledge base:", key="knowledge_input", height=200)

    if "success_message" in st.session_state:
        st.success(st.session_state.success_message)
        st.session_state.success_message = None

    with st.expander("📘 View Current Knowledge Base"):
        st.code(st.session_state.knowledge_base or "Knowledge base is empty.", language="markdown")

# Application Routing
def run_app():
    pages = [
        st.Page(page_1, title="Chat with AI!"),
        st.Page(update_knowledge, title="Update Knowledge Base"),
    ]
    pg = st.navigation(pages, position="top")
    pg.run()

# Entry point with login control
if "login_status" not in st.session_state or not st.session_state.login_status:
    login()
else:
    run_app()
