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

# Step 1: Build client config from st.secrets
client_config = {
    "web": {
        "client_id": st.secrets["web"]["client_id"],
        "project_id": st.secrets["web"]["project_id"],
        "auth_uri": st.secrets["web"]["auth_uri"],
        "token_uri": st.secrets["web"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["web"]["auth_provider_x509_cert_url"],
        "client_secret": st.secrets["web"]["client_secret"],
        "redirect_uris": st.secrets["web"]["redirect_uris"],
        "javascript_origins": st.secrets["web"]["javascript_origins"]
    }
}

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

if "credentials" not in st.session_state:
    flow = Flow.from_client_config(client_config, scopes=SCOPES)
    flow.redirect_uri = st.secrets["web"]["redirect_uris"][0]  # Cloud redirect URI
    auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")
    st.markdown(f"[Authorize Google Drive access]({auth_url})")
else:
    creds = Credentials.from_authorized_user_info(st.session_state["credentials"], SCOPES)
    service = build("drive", "v3", credentials=creds)
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
        file_metadata = {"name": uploaded_file.name}
        media = io.BytesIO(uploaded_file.read())

        file = service.files().create(
            body=file_metadata,
            media_body=io.BytesIO(media.getvalue()),
            fields="id"
        ).execute()

        st.success("Dine billeder er gemt! 📷")
        st.balloons()
        st.session_state.uploader_key = str(uuid.uuid4())
        st.rerun()
    else:
        st.markdown("⬆️ Brug uploaderen ovenover!")

    # Optional photo preview
    with st.expander("📁 Se nogle billeder fra aftenen her!"):
        photos = os.listdir(UPLOAD_DIR)
        sample_photos = random.sample(photos, min(len(photos), 5))
        if photos:
            for photo in sorted(sample_photos, reverse=True):
                st.image(os.path.join(UPLOAD_DIR, photo), use_container_width=True)
        else:
            st.info("Ingen billeder endnu!")
#
#guess = st.text_input(
#    label="Fundet?", value="SLFLAG{...}"
#)
#if flag==guess:
#    st.write(f"Uhhhhhhhhhhhhh {flag=} og {guess=}")
#else:
#    st.write(f"Buuuuuuuuuuh {guess=} no gucci")
