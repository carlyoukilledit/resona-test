import streamlit as st
import requests
import time

# Define the URLs
url = "https://yuhezh.buildship.run/igt"
login_url = "https://yuhezh.buildship.run/uval"
credit_check_url = "https://yuhezh.buildship.run/credd"
credit_deduct_url = "https://yuhezh.buildship.run/1credu"

# ... (keep the CSS and session state initialization as before)

# Error handling wrapper for API calls
def api_call(url, params=None):
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response
    except requests.exceptions.HTTPError as errh:
        st.error(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        st.error(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        st.error(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        st.error(f"Something went wrong: {err}")
    return None

# Login function
def login(username, password):
    response = api_call(login_url, params={"Username": username, "Password": password})
    if response and response.status_code == 200:
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.credits = check_credits(username)
        return True
    return False

# Check credits function
def check_credits(username):
    response = api_call(credit_check_url, params={"Username": username})
    if response and response.status_code == 200:
        try:
            credits = int(response.text)
            return credits
        except ValueError:
            st.error("Error parsing credit information")
    return 0

# Deduct credit function
def deduct_credit(username):
    response = api_call(credit_deduct_url, params={"Username": username})
    if response and response.status_code == 200:
        try:
            new_credits = int(response.text)
            st.session_state.credits = new_credits
            return True
        except ValueError:
            st.error("Error parsing credit information after deduction")
    return False

# ... (keep the login section as before)

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

    # ... (keep the instructions as before)

    # Step 3: Submit
    st.header("Step 3: Submit")
    if st.button("Submit"):
        current_credits = check_credits(st.session_state.username)
        if current_credits > 0:
            if uploaded_file is not None:
                files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            elif video_link:
                try:
                    response = requests.get(video_link)
                    response.raise_for_status()
                    files = {'file': (video_link.split('/')[-1], response.content, 'video/mp4')}
                except requests.exceptions.RequestException as err:
                    st.error(f"Failed to download video from link: {err}")
                    files = None
            else:
                st.warning("Please upload a file or provide a video link before submitting.")
                files = None

            if files is not None:
                with st.spinner("Processing..."):
                    def process_video(files, description):
                        try:
                            response = requests.post(url, files=files, data={'description': description})
                            response.raise_for_status()
                            return response
                        except requests.exceptions.RequestException as err:
                            st.error(f"Error processing video: {err}")
                            return None

                    response = process_video(files, video_description)

                    if response and response.status_code == 200:
                        # Deduct credit only after successful processing
                        if deduct_credit(st.session_state.username):
                            st.success(f"Video successfully processed: {response.text}")
                            st.write(f"You now have {st.session_state.credits} credits remaining.")
                        else:
                            st.error("Video was processed, but failed to deduct credit. Please contact support.")
                    else:
                        st.error("Video processing failed. No credit was deducted. Please try again.")
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
