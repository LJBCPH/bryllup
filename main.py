import streamlit as st
from datetime import datetime
import os
import random
import uuid
import time
import io


from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload
from google.oauth2.credentials import Credentials
import os
import io

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

# Load your service account JSON
import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

# ID of the Drive folder where files will be uploaded
DRIVE_FOLDER_ID = "1zzAZH9xwyUe1D-VykZ-xE5RWCkkRYbSK?dmr=1&ec=wgc-drive-globalnav-goto"

import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# Your folder ID (make sure the service account has access)
DRIVE_FOLDER_ID = "1zzAZH9xwyUe1D-VykZ-xE5RWCkkRYbSK"

# Load credentials from Streamlit secrets
import streamlit as st
SERVICE_ACCOUNT_INFO = st.secrets["SERVICE_ACCOUNT_INFO"]

credentials = service_account.Credentials.from_service_account_info(
    SERVICE_ACCOUNT_INFO,
    scopes=["https://www.googleapis.com/auth/drive"]
)

service = build('drive', 'v3', credentials=credentials)

results = drive_service.files().list(
    q="'1zzAZH9xwyUe1D-VykZ-xE5RWCkkRYbSK' in parents",
    fields="files(id, name)"
).execute()

print(results.get("files", []))

# Create a test file in the folder
file_metadata = {
    'name': 'test_upload.txt',
    'parents': [DRIVE_FOLDER_ID]
}

media = MediaIoBaseUpload(io.BytesIO(b"Hello from service account!"), mimetype='text/plain')

file = service.files().create(
    body=file_metadata,
    media_body=media,
    fields='id'
).execute()

st.write(f"Uploaded file ID: {file['id']}")


def upload_to_drive(file):
    try:
        # Authenticate using service account from st.secrets
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["SERVICE_ACCOUNT_INFO"],
            scopes=["https://www.googleapis.com/auth/drive"]
        )
        service = build('drive', 'v3', credentials=credentials)

        file_metadata = {
            'name': file.name,
            'parents': [DRIVE_FOLDER_ID]
        }

        media = MediaIoBaseUpload(io.BytesIO(file.read()), mimetype=file.type)

        service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        return True
    except Exception as e:
        st.error(f"Error uploading {file.name}: {e}")
        return False
        
     
st.set_page_config(
    page_title="💍 Vores bryllup",
    page_icon="💒",
    layout="centered",
)

# Header
st.markdown("<h1 style='text-align: center; color: #8b0000;'>Sandras og Lucas' Bryllup</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Del dine billeder fra dagen/aftenen med os!</p>", unsafe_allow_html=True)

st.markdown("---")

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = str(uuid.uuid4())

uploaded_files = st.file_uploader(
    "Vælg billede(r) som du vil dele med os",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True,
    key=st.session_state.uploader_key
)

from PIL import Image, ExifTags

def save_image_with_rotation_handling(uploaded_file, save_path):
    try:
        image = Image.open(uploaded_file)
        try:
            exif = image._getexif()
            if exif is not None:
                orientation_key = next(
                    (k for k, v in ExifTags.TAGS.items() if v == 'Orientation'), None
                )
                if orientation_key and orientation_key in exif:
                    orientation = exif[orientation_key]
                    if orientation == 3:
                        image = image.rotate(180, expand=True)
                    elif orientation == 6:
                        image = image.rotate(270, expand=True)
                    elif orientation == 8:
                        image = image.rotate(90, expand=True)
        except Exception:
            pass
        image.save(save_path)
    except Exception as e:
        st.error(f"Et billede kunne ikke gemmes {uploaded_file.name}: {e}")


# if uploaded_files:
#     st.success("TAK! 💕")
#
#     for file in uploaded_files:
#         # print(uploaded_files)
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         save_path = os.path.join(UPLOAD_DIR, f"{timestamp}_{file.name}")
#         save_image_with_rotation_handling(file, save_path)
#
#     st.toast(f"Dine billeder er gemt!", icon="📷")
#     #uploaded_files=None
#
#     st.markdown("### 🥰 Dine billeder er blevet gemt hos os!")
#     st.balloons()
#     #st.session_state.upload_files = None
#     time.sleep(5)
#     st.session_state.uploader_key=str(uuid.uuid4())
#     st.rerun()
# else:
#     st.markdown("⬆️ Brug uploaderen ovenover!")

from PIL import Image, ImageOps
from concurrent.futures import ThreadPoolExecutor

MAX_WIDTH = 2048
JPEG_QUALITY = 85

def process_and_save(uploaded_file):
    try:
        img = Image.open(uploaded_file)
        img = ImageOps.exif_transpose(img)  # Auto-rotate using EXIF
        if img.width > MAX_WIDTH:
            img.thumbnail((MAX_WIDTH, MAX_WIDTH))  # Maintain aspect ratio
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = os.path.join(UPLOAD_DIR, f"{timestamp}_{uploaded_file.name}")
        img.save(save_path, "JPEG", quality=JPEG_QUALITY, optimize=True)
        return uploaded_file.name
    except Exception as e:
        return f"Fejl ved {uploaded_file.name}: {e}"

if uploaded_files:
    for file in uploaded_files:  # <-- loop over each file
        upload_to_drive(file)
    #upload_to_drive(uploaded_files)

    st.success("Dine billeder er gemt! 📷")
    st.balloons()
    st.session_state.uploader_key = str(uuid.uuid4())
    st.rerun()
else:
    st.markdown("⬆️ Brug uploaderen ovenover!")

# Optional photo preview
#with st.expander("📁 Se nogle billeder fra aftenen her!"):
#    photos = os.listdir(UPLOAD_DIR)
#    sample_photos = random.sample(photos, min(len(photos), 5))
#    if photos:
#        for photo in sorted(sample_photos, reverse=True):
#            st.image(os.path.join(UPLOAD_DIR, photo), use_container_width=True)
#    else:
#        st.info("Ingen billeder endnu!")
#
#guess = st.text_input(
#    label="Fundet?", value="SLFLAG{...}"
#)
#if flag==guess:
#    st.write(f"Uhhhhhhhhhhhhh {flag=} og {guess=}")
#else:
#    st.write(f"Buuuuuuuuuuh {guess=} no gucci")
