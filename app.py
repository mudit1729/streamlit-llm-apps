import streamlit as st
import google.generativeai as genai
import PyPDF2
import os
import io

def read_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

# Sidebar for API key input
with st.sidebar:
    api_key_input = st.text_input("Enter Gemini API Key (optional)", type="password")
    st.markdown("Leave blank to use environment variable `API_KEY`")

# Determine which API key to use
if api_key_input:
    api_key = api_key_input
elif "API_KEY" in os.environ:
    api_key = os.environ["API_KEY"]
else:
    api_key = None

# Configure the Gemini API if we have a key
if api_key:
    genai.configure(api_key=api_key)
    model_available = True
else:
    st.warning("Please provide a Gemini API key to use this application.")
    model_available = False

st.title("📝 File Q&A with Google Gemini")
uploaded_file = st.file_uploader("Upload an article", type=("txt", "md", "pdf"))
question = st.text_input(
    "Ask something about the article",
    placeholder="Can you give me a short summary?",
    disabled=not uploaded_file or not model_available,
)

if uploaded_file and question and model_available:
    if uploaded_file.type == "application/pdf":
        article = read_pdf(uploaded_file)
    else:
        article = uploaded_file.read().decode()
    
    prompt = f"Here's an article:\n\n{article}\n\n{question}"

    model = genai.GenerativeModel("gemini-1.5-pro")
    
    st.write("### Answer")
    response_container = st.empty()
    full_response = ""

    with st.spinner("Generating response..."):
        try:
            response = model.generate_content(prompt, stream=True)

            for chunk in response:
                full_response += chunk.text
                response_container.markdown(full_response + "▌")

            response_container.markdown(full_response)

            # Add a button to regenerate the response
            if st.button("Regenerate Response"):
                full_response = ""
                with st.spinner("Regenerating response..."):
                    response = model.generate_content(prompt, stream=True)

                    for chunk in response:
                        full_response += chunk.text
                        response_container.markdown(full_response + "▌")

                response_container.markdown(full_response)
        
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.error("Please check your API key and try again.")