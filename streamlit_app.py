import streamlit as st
import google.generativeai as genai

# Show title and description.
st.title("💬 Chatbot")
st.write(
    "This is a simple chatbot that uses Google's Gemini Flash-2.5 model to generate responses. "
    "To use this app, you need to provide a Google Generative AI API key, which you can get [here](https://makersuite.google.com/app/apikey). "
    "See [Google Generative AI documentation](https://ai.google.dev/) for more details."
)

# Ask user for their Google Generative AI API key via `st.text_input`.
api_key = st.text_input("Google Generative AI API Key", type="password")
if not api_key:
    st.info("Please add your Google Generative AI API key to continue.", icon="🗝️")
else:
    # Configure Google Generative AI client
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash-latest")

    # Create a session state variable to store the chat messages.
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display the existing chat messages via `st.chat_message`.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Create a chat input field to allow the user to enter a message.
    if prompt := st.chat_input("What is up?"):
        # Store and display the current prompt.
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Prepare conversation history for Gemini API
        history = []
        for m in st.session_state.messages:
            if m["role"] == "user":
                history.append({"role": "user", "parts": [m["content"]]})
            elif m["role"] == "assistant":
                history.append({"role": "model", "parts": [m["content"]]})

        # Generate a response using the Gemini API.
        try:
            response_stream = model.generate_content(
                history,
                stream=True,
            )
            # Stream and accumulate the response
            with st.chat_message("assistant"):
                full_response = ""
                for chunk in response_stream:
                    if chunk.candidates and chunk.candidates[0].content.parts:
                        part = chunk.candidates[0].content.parts[0].text
                        st.write(part, end="")
                        full_response += part
                st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"Error: {e}")
