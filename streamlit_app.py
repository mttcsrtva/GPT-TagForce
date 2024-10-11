import streamlit as st
import openai
import os
import json
from PIL import Image
import shutil
import pandas as pd
import base64
import io

# Set Streamlit page configuration
st.set_page_config(page_title="Image Tagging and Description Generator", layout="wide")

# Directory structure and paths
PROCESSED_IMAGES_DIR = "processed_images"
PROJECTS_DIR = "projects"

# Ensure necessary directories exist
os.makedirs(PROCESSED_IMAGES_DIR, exist_ok=True)
os.makedirs(PROJECTS_DIR, exist_ok=True)

# Load configuration from config.json
with open('config.json', 'r') as f:
    config = json.load(f)

system_prompt = config['system_prompt']
model_name = config['model_name']
max_tokens = config['max_tokens']
# Removed response_format since it is not used in this version of the API

def main():
    st.title("🌟 Image Tagging and Description Generator")

    # User input for OpenAI API key
    openai_api_key = st.text_input("Enter your OpenAI API Key", type="password")

    # Display available projects without requiring API key
    display_existing_projects()

    if openai_api_key:
        # Set OpenAI API key
        openai.api_key = openai_api_key
        st.success("API key set successfully!")

        # Tabs for project management and visualization
        tab1, tab2 = st.tabs(["Manage Projects", "View Visualization"])

        with tab1:
            manage_projects_tab(openai_api_key)
        with tab2:
            view_visualization_tab()
    else:
        st.info("Please enter your OpenAI API key to create or modify projects.")

def display_existing_projects():
    st.header("Existing Projects")
    projects = [f.split(".")[0] for f in os.listdir(PROJECTS_DIR) if f.endswith(".json")]
    if projects:
        selected_project = st.selectbox("Select a project to view", projects)
        if selected_project:
            project_path = os.path.join(PROJECTS_DIR, f"{selected_project}.json")
            with open(project_path, 'r') as f:
                project_data = json.load(f)

            st.subheader(f"Images in Project '{selected_project}'")
            for image_info in project_data["images"]:
                st.image(os.path.join(PROCESSED_IMAGES_DIR, image_info["filename"]), width=150)
                st.text(f"Filename: {image_info['filename']}")
                st.text(f"Description: {image_info['description']}")
                st.text(f"Tags: {', '.join(image_info['tags'])}")
    else:
        st.info("No projects available. Please create a new project after entering your API key.")

def manage_projects_tab(api_key):
    st.header("Manage Projects")
    # Allow user to modify system prompt
    st.subheader("System Prompt Configuration")
    global system_prompt
    system_prompt = st.text_area("Edit System Prompt", value=system_prompt, height=100)
    
    # Project creation and deletion
    project_name = st.text_input("Enter a new project name")
    if st.button("Create Project") and project_name:
        project_path = os.path.join(PROJECTS_DIR, f"{project_name}.json")
        if not os.path.exists(project_path):
            with open(project_path, 'w') as f:
                json.dump({"images": []}, f)
            st.success(f"Project '{project_name}' created successfully!")
        else:
            st.warning("Project with this name already exists.")

    if st.button("Delete Project") and project_name:
        project_path = os.path.join(PROJECTS_DIR, f"{project_name}.json")
        if os.path.exists(project_path):
            os.remove(project_path)
            st.success(f"Project '{project_name}' deleted successfully!")
        else:
            st.warning("Project with this name does not exist.")

    # Select an existing project to work with
    projects = [f.split(".")[0] for f in os.listdir(PROJECTS_DIR) if f.endswith(".json")]
    selected_project = st.selectbox("Select a project to manage", projects)

    if selected_project:
        project_path = os.path.join(PROJECTS_DIR, f"{selected_project}.json")
        with open(project_path, 'r') as f:
            project_data = json.load(f)

        # Upload images to the selected project
        uploaded_files = st.file_uploader("Upload Images", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
        if uploaded_files:
            for uploaded_file in uploaded_files:
                image = Image.open(uploaded_file)

                # Resize and compress image
                image = resize_and_compress_image(image, max_size=(500, 500), max_bytes=150000)
                image_path = os.path.join(PROCESSED_IMAGES_DIR, uploaded_file.name)
                image.save(image_path, format="JPEG", quality=85)

                # Add image info to project data
                project_data["images"].append({
                    "filename": uploaded_file.name,
                    "description": "",
                    "tags": []
                })

            # Save updated project data
            with open(project_path, 'w') as f:
                json.dump(project_data, f, indent=4)
            st.success("Images uploaded successfully!")

        # Display project images and their data
        st.subheader(f"Images in Project '{selected_project}'")
        for idx, image_info in enumerate(project_data["images"]):
            st.image(os.path.join(PROCESSED_IMAGES_DIR, image_info["filename"]), width=150)
            st.text(f"Filename: {image_info['filename']}")
            st.text(f"Description: {image_info['description']}")
            st.text(f"Tags: {', '.join(image_info['tags'])}")

            if st.button(f"Generate Description for {image_info['filename']}", key=f"gen_{idx}"):
                # Call OpenAI API to generate description and tags
                try:
                    with open(os.path.join(PROCESSED_IMAGES_DIR, image_info["filename"]), "rb") as image_file:
                        img_base64 = base64.b64encode(image_file.read()).decode('utf-8')
                    
                    response = openai.ChatCompletion.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": f"Describe the following image and provide tags: {image_info['filename']}"}
                        ],
                        max_tokens=max_tokens
                    )
                    response_text = response['choices'][0]['message']['content'].strip()

                    # Update description and tags
                    description, *tags = response_text.split('\n')
                    image_info["description"] = description
                    image_info["tags"] = [tag.strip() for tag in tags if tag.strip()]

                    # Save updated project data
                    with open(project_path, 'w') as f:
                        json.dump(project_data, f, indent=4)
                    st.success(f"Description and tags updated for {image_info['filename']}")
                except Exception as e:
                    st.error(f"Failed to generate description: {str(e)}")

            if st.button(f"Remove {image_info['filename']} from dataset", key=f"rem_{idx}"):
                # Remove image from dataset
                os.remove(os.path.join(PROCESSED_IMAGES_DIR, image_info['filename']))
                project_data["images"].remove(image_info)
                with open(project_path, 'w') as f:
                    json.dump(project_data, f, indent=4)
                st.success(f"Image '{image_info['filename']}' removed successfully!")


def resize_and_compress_image(image, max_size=(500, 500), max_bytes=150000):
    image.thumbnail(max_size, Image.ANTIALIAS)
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG", quality=85)
    while buffered.tell() > max_bytes:
        quality = int(buffered.tell() / max_bytes * 85)
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG", quality=max(quality, 10))
    return Image.open(buffered)

def view_visualization_tab():
    st.header("View Visualization")
    st.write("Visualization tab - Here, you can see the graph of relationships between images and tags.")

    # Placeholder - Future work to integrate D3.js visualization
    st.text("Visualization coming soon...")

if __name__ == "__main__":
    try:
        import openai
    except ImportError:
        st.error("The 'openai' library is not installed. Please install it by running: pip install openai")
    else:
        main()