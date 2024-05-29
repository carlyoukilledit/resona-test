import streamlit as st
import requests
import time

# Define the URL
url = "https://yuhezh.buildship.run/igt"

# Custom CSS for styling the submit button
st.markdown(
    """
    <style>
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        padding: 10px 26px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 33px;
        margin: 10px 2px;
        cursor: pointer;
        border-radius: 12px;
        border: none;
        transition: background-color 0.3s;
    }
    .stButton > button:hover {
        background-color: #45a049;
    }
    </style>
    """, 
    unsafe_allow_html=True
)

# Streamlit interface
st.title("Resona - Video to Audio")
st.write("Upload a video file and the AI will create the audio for it.")

# Step 1: Upload Your Video
st.header("Step 1: Upload Your Video")
uploaded_file = st.file_uploader("Choose a video file", type=["mp4", "mov", "m4a"])

# Step 2: Describe Your Video
st.header("Step 2: Describe Your Video")
video_description = st.text_area(
    "Video Description",
    placeholder="For example: This video contains a detailed tutorial on how to create a Streamlit app, demonstrating feature integration and best practices...",
    height=100
)

# Instructions for video description (below text area)
st.write("""
Tips for a helpful video description:
* Provide a brief summary of the video's content.
* Mention important points or highlights in the video.
* Describe any background music or sound effects.
* Specify the intended audience or context.
""")

# Step 3: Submit
st.header("Step 3: Submit")
if st.button("Submit"):
    if uploaded_file is not None:
        # Display details of the uploaded file
        st.write("Filename:", uploaded_file.name)
        st.write("File type:", uploaded_file.type)
        st.write("File size:", uploaded_file.size, "bytes")

        # Show a loading spinner
        with st.spinner("Uploading file..."):
            # Function to upload the file
            def upload_file(file, description):
                files = {'file': (file.name, file.getvalue(), file.type)}
                data = {'description': description}
                response = requests.post(url, files=files, data=data)
                return response

            # Upload the file
            response = upload_file(uploaded_file, video_description)

            # Display the result of the upload
            if response.status_code == 200:
                st.success(f"File successfully uploaded: {response.text}")
            else:
                st.error(f"File upload failed: {response.status_code} - {response.text}")
    else:
        st.warning("Please upload a file before submitting.")
