import streamlit as st
from az import upload_txt_to_blob, read_txt_from_blob
from openai import AzureOpenAI

CONTAINER_NAME = "poll"

client = AzureOpenAI(
    api_key=st.secrets["azure"]["AZURE_OPENAI_KEY"],
    api_version="2023-05-15",
    azure_endpoint="https://poll-rag-ai.openai.azure.com/",
)

AZURE_DEPLOYMENT_NAME = "gpt-4o"

def call_azure_openai(prompt: str, context: str) -> str:
    response = client.chat.completions.create(
        model=AZURE_DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": "Voici un document utilisateur. Réponds aux questions en te basant uniquement sur son contenu."},
            {"role": "user", "content": context},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=800,
    )
    return response.choices[0].message.content


st.title("💬 Assistant OpenAI + Azure Blob")

uploaded_file = st.file_uploader("📄 Upload un fichier .txt", type="txt")

if uploaded_file is not None:
    blob_name = uploaded_file.name

    try:
        upload_txt_to_blob(CONTAINER_NAME, blob_name, uploaded_file.getvalue())
        st.success(f"✅ Fichier '{blob_name}' uploadé avec succès dans Azure Blob Storage.")
    except Exception as e:
        st.error(f"❌ Erreur d'upload : {e}")
        st.stop()

    try:
        txt_content = read_txt_from_blob(CONTAINER_NAME, blob_name)
        st.text_area("📄 Contenu du fichier récupéré :", value=txt_content, height=200)
    except Exception as e:
        st.error(f"❌ Erreur de lecture depuis Azure Blob : {e}")
        st.stop()

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Fichier chargé ✅. Pose une question à propos de son contenu."}
        ]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Pose ta question à propos du fichier..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
    
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            assistant_reply = call_azure_openai(prompt, txt_content)
            response_placeholder.markdown(assistant_reply)

        st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
