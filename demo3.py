import streamlit as st
import bot3
from bot3 import fun_bot
#import pandas as pd
#import spacy
#from spacy.matcher import PhraseMatcher
from PIL import Image

st. set_page_config(layout="wide")

# Display the logo in the sidebar
logo_path = r"fn.jpg"
logo_image = Image.open(logo_path)
st.sidebar.image(logo_image, use_column_width=True)
st.sidebar.markdown("# FickleNickle (Canada.)")


# Streamlit App
def main():
    print("\nStart \n")
    # Add a sidebar
    st.markdown("#### Investo ChatBot 💬 📚")
    print("session state: ", st.session_state)

    # Initialize Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # React to user input
    prompt = st.chat_input("What is up?")
    print("prompt: ", prompt)
    # Display the first user input in the chat container
    if prompt != None:
        #with st.chat_message("user"):
        #   st.markdown(prompt)
        # Append the user's input to the chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display the user input at the bottom above the user input bar
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
                       
        # Display assistant response in the chat message container
        with st.chat_message("assistant"):
            response = fun_bot(st.session_state.messages[-1]["content"])
            st.write(f"Investo: {response}")

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": f"Investo: {response}"})
        # Display assistant response in the chat message container
        #st.write(f"{response}")
    print("-------------------------------------------------------------")
    print("messages:", st.session_state.messages)

    # Display chat history in the chat container
    #for message in st.session_state.messages:
    #    with st.chat_message(message["role"]):
    #       st.markdown(message["content"])

    # Clear chat history button in the sidebar
    if st.sidebar.button("Clear Chat"):
        st.session_state.messages = []

if __name__ == "__main__":
    main()
