import streamlit as st
import os
import json
import base64
import io
import uuid  # For generating unique filenames
from PIL import Image
from openai import OpenAI
import time

# Set Streamlit page configuration
st.set_page_config(page_title="🌟 Image Tagging and Description Generator", layout="wide")

# Directory structure and paths
PROCESSED_IMAGES_DIR = "processed_images"
PROJECTS_DIR = "projects"
CONFIG_FILE = "config.json"

# Ensure necessary directories exist
os.makedirs(PROCESSED_IMAGES_DIR, exist_ok=True)
os.makedirs(PROJECTS_DIR, exist_ok=True)

# Load configuration from config.json
with open(CONFIG_FILE, 'r') as f:
    config = json.load(f)

default_system_prompt = config['system_prompt']
model_name = config['model_name']
max_tokens = config['max_tokens']
response_format_config = config['response_format']

def main():
    st.title("🌟 Image Tagging and Description Generator")

    # Initialize session state variables
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = None

    if 'system_prompt' not in st.session_state:
        st.session_state.system_prompt = default_system_prompt

    # User input for OpenAI API key
    openai_api_key = st.text_input("Enter your OpenAI API Key", type="password")

    if openai_api_key:
        # Initialize the OpenAI client
        client = OpenAI(api_key=openai_api_key)
        st.success("API key set successfully!")

        # Tabs for project management and visualization
        tab1, tab2 = st.tabs(["Manage Projects", "View Visualization"])

        with tab1:
            manage_projects_tab(client)
        with tab2:
            view_visualization_tab()
    else:
        st.info("Please enter your OpenAI API key to create or modify projects.")

