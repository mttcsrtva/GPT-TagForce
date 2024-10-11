# Image Tagging and Description Generator

## Introduction

This application allows users to:
- Generate image descriptions and tags using OpenAI's GPT model.
- Visualize relationships between images and tags in an interactive D3.js network graph.

## Features
- Users provide their OpenAI API key for secure and personalized usage.
- Project-based image management: add, view, and delete files in a project.
- Interactive visualization for exploring relationships between images and their tags.

## Installation
1. Clone the repository and install dependencies.
    ```bash
    git clone <repository-url>
    cd blank-app
    pip install -r requirements.txt
    ```

2. Run the app using Streamlit.
    ```bash
    streamlit run streamlit_app.py
    ```

## Usage
- Users can upload images and create separate projects.
- Each user must enter their own OpenAI API key to proceed.
- The generated output can be viewed interactively in the app.

