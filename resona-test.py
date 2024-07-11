import streamlit as st
import requests
import json

# Define the URLs
VIDEO_PROCESSING_URL = "https://yuhezh.buildship.run/igt"
LOGIN_URL = "https://yuhezh.buildship.run/uval"
CREDIT_CHECK_URL = "https://yuhezh.buildship.run/credd"
CREDIT_DEDUCT_URL = "https://yuhezh.buildship.run/1credu"

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

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ''
    st.session_state.credits = 0

def api_call(url, params=None, files=None, data=None, json=None, method='GET'):
    try:
        if method == 'GET':
            response = requests.get(url, params=params)
        elif method == 'POST':
            response = requests.post(url, params=params, files=files, data=data, json=json)
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

def deduct_credit(username):
    response = api_call(CREDIT_DEDUCT_URL, params={"Username": username}, method='GET')
    if response and response.status_code == 200:
        try:
            st.session_state.credits = int(response.text)
            return True
        except ValueError:
            st.error("Error parsing credit information after deduction")
    return False

def process_video(files, description):
    return api_call(VIDEO_PROCESSING_URL, files=files, data={'description': description}, method='POST')

def main():
    st.title("Resona - Video to Audio")

    if not st.session_state.logged_in:
        st.header("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if login(username, password):
                st.success("Logged in successfully!")
            else:
                st.error("Invalid username or password")
    else:
        st.write(f"Welcome, {st.session_state.username}! You have {st.session_state.credits} credits remaining.")

        if st.button("Refresh Credits"):
            st.session_state.credits = check_credits(st.session_state.username)
            st.success(f"Credits refreshed. You have {st.session_state.credits} credits.")

        st.write("Upload a video file or provide a video link, and the AI will create the audio for it.")

        st.header("Step 1: Upload Your Video or Video Link")
        uploaded_file = st.file_uploader("Choose a video file", type=["mp4", "mov", "m4a"])
        video_link = st.text_input("Or enter a video link")

        st.header("Step 2: Describe Your Video")
        video_description = st.text_area(
            "Video Description",
            placeholder="For example: This video contains a detailed tutorial on how to create a Streamlit app, demonstrating feature integration and best practices...",
            height=100
        )

        st.write("""
        Tips for a helpful video description:
        * Provide a brief summary of the video's content.
        * Mention important points or highlights in the video.
        * Describe any background music or sound effects.
        * Specify the intended audience or context.
        """)

        st.header("Step 3: Submit")
        if st.button("Submit"):
            if st.session_state.credits > 0:
                files = None
                if uploaded_file:
                    files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                elif video_link:
                    response = api_call(video_link, method='GET')
                    if response:
                        files = {'file': (video_link.split('/')[-1], response.content, 'video/mp4')}
                    else:
                        st.error("Failed to download video from link.")
                
                if files:
                    with st.spinner("Processing..."):
                        response = process_video(files, video_description)
                        if response and response.status_code == 200:
                            if deduct_credit(st.session_state.username):
                                st.success(f"Video successfully processed: {response.text}")
                                st.write(f"You now have {st.session_state.credits} credits remaining.")
                            else:
                                st.error("Video was processed, but failed to deduct credit. Please contact support.")
                        else:
                            st.error("Video processing failed. No credit was deducted. Please try again.")
                else:
                    st.warning("Please upload a file or provide a valid video link before submitting.")
            else:
                st.error("You don't have enough credits to process this video.")

        if st.session_state.username == 'admin':
            st.header("Admin Section")
            st.write("Note: This section is for demonstration purposes only.")
            target_user = st.text_input("Enter username to check credits")
            if st.button("Check User Credits"):
                user_credits = check_credits(target_user)
                st.write(f"{target_user} has {user_credits} credits.")

if __name__ == "__main__":
    main()
