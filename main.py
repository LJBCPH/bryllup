import streamlit as st
from datetime import datetime
import os
import random
import uuid
import time

# App settings
UPLOAD_DIR = "uploaded_photos"
os.makedirs(UPLOAD_DIR, exist_ok=True)

st.set_page_config(
    page_title="💍 Vores bryllup",
    page_icon="💒",
    layout="centered",
)

# Flag
with open('flag.txt', 'r') as file:
    # Read the entire content of the file
    flag = file.read()
st.markdown(f"""
<span style="position:absolute; left:-10000px; font-size:1px; user-select:text;">
{flag}
</span>
""", unsafe_allow_html=True)


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
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(process_and_save, uploaded_files))

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
