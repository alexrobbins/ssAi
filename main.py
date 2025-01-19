from enum import Enum

import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from typing import TypedDict, List

load_dotenv()

client = OpenAI()

MESSAGES = "messages"
ROLE = "role"
CONTENT = "content"
OPENAI_MODEL = "openai_model"

SYSTEM_PROMPT = """
You are the AI for a spy agency. You help agents plan and execute their missions. You only use language or themes that
are appropriate for children under 12. Your responses should be interesting and end with a question to keep the agent
conversation going. Don't mention that this is all pretend.
"""

FIRST_MESSAGE = """
Hello agent. How can I help you with your mission today?
"""

class Role(Enum):
    developer = "developer"
    user = "user"
    assistant = "assistant"

class Message(TypedDict):
    role: Role
    content: str

def display_messages(messages: List[Message]):
    for message in messages:
        if message[ROLE] == Role.developer.value:
            continue
        with st.chat_message(message[ROLE]):
            st.markdown(message[CONTENT])

def get_response_from_openai(model, messages):
    return client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
    )

def main():
    st.logo(open("media/ssa-logo-big-red.png", "rb").read(), size="large")
    st.title("SSA AI")

    if st.button("Restart conversation"):
        st.session_state[MESSAGES] = []

    if OPENAI_MODEL not in st.session_state:
        st.session_state[OPENAI_MODEL] = "gpt-4o-mini"

    if MESSAGES not in st.session_state or not st.session_state[MESSAGES]:
        st.session_state[MESSAGES] = [
            {"role": Role.developer.value,
             "content": SYSTEM_PROMPT,},
            {"role": Role.assistant.value,
             "content": FIRST_MESSAGE,},
        ]

    if st.session_state[MESSAGES]:
        display_messages(st.session_state[MESSAGES])

    if prompt := st.chat_input("Enter message here"):
        with st.chat_message(Role.user.value):
            st.markdown(prompt)
        st.session_state[MESSAGES].append({"role": Role.user.value, "content": prompt})

        with st.chat_message(Role.assistant.value):
            stream = get_response_from_openai(st.session_state[OPENAI_MODEL], st.session_state[MESSAGES])
            response = st.write_stream(stream)
        st.session_state[MESSAGES].append({"role": Role.assistant.value, "content": response})

main()
