import streamlit as st
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

def main():
    st.title("Chatbot")

    # Load the model and tokenizer
    model_name = "openchat/openchat-3.5-0106"
    model = AutoModelForCausalLM.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # Define a pipeline for chatting
    chat_pipeline = pipeline("text2text-generation", model=model, tokenizer=tokenizer)

    # Chatbot interface
    user_input = st.text_input("You:", "")
    if st.button("Send"):
        response = chat_pipeline(user_input)[0]['generated_text']
        st.text_area("Chatbot:", value=response, height=100)

if __name__ == "__main__":
    main()
