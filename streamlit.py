import streamlit as st

# Import your existing functions
from bot import Cosine_distance, extract_company_and_year, extract_and_year, fun_detail, simulate_typing, fun_bot

# Streamlit App
def main():
    st.title("Financial Chatbot")

    # User input
    user_question = st.text_input("Ask a question:")

    # Chatbot response
    if st.button("Ask"):
        response = fun_bot(user_question)
        st.write(f"Investo: {response}")

if __name__ == "__main__":
    main()
