import streamlit as st
import dropbox
from io import BytesIO
import re
import unicodedata
import datetime

# Store your Dropbox token in Streamlit secrets in production
DROPBOX_TOKEN = st.secrets["my_app"]["sec"]
dbx = dropbox.Dropbox(DROPBOX_TOKEN)

# Main uploads folder name
MAIN_FOLDER = "/bryllup"

def clean_filename(filename):
    """Remove invalid characters for Dropbox paths."""
    nfkd = unicodedata.normalize("NFKD", filename)
    filename = "".join(c for c in nfkd if not unicodedata.combining(c))
    filename = re.sub(r'[<>:"/\\|?*]', "", filename)
    filename = filename.strip()
    return filename

st.title("Upload multiple images to Dropbox")

uploaded_files = st.file_uploader(
    "Choose images",
    type=["jpg", "png", "jpeg"],
    accept_multiple_files=True
)

if uploaded_files:
    # Create a unique subfolder for this batch
    timestamp_folder = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    for uploaded_file in uploaded_files:
        file_name = clean_filename(uploaded_file.name)
        file_bytes = BytesIO(uploaded_file.read())

        # Full path: /streamlit_uploads/2025-08-14_12-30-00/filename.jpg
        path = f"{MAIN_FOLDER}/{timestamp_folder}/{file_name}"

        dbx.files_upload(
            file_bytes.getvalue(),
            path,
            mode=dropbox.files.WriteMode.overwrite
        )

        st.success(f"Uploaded {file_name} to Dropbox!")

        # Public link
        try:
            link = dbx.sharing_create_shared_link_with_settings(path).url
        except dropbox.exceptions.ApiError:
            link = dbx.sharing_list_shared_links(path).links[0].url

        st.write(f"[View {file_name}]({link})")
