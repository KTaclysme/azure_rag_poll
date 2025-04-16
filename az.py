from azure.storage.blob import BlobServiceClient
import streamlit as st

account_url = "https://pollragstockage.blob.core.windows.net"
account_key = st.secrets["azure"]["AZURE_STORAGE_KEY"]

blob_service_client = BlobServiceClient(account_url=account_url, credential=account_key)

def upload_txt_to_blob(container_name: str, blob_name: str, content: bytes):
    container_client = blob_service_client.get_container_client(container_name)
    container_client.upload_blob(name=blob_name, data=content, overwrite=True)

def read_txt_from_blob(container_name: str, blob_name: str) -> str:
    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(blob_name)
    downloader = blob_client.download_blob()
    return downloader.readall().decode("utf-8")
