# auth_handler.py
import streamlit as st
import time

class AuthManager:
    def __init__(self):
        if 'user' not in st.session_state:
            st.session_state.user = None

    def login_google_mock(self):
        """
        Simulates a serious Google OAuth Process.
        For production, replace with firebase_admin.auth.verify_id_token()
        """
        with st.spinner("Connecting to Google Secure Gateway..."):
            time.sleep(2) # Simulate API handshake
            
            # Mock Data - In real app, this comes from Google Decoded Token
            st.session_state.user = {
                "name": "Professional Trader",
                "email": "trader@gmail.com",
                "uid": "12345-abcde",
                "photo": "https://lh3.googleusercontent.com/a/default-user=s96-c" 
            }
            st.rerun()

    def logout(self):
        st.session_state.user = None
        st.rerun()

    def is_authenticated(self):
        return st.session_state.user is not None
    
    def get_user(self):
        return st.session_state.user
