import sys
import os
import streamlit as st
import pandas as pd
from PIL import Image
from dotenv import load_dotenv
import bcrypt


import matplotlib.pyplot as plt
# Add parent folder to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import internal modules
from utils.db_utils import connect_to_mongo
from scripts.ingest import ingest_folder
from scripts.augment import augment_folder
from scripts.split_dataset import split_dataset
from scripts.export_snapshots import export_snapshot

# Load environment variables
load_dotenv()
db = connect_to_mongo()

# --- Login Interface ---
def login():
    st.title("🔐 Radiologist Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_button = st.button("Login")

    if login_button:
        user = db.users.find_one({"username": username})
        if user and bcrypt.checkpw(password.encode(), user["password_hash"]):
            st.session_state["user"] = user
            st.session_state["logged_in"] = True
        else:
            st.error("Invalid credentials")

# --- Image Upload & Preview ---
def image_uploader():
    st.subheader("📤 Upload Image for Preview")
    uploaded_file = st.file_uploader("Choose an image file", type=["png", "jpg", "jpeg", "dcm"])
    
    if uploaded_file:
        if uploaded_file.name.endswith(".dcm"):
            import pydicom
            dicom_data = pydicom.dcmread(uploaded_file)

            # Extract pixel array and show image
            image = dicom_data.pixel_array
            st.image(image, caption="🩻 DICOM Image", use_column_width=True)

            # Show metadata
            st.markdown("### 📋 DICOM Metadata")
            metadata = {
                "Patient Name": getattr(dicom_data, "PatientName", "N/A"),
                "Patient ID": getattr(dicom_data, "PatientID", "N/A"),
                "Modality": getattr(dicom_data, "Modality", "N/A"),
                "Study Date": getattr(dicom_data, "StudyDate", "N/A"),
                "Image Dimensions": f"{image.shape[0]} x {image.shape[1]}",
                "Pixel Spacing": getattr(dicom_data, "PixelSpacing", "N/A"),
                "Bits Stored": getattr(dicom_data, "BitsStored", "N/A"),
                "Photometric Interpretation": getattr(dicom_data, "PhotometricInterpretation", "N/A")
            }

            for key, value in metadata.items():
                st.write(f"**{key}:** {value}")
        else:
            image = Image.open(uploaded_file)
            st.image(image, caption="🖼️ Uploaded Image", use_column_width=True)


def dataset_browser():
    st.subheader("🗂 Browse Dataset")
    base_path = "dataset/train"
    class_choice = st.selectbox("Choose class", ["pneumothorax", "no_pneumothorax"])
    image_files = os.listdir(os.path.join(base_path, class_choice))
    selected_image = st.selectbox("Select image", image_files)
    image_path = os.path.join(base_path, class_choice, selected_image)

    try:
        if selected_image.lower().endswith(".dcm"):
            import pydicom
            dicom_data = pydicom.dcmread(image_path)
            image = dicom_data.pixel_array
            st.image(image, caption=f"{class_choice}: {selected_image}", use_column_width=True)
        else:
            with open(image_path, "rb") as f:
                image_bytes = f.read()
            st.image(image_bytes, caption=f"{class_choice}: {selected_image}", use_column_width=True)
    except Exception as e:
        st.error(f"⚠️ Could not display image: {e}")

# --- Metadata Viewer ---
def show_labels():
    st.subheader("📋 Labels Metadata")
    try:
        labels_df = pd.read_csv("dataset/labels.csv")
        st.dataframe(labels_df)

        st.write("📌 Available columns:", list(labels_df.columns))

        search_id = st.text_input("🔍 Search by Image ID")
        if search_id:
            if "image_id" in labels_df.columns:
                result = labels_df[labels_df["image_id"] == search_id]
                st.write(result)
            else:
                st.error("❌ Column 'image_id' not found in labels.csv. Please check your file structure.")
    except FileNotFoundError:
        st.error("labels.csv not found in dataset folder.")

# --- Stage Viewer ---
def stage_viewer():
    st.subheader("🔍 View Dataset by Stage")
    stage = st.radio("Select stage", ["Raw", "Anonymized", "Augmented", "Snapshot"])
    stage_map = {
        "Raw": "data/raw",
        "Anonymized": "data/anonymized",
        "Augmented": "data/augmented",
        "Snapshot": "data/snapshots"
    }
    folder = stage_map[stage]
    if os.path.exists(folder):
        files = [f for f in os.listdir(folder) if f.lower().endswith((".png", ".jpg", ".jpeg", ".dcm"))]
        if files:
            selected = st.selectbox(f"{stage} files", files)
            file_path = os.path.join(folder, selected)
            if selected.endswith(".dcm"):
                import pydicom
                dicom_data = pydicom.dcmread(file_path)
                image = dicom_data.pixel_array
                st.image(image, caption=f"{stage}: {selected}", use_column_width=True)
            else:
                st.image(file_path, caption=f"{stage}: {selected}", use_column_width=True)
        else:
            st.warning(f"No image files found in {folder}")
    else:
        st.error(f"{folder} does not exist.")

# --- Action Panel ---
def action_panel():
    st.subheader("⚙️ Dataset Actions")
    option = st.selectbox("Choose action:", ["Ingest", "Augment", "Split Dataset", "Export Snapshot"])

    if option == "Ingest":
        ingest_mode = st.radio("Select ingestion mode", ["Single File", "Batch Folder"])
        if ingest_mode == "Single File":
            uploaded_dicom = st.file_uploader("Upload a DICOM file", type=["dcm"])
            subfolder = st.text_input("Subfolder name under data/ingest", "manual_upload")
            if st.button("Ingest Single File") and uploaded_dicom:
                temp_path = f"temp_{uploaded_dicom.name}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_dicom.getbuffer())
                ingest_folder(folder_path="data/raw", output_subfolder=subfolder)
                os.remove(temp_path)
                st.success("✅ Single file ingestion complete!")
            elif ingest_mode == "Batch Folder":
                folder = st.text_input("📂 Path to raw DICOM folder", "data/raw")
                subfolder = st.text_input("Subfolder name under data/ingest", "batch_upload")
                if st.button("Ingest Folder"):
                    ingest_folder(folder_path=folder, output_subfolder=subfolder)
                    st.success(f"✅ Batch ingestion complete to data/ingest/{subfolder}")

    elif option == "Augment":
        folder = st.text_input("📂 Path to anonymized folder", "data/anonymized")
        if st.button("Start Augmentation"):
            augment_folder(folder)
            st.success("✅ Augmentation complete!")

    elif option == "Split Dataset":
        if st.button("Split into Train/Val/Test"):
            split_dataset()
            st.success("✅ Dataset split complete!")

    elif option == "Export Snapshot":
        if st.button("Create Snapshot"):
            export_snapshot()
            st.success("✅ Snapshot created!")

def show_analytics():
    st.subheader("📊 Dataset Analytics")

    stages = {
        "Raw": "data/raw",
        "Anonymized": "data/anonymized",
        "Augmented": "data/augmented",
        "Snapshot": "data/snapshots"
    }

    selected_stage = st.selectbox("Choose stage", list(stages.keys()))
    folder = stages[selected_stage]

    if not os.path.exists(folder):
        st.warning(f"Folder not found: {folder}")
        return

    files = [f for f in os.listdir(folder) if f.lower().endswith((".png", ".jpg", ".jpeg", ".dcm"))]
    st.metric("🖼️ Total Images", len(files))

    # Class balance from folder names or labels.csv
    if selected_stage == "Raw" and os.path.exists("dataset/labels.csv"):
        labels_df = pd.read_csv("dataset/labels.csv")
        if "label" in labels_df.columns:
            class_counts = labels_df["label"].value_counts()
            fig, ax = plt.subplots()
            ax.bar(class_counts.index, class_counts.values, color=["#4CAF50", "#F44336"])
            ax.set_title("Class Distribution")
            st.pyplot(fig)

    # Image dimension stats (sample 10)
    sample_dims = []
    for f in files[:10]:
        try:
            path = os.path.join(folder, f)
            if f.endswith(".dcm"):
                import pydicom
                img = pydicom.dcmread(path).pixel_array
            else:
                img = Image.open(path)
            sample_dims.append(img.size if hasattr(img, "size") else img.shape[::-1])
        except:
            continue

    if sample_dims:
        widths, heights = zip(*sample_dims)
        st.write(f"📐 Avg Width: {sum(widths)//len(widths)} px")
        st.write(f"📐 Avg Height: {sum(heights)//len(heights)} px")

        fig, ax = plt.subplots()
        ax.hist(widths, bins=5, alpha=0.7, label="Width")
        ax.hist(heights, bins=5, alpha=0.7, label="Height")
        ax.legend()
        ax.set_title("Image Dimension Distribution")
        st.pyplot(fig)



# --- Main Dashboard ---
def dashboard():
    st.title("🧠 ML Dataset Manager")
    st.write(f"Logged in as: **{st.session_state['user']['username']}**")

    tabs = st.tabs(["📤 Upload", "🗂 Browse", "📋 Labels", "🔍 Stages", "⚙️ Actions", "📊 Analytics"])
    with tabs[0]: image_uploader()
    with tabs[1]: dataset_browser()
    with tabs[2]: show_labels()
    with tabs[3]: stage_viewer()
    with tabs[4]: action_panel()
    with tabs[5]: show_analytics()




# --- App Entry Point ---
if "user" not in st.session_state:
    login()
else:
    dashboard()
