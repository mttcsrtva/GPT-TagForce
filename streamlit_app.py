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

def main():
    st.title("🌟 Image Tagging and Description Generator")

    # User input for OpenAI API key
    openai_api_key = st.text_input("Enter your OpenAI API Key", type="password")

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
        st.info("Please enter your OpenAI API key to proceed.")

def manage_projects_tab(api_key):
    st.header("Manage Projects")
    project_name = st.text_input("Enter a new project name")
    
    if st.button("Create Project") and project_name:
        project_path = os.path.join(PROJECTS_DIR, f"{project_name}.json")
        if not os.path.exists(project_path):
            with open(project_path, 'w') as f:
                json.dump({"images": []}, f)
            st.success(f"Project '{project_name}' created successfully!")
        else:
            st.warning("Project with this name already exists.")

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
                image_path = os.path.join(PROCESSED_IMAGES_DIR, uploaded_file.name)
                image.save(image_path)

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
        for image_info in project_data["images"]:
            st.image(os.path.join(PROCESSED_IMAGES_DIR, image_info["filename"]), width=150)
            st.text(f"Filename: {image_info['filename']}")
            st.text(f"Description: {image_info['description']}")
            st.text(f"Tags: {', '.join(image_info['tags'])}")

            if st.button(f"Generate Description for {image_info['filename']}"):
                # Call OpenAI API to generate description and tags
                try:
                    with open(os.path.join(PROCESSED_IMAGES_DIR, image_info["filename"]), "rb") as image_file:
                        img_base64 = base64.b64encode(image_file.read()).decode('utf-8')
                    
                    response = openai.ChatCompletion.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "You are an AI assistant specialized in art analysis. Provide detailed descriptions and comprehensive tags for paintings."},
                            {"role": "user", "content": f"Describe the following image and provide tags: {image_info['filename']}"}
                        ],
                        max_tokens=300
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