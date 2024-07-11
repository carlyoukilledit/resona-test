import streamlit as st
import requests
import time

# Define the URLs
url = "https://yuhezh.buildship.run/igt"
login_url = "https://yuhezh.buildship.run/uval"
credit_url = "https://yuhezh.buildship.run/credd"
deduct_credit_url = "https://yuhezh.buildship.run/1credu"

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

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ''
if 'credits' not in st.session_state:
    st.session_state.credits = 0

# Login function
def login(username, password):
    response = requests.get(f"{login_url}?Username={username}&Password={password}")
    if response.status_code == 200:
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.credits = check_credits(username)
        return True
    return False

# Check credits function
def check_credits(username):
    response = requests.get(f"{credit_url}?Username={username}")
    if response.status_code == 200:
        try:
            credits = int(response.text)
            return credits
        except ValueError:
            st.error("Error parsing credit information")
            return 0
    else:
        st.error(f"Error checking credits: {response.status_code}")
        return 0

# Deduct credit function
def deduct_credit(username):
    response = requests.get(f"{deduct_credit_url}?Username={username}")
    if response.status_code == 200:
        try:
            new_credit_balance = int(response.text)
            st.session_state.credits = new_credit_balance
            return True
        except ValueError:
            st.error("Error parsing credit information after deduction")
            return False
    else:
        st.error(f"Error deducting credit: {response.status_code}")
        return False

# Login section
if not st.session_state.logged_in:
    st.header("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if login(username, password):
            st.success("Logged in successfully!")
        else:
            st.error("Invalid username or password")

# Main application
if st.session_state.logged_in:
    st.title("Resona - Video to Audio")
    st.write(f"Welcome, {st.session_state.username}! You have {st.session_state.credits} credits remaining.")

    # Refresh credits button
    if st.button("Refresh Credits"):
        st.session_state.credits = check_credits(st.session_state.username)
        st.success(f"Credits refreshed. You have {st.session_state.credits} credits.")

    st.write("Upload a video file or provide a video link, and the AI will create the audio for it.")

    # Step 1: Upload Your Video or Video Link
    st.header("Step 1: Upload Your Video or Video Link")
    uploaded_file = st.file_uploader("Choose a video file", type=["mp4", "mov", "m4a"])
    video_link = st.text_input("Or enter a video link")

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
        current_credits = check_credits(st.session_state.username)
        if current_credits > 0:
            if uploaded_file is not None:
                files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            elif video_link:
                response = requests.get(video_link)
                if response.status_code == 200:
                    files = {'file': (video_link.split('/')[-1], response.content, 'video/mp4')}
                else:
                    st.error(f"Failed to download video from link: {response.status_code}")
                    files = None
            else:
                st.warning("Please upload a file or provide a video link before submitting.")
                files = None

            if files is not None:
                with st.spinner("Processing..."):
                    def process_video(files, description):
                        data = {'description': description}
                        response = requests.post(url, files=files, data=data)
                        return response

                    response = process_video(files, video_description)

                    if response.status_code == 200:
                        if deduct_credit(st.session_state.username):
                            st.success(f"Video successfully processed: {response.text}")
                            st.write(f"You now have {st.session_state.credits} credits remaining.")
                        else:
                            st.error("Failed to deduct credit. The video was processed, but credit deduction failed.")
                    else:
                        st.error(f"Video processing failed: {response.status_code} - {response.text}")
        else:
            st.error("You don't have enough credits to process this video.")

# Admin section (for demonstration purposes)
if st.session_state.logged_in and st.session_state.username == 'admin':
    st.header("Admin Section")
    st.write("Note: This section is for demonstration purposes only. In a real application, you would implement secure admin functionality.")
    target_user = st.text_input("Enter username to check credits")
    if st.button("Check User Credits"):
        user_credits = check_credits(target_user)
        st.write(f"{target_user} has {user_credits} credits.")
