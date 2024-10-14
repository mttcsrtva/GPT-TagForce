# **GPT-TagForce**  
*A Research & Development Beta*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Welcome to **GPT-TagForce**, a beta-stage R&D tool designed to generate image descriptions and tags using OpenAI models. This app is a sandbox for exploring image-tag relationships through interactive graph visualization. Please note, it’s still under active development—expect a few rough edges while we continue refining the Force!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Installation (っ◕‿◕)っ

1. **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd GPT-TagForce
    ```

2. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Run the app**:
    ```bash
    streamlit run streamlit_app.py
    ```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Features ☆*:.˙.ؾ(≧□≦)o.˙.:*☆

- **Tag Generation**: Automatically generate image descriptions and comprehensive tags for each image using your OpenAI API key.
- **Project-Based Management**: Organize your images into projects for better management and isolation.
- **Interactive Visualization**: Explore how images and tags are related via a D3.js-powered graph.
- **Custom AI Instructions**: Modify the AI's behavior by adjusting the system prompt, such as the number of tags, level of detail, and tag format.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Usage •͡˘㇁•͡˘

- **Enter OpenAI API Key**: This app requires your personal API key for generating tags and descriptions.
- **Create Projects**: Manage multiple projects, each with its own set of images.
- **Upload Images**: Upload images and let AI generate detailed descriptions and tags for each.
- **Visualize**: View the relationships between images and tags in an interactive network graph.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Known Issues (╯°□°）╯​┻━┻

- **JSON Parsing**: Occasionally, the AI may respond with JSON that doesn’t match the schema. If this happens, a quick rerun usually resolves it.
- **Image Compression**: The image compression logic may struggle with large images. For best results, stick with smaller file sizes.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## About (づ ＼＾ ‿＾)］

Developed by **Mattia** at **The Visual Agency**, **GPT-TagForce** is an experimental project focused on AI-driven image analysis and tagging. Your feedback and testing are welcome as we continue to develop this research tool!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

