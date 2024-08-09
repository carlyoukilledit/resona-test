import streamlit as st
import requests
import os
import uuid

# Define the URLs
VIDEO_PROCESSING_URL = "https://yuhezh.buildship.run/upload-file"
LOGIN_URL = "https://yuhezh.buildship.run/uval"
CREDIT_CHECK_URL = "https://yuhezh.buildship.run/credd"
FILE_UPLOAD_URL = "https://transfer.sh/"  # We'll use transfer.sh as a temporary file host

# Custom CSS
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
        font-size: 18px;
        margin: 10px 2px;
        cursor: pointer;
        border-radius: 12px;
        border: none;
        transition: background-color 0.3s;
    }
    .stButton > button:hover {
        background-color: #45a049;
    }
    .upload-section {
        background-color: #f0f0f0;
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ''
    st.session_state.credits = 0
    st.session_state.video_processed = False

def api_call(url, params=None, data=None, json=None, headers=None, method='GET', files=None):
    try:
        if method == 'GET':
            response = requests.get(url, params=params, headers=headers)
        elif method == 'POST':
            response = requests.post(url, params=params, data=data, json=json, headers=headers, files=files)
        elif method == 'PUT':
            response = requests.put(url, data=data, headers=headers)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as err:
        st.error(f"API Error: {err}")
        return None

def login(username, password):
    response = api_call(LOGIN_URL, params={"Username": username, "Password": password})
    if response and response.status_code == 200:
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.credits = check_credits(username)
        return True
    return False

def check_credits(username):
    response = api_call(CREDIT_CHECK_URL, params={"Username": username})
    if response and response.status_code == 200:
        try:
            return int(response.text)
        except ValueError:
            st.error("Error parsing credit information")
    return 0

def upload_file(file):
    filename = f"{uuid.uuid4()}-{file.name}"
    headers = {'Content-Type': 'application/octet-stream'}
    response = api_call(f"{FILE_UPLOAD_URL}/{filename}", data=file.getvalue(), headers=headers, method='PUT')
    if response and response.status_code == 200:
        return response.text.strip()  # The response contains the download URL
    return None

def process_video(video_link, username, description):
    headers = {"Username": username}
    data = {'description': description if description else ' '}
    params = {'video_link': video_link}
    return api_call(VIDEO_PROCESSING_URL, params=params, data=data, headers=headers, method='POST')

def main():
    st.title("Resona - Video to Audio")

    if not st.session_state.logged_in:
        st.header("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if login(username, password):
                st.success("Logged in successfully!")
                st.experimental_rerun()
            else:
                st.error("Invalid username or password")
    else:
        st.write(f"Welcome, {st.session_state.username}! You have {st.session_state.credits} credits remaining.")

        if st.button("Refresh Credits"):
            st.session_state.credits = check_credits(st.session_state.username)
            st.success(f"Credits refreshed. You have {st.session_state.credits} credits.")

        st.write("Upload a video file, and the AI will create the audio for it.")

        uploaded_file = st.file_uploader("Choose a video file", type=["mp4", "mov", "m4a"])

        description = st.text_input("Positive Keywords (optional) - [**EXPERIMENTAL**]")

        if st.button("Process Video"):
            if st.session_state.credits > 0:
                if uploaded_file:
                    with st.spinner("Uploading file..."):
                        video_link = upload_file(uploaded_file)
                    
                    if video_link:
                        with st.spinner("Processing..."):
                            response = process_video(video_link, st.session_state.username, description)
                            if response and response.status_code == 200:
                                st.success(f"Video successfully processed: {response.text}")
                                st.session_state.credits = check_credits(st.session_state.username)
                                st.write(f"You now have {st.session_state.credits} credits remaining.")
                                st.session_state.video_processed = True
                            else:
                                st.error("Video processing failed. Please try again.")
                    else:
                        st.error("Failed to upload the file. Please try again.")
                else:
                    st.warning("Please upload a file before submitting.")
            else:
                st.error("You don't have enough credits to process this video.")

        if st.session_state.video_processed:
            if st.button("Download Output"):
                st.markdown('<a href="https://discord.gg/fbAn3f4QEj" target="_blank">Click here to download the output</a>', unsafe_allow_html=True)

        if st.session_state.username == 'admin':
            st.header("Admin Section")
            st.write("Note: This section is for demonstration purposes only.")
            target_user = st.text_input("Enter username to check credits")
            if st.button("Check User Credits"):
                user_credits = check_credits(target_user)
                st.write(f"{target_user} has {user_credits} credits.")

if __name__ == "__main__":
    main()