def manage_projects_tab(client):
    st.header("Manage Projects")

    # Section 1: List existing projects with options to open or delete
    st.subheader("Project Overview")
    projects = [f.split(".")[0] for f in os.listdir(PROJECTS_DIR) if f.endswith(".json")]
    if projects:
        for project_name in projects:
            col1, col2, col3 = st.columns([4, 1, 1])
            col1.write(project_name)
            if col2.button("Open", key=f"open_{project_name}"):
                st.session_state.selected_project = project_name
                st.session_state.uploaded_files = None  # Reset uploaded files when changing projects
                st.rerun()
            if col3.button("Delete", key=f"delete_{project_name}"):
                project_path = os.path.join(PROJECTS_DIR, f"{project_name}.json")
                if os.path.exists(project_path):
                    os.remove(project_path)
                    st.success(f"Project '{project_name}' deleted successfully!")
                    if 'selected_project' in st.session_state and st.session_state.selected_project == project_name:
                        st.session_state.selected_project = None
                        st.session_state.uploaded_files = None
                    st.rerun()
    else:
        st.info("No projects available. Please create a new project.")

    # Section 2: Create a new project
    st.subheader("Create New Project")
    new_project_name = st.text_input("Enter a new project name")
    if st.button("Create Project") and new_project_name:
        project_path = os.path.join(PROJECTS_DIR, f"{new_project_name}.json")
        if not os.path.exists(project_path):
            with open(project_path, 'w') as f:
                json.dump({"images": []}, f)
            st.success(f"Project '{new_project_name}' created successfully!")
            st.session_state.selected_project = new_project_name
            st.session_state.uploaded_files = None
            st.rerun()
        else:
            st.warning("Project with this name already exists.")

    # Section 3: Open and manage a selected project
    if 'selected_project' in st.session_state and st.session_state.selected_project:
        selected_project = st.session_state.selected_project
        st.subheader(f"Managing Project: {selected_project}")
        project_path = os.path.join(PROJECTS_DIR, f"{selected_project}.json")
        if os.path.exists(project_path):
            with open(project_path, 'r') as f:
                project_data = json.load(f)

            # Allow user to modify the system prompt
            st.subheader("Edit System Prompt")
            st.session_state.system_prompt = st.text_area("System Prompt", value=st.session_state.system_prompt, height=100)

            # Upload images to the selected project
            st.subheader("Upload Images to Project")
            uploaded_files = st.file_uploader("Upload Images", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True, key='file_uploader')
            if uploaded_files:
                if st.button("Process Uploaded Images"):
                    st.session_state.uploaded_files = uploaded_files

            if st.session_state.uploaded_files:
                for uploaded_file in st.session_state.uploaded_files:
                    image = Image.open(uploaded_file)

                    # Resize and compress image
                    image = resize_and_compress_image(image, max_size=(500, 500), max_bytes=150000)

                    # Generate a unique filename
                    unique_filename = f"{uuid.uuid4().hex}_{uploaded_file.name}"
                    image_path = os.path.join(PROCESSED_IMAGES_DIR, unique_filename)

                    # Save the image
                    image.save(image_path, format="JPEG", quality=85)

                    # Add image info to project data
                    project_data["images"].append({
                        "filename": unique_filename,
                        "original_filename": uploaded_file.name,
                        "description": "",
                        "tags": []
                    })
                    st.success(f"Image '{uploaded_file.name}' uploaded successfully!")

                # Save updated project data
                with open(project_path, 'w') as f:
                    json.dump(project_data, f, indent=4)
                st.session_state.uploaded_files = None  # Reset after processing
                st.rerun()

            # Display project images and their data
            st.subheader("Images in Project")
            if project_data["images"]:
                for idx, image_info in enumerate(project_data["images"]):
                    st.image(os.path.join(PROCESSED_IMAGES_DIR, image_info["filename"]), width=150)
                    st.text(f"Filename: {image_info['original_filename']}")
                    st.text(f"Description: {image_info['description']}")
                    st.text(f"Tags: {', '.join(image_info['tags'])}")

                    col1, col2 = st.columns([1, 1])
                    if col1.button(f"Generate Description", key=f"gen_{selected_project}_{idx}"):
                        # Call OpenAI API to generate description and tags
                        try:
                            # Read the image and convert to base64
                            image_path = os.path.join(PROCESSED_IMAGES_DIR, image_info["filename"])
                            with open(image_path, "rb") as image_file:
                                img_data = image_file.read()
                            img_str = base64.b64encode(img_data).decode()

                            # Prepare messages
                            messages = [
                                {
                                    "role": "system",
                                    "content": st.session_state.system_prompt
                                },
                                {
                                    "role": "user",
                                    "content": [
                                        {"type": "text", "text": "Provide a brief description and list all prominent objects or elements in this image as tags. Output the result strictly in the JSON format specified by the schema."},
                                        {
                                            "type": "image_url",
                                            "image_url": {
                                                "url": f"data:image/jpeg;base64,{img_str}",
                                            },
                                        },
                                    ],
                                }
                            ]

                            # Construct the response_format with 'type' field
                            response_format = {
                                "type": "json_schema",
                                "json_schema": response_format_config
                            }

                            # Call the OpenAI API
                            response = client.chat.completions.create(
                                model=model_name,
                                messages=messages,
                                max_tokens=max_tokens,
                                response_format=response_format
                            )

                            # Access the response content
                            response_text = response.choices[0].message.content

                            # Parse the JSON string
                            try:
                                result = json.loads(response_text)
                                description = result['description']
                                tags = result['tags']
                            except json.JSONDecodeError as e:
                                st.error(f"Failed to parse JSON response for {image_info['original_filename']}: {e}")
                                continue

                            # Update description and tags
                            image_info["description"] = description
                            image_info["tags"] = tags

                            # Save updated project data
                            with open(project_path, 'w') as f:
                                json.dump(project_data, f, indent=4)
                            st.success(f"Description and tags updated for {image_info['original_filename']}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"An unexpected error occurred: {str(e)}")

                    if col2.button(f"Remove Image", key=f"rem_{selected_project}_{idx}"):
                        # Remove image from dataset
                        image_path = os.path.join(PROCESSED_IMAGES_DIR, image_info['filename'])
                        if os.path.exists(image_path):
                            os.remove(image_path)
                        project_data["images"].pop(idx)
                        with open(project_path, 'w') as f:
                            json.dump(project_data, f, indent=4)
                        st.success(f"Image '{image_info['original_filename']}' removed successfully!")
                        st.rerun()
            else:
                st.info("No images in this project. Please upload images to get started.")

            # Batch generate descriptions
            if st.button("Generate Descriptions for All Images", key=f"batch_gen_{selected_project}"):
                try:
                    progress_bar = st.progress(0)
                    total_images = len(project_data["images"])
                    for idx, image_info in enumerate(project_data["images"]):
                        if not image_info["description"]:
                            # Read the image and convert to base64
                            image_path = os.path.join(PROCESSED_IMAGES_DIR, image_info["filename"])
                            with open(image_path, "rb") as image_file:
                                img_data = image_file.read()
                            img_str = base64.b64encode(img_data).decode()

                            # Prepare messages
                            messages = [
                                {
                                    "role": "system",
                                    "content": st.session_state.system_prompt
                                },
                                {
                                    "role": "user",
                                    "content": [
                                        {"type": "text", "text": "Provide a brief description and list all prominent objects or elements in this image as tags. Output the result strictly in the JSON format specified by the schema."},
                                        {
                                            "type": "image_url",
                                            "image_url": {
                                                "url": f"data:image/jpeg;base64,{img_str}",
                                            },
                                        },
                                    ],
                                }
                            ]

                            # Construct the response_format with 'type' field
                            response_format = {
                                "type": "json_schema",
                                "json_schema": response_format_config
                            }

                            # Call the OpenAI API
                            response = client.chat.completions.create(
                                model=model_name,
                                messages=messages,
                                max_tokens=max_tokens,
                                response_format=response_format
                            )

                            # Access the response content
                            response_text = response.choices[0].message.content

                            # Parse the JSON string
                            try:
                                result = json.loads(response_text)
                                description = result['description']
                                tags = result['tags']
                            except json.JSONDecodeError as e:
                                st.error(f"Failed to parse JSON response for {image_info['original_filename']}: {e}")
                                continue

                            # Update description and tags
                            image_info["description"] = description
                            image_info["tags"] = tags

                            # Update progress bar
                            progress = (idx + 1) / total_images
                            progress_bar.progress(progress)
                    # Save updated project data
                    with open(project_path, 'w') as f:
                        json.dump(project_data, f, indent=4)
                    st.success("Descriptions and tags generated for all images.")
                    st.rerun()
                except Exception as e:
                    st.error(f"An unexpected error occurred while generating descriptions: {str(e)}")

def resize_and_compress_image(image, max_size=(500, 500), max_bytes=150000):
    image.thumbnail(max_size, Image.LANCZOS)
    # Compress to target file size if necessary
    quality = 85
    while True:
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG", quality=quality)
        if buffered.tell() <= max_bytes or quality <= 20:
            break
        quality -= 5
    buffered.seek(0)
    return Image.open(buffered)

def view_visualization_tab():
    st.header("View Visualization")

    # Selector for projects
    projects = [f.split(".")[0] for f in os.listdir(PROJECTS_DIR) if f.endswith(".json")]
    if projects:
        selected_project = st.selectbox("Select a project to visualize", projects)
        if selected_project:
            project_path = os.path.join(PROJECTS_DIR, f"{selected_project}.json")
            with open(project_path, 'r') as f:
                project_data = json.load(f)

            if project_data["images"]:
                # Prepare data for visualization
                nodes_data, links_data = prepare_graph_data(project_data)

                # Serialize data to JSON
                graph_data = {'nodes': nodes_data, 'links': links_data}
                graph_json = json.dumps(graph_data)

                # Display the graph
                st.subheader("Interactive Visualization")
                display_d3_graph(graph_json)
            else:
                st.info("No images in this project to visualize.")
    else:
        st.info("No projects available to visualize.")

def prepare_graph_data(project_data):
    nodes = []
    links = []
    node_ids = {}
    tag_ids = {}
    idx_counter = 0

    # Build nodes and edges
    for item in project_data["images"]:
        # Image node
        image_id = f"image_{idx_counter}"
        node_ids[item['filename']] = image_id
        idx_counter += 1

        # Encode image to base64
        image_path = os.path.join(PROCESSED_IMAGES_DIR, item['filename'])
        with open(image_path, 'rb') as img_file:
            img_data = img_file.read()
        img_base64 = base64.b64encode(img_data).decode('utf-8')
        img_src = f"data:image/jpeg;base64,{img_base64}"

        nodes.append({
            'id': image_id,
            'type': 'image',
            'filename': item['original_filename'],
            'description': item.get('description', ''),
            'image_data': img_src  # Use base64 encoded image
        })

        # Tag nodes and links
        for tag in item.get('tags', []):
            if tag not in tag_ids:
                tag_id = f"tag_{len(tag_ids)}"
                tag_ids[tag] = tag_id
                nodes.append({
                    'id': tag_id,
                    'type': 'tag',
                    'name': tag
                })
            else:
                tag_id = tag_ids[tag]

            # Link between image and tag
            links.append({
                'source': image_id,
                'target': tag_id
            })

    return nodes, links

def display_d3_graph(graph_json):
    # Read the D3.js visualization HTML template
    with open('d3_graph.html', 'r') as f:
        html_content = f.read()

    # Inject the graph data into the HTML
    html_content = html_content.replace('<!--GRAPH_DATA_PLACEHOLDER-->', graph_json)

    # Display the HTML in Streamlit
    st.components.v1.html(html_content, height=800, scrolling=True)

if __name__ == "__main__":
    main()
