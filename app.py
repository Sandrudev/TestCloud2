import random
import string
import os
import telebot
import streamlit as st

# Settings for your app
TELEGRAM_BOT_TOKEN = '5660590671:AAHboouGd0fFTpdjJSZpTfrtLyWsK1GM2JE'
CHANNEL_ID = '-1002173127202'  # Your Telegram channel ID
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Create Telegram bot instance
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Function to generate random tokens
def generate_token(length=12):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Function to upload file
def upload_file(file, user_token):
    filename = file.name
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    with open(file_path, 'wb') as f:
        f.write(file.getbuffer())

    file_type = 'image' if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')) else 'video'
    
    # Send the file to the Telegram channel with the token as caption
    with open(file_path, 'rb') as f:
        try:
            bot.send_document(chat_id=CHANNEL_ID, document=f, caption=user_token)
        except telebot.apihelper.ApiException as e:
            st.error(f"Error sending file to Telegram: {e}")

# Function to check if a token exists in the Telegram channel
def check_token_in_channel(token):
    updates = bot.get_updates()
    for update in updates:
        if update.channel_post and update.channel_post.caption:
            if token in update.channel_post.caption:
                return True
    return False

# Streamlit UI
def main():
    st.title("Streamlit App with Telegram Integration")

    # Login section
    if 'admin_token' not in st.session_state:
        st.subheader("Login")
        login_token = st.text_input("Enter your token")

        if st.button("Login"):
            if check_token_in_channel(login_token):
                st.session_state['admin_token'] = login_token
                st.success("Login successful!")
                st.experimental_rerun()  # Reload the app to reflect logged-in state
            else:
                st.error("Invalid token! Please check and try again.")

        st.subheader("Or Register")
        if st.button("Register"):
            token = generate_token()
            with open('generated_tokens.txt', 'a') as f:  # Keep track of generated tokens (optional)
                f.write(f"{token}\n")
            bot.send_message(chat_id=CHANNEL_ID, text=f"New Token: {token}")
            st.success(f"Registration successful! Your token is: {token}")

    # After login, show the dashboard
    else:
        st.subheader("Dashboard")

        # Show file upload option
        uploaded_file = st.file_uploader("Choose a file to upload")
        if uploaded_file is not None:
            upload_file(uploaded_file, st.session_state['admin_token'])
            st.success("File uploaded successfully!")

        # Display uploaded files (Here we assume that files are sent with the token in the caption)
        st.subheader("Files Uploaded Under Your Token")
        updates = bot.get_updates()
        for update in updates:
            if update.channel_post and update.channel_post.caption == st.session_state['admin_token']:
                if update.channel_post.document:
                    file_url = update.channel_post.document.file_id
                    st.write(f"File: {file_url}")

        # Option to log out
        if st.button("Log Out"):
            del st.session_state['admin_token']
            st.experimental_rerun()

if __name__ == "__main__":
    main()

