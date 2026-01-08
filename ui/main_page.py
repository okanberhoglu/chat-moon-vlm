import streamlit as st
from PIL import Image
from ui.base_page import BasePage
from config import SUPPORTED_IMAGE_TYPES, PAGE_CHAT


class MainPage(BasePage):
    
    @staticmethod
    def render():
        st.write("# ChatMoonVLM")
        
        image_file = st.file_uploader(
            "Upload an image", 
            type=SUPPORTED_IMAGE_TYPES
        )
        
        if image_file is not None:
            # Display uploaded image
            image = Image.open(image_file)
            st.image(image, caption="Uploaded Image")
            
            # Proceed button
            if st.button("Proceed with that image"):
                # Store in session state and navigate to chat
                st.session_state.uploaded_image = image
                st.session_state.uploaded_image_file = image_file
                st.session_state.page = PAGE_CHAT
                st.rerun()
        
        MainPage.apply_common_styles()