import streamlit as st
import os
from PIL import Image
from ui.base_page import BasePage
from services import ChatService, ImageService
from config import SUPPORTED_IMAGE_TYPES, PAGE_CHAT


class MainPage(BasePage):
    
    @staticmethod
    def render():
        st.write("# ChatMoonVLM")
        st.markdown("### Your AI-powered image chat assistant")
        
        col_history, col_upload = st.columns([1, 3])
        
        with col_upload:
            st.markdown("### Start New Chat")
            st.markdown("Upload an image to begin a conversation")
            
            image_file = st.file_uploader(
                "Choose an image", 
                type=SUPPORTED_IMAGE_TYPES,
                label_visibility="collapsed"
            )
            
            if image_file is not None:
                image = Image.open(image_file)
                st.image(image, caption="Selected Image")
                
                if st.button("Start New Chat", use_container_width=True):
                    history = ChatService.load_history()
                    
                    image_name = image_file.name
                    new_chat_session = ChatService.create_session(image_name)
                    
                    chat_name = ChatService.generate_chat_name(new_chat_session, history)
                    new_chat_session['chat_name'] = chat_name
                    
                    chat_id = new_chat_session['id']
                    ImageService.save_image(image, chat_id)
                    
                    history.append(new_chat_session)
                    ChatService.save_history(history)
                    
                    st.session_state.uploaded_image = image
                    st.session_state.uploaded_image_file = image_file
                    st.session_state.current_chat_session = new_chat_session
                    st.session_state.chat_messages = []
                    st.session_state.page = PAGE_CHAT
                    st.rerun()
        
        with col_history:
            st.markdown("### Recent Chats")
            st.caption("Showing the 10 most recent chats")
            
            history = ChatService.load_history()
            
            if history:
                for i, chat in enumerate(reversed(history[-10:])):
                    chat_label = chat.get('chat_name', chat.get('image_name', 'Unnamed Chat')[:25])
                    
                    with st.container():
                        if st.button(
                            chat_label,
                            key=f"chat_history_{i}", 
                            use_container_width=True
                        ):
                            st.session_state.current_chat_session = chat
                            st.session_state.chat_messages = chat['messages']
                            
                            if 'image_path' in chat and os.path.exists(chat['image_path']):
                                loaded_image = ImageService.load_image(chat['image_path'])
                                if loaded_image:
                                    st.session_state.uploaded_image = loaded_image
                            
                            st.session_state.page = PAGE_CHAT
                            st.rerun()
            else:
                st.info("No previous chats yet. Start a new chat by uploading an image!")
        
        MainPage.apply_common_styles()