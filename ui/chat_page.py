
import streamlit as st
import os
from datetime import datetime
from ui.base_page import BasePage
from services import ChatService, ImageService
from config import PAGE_MAIN


class ChatPage(BasePage):
    
    @staticmethod
    def render():
        st.write("# ChatMoonVLM")
    
        if 'current_chat_session' not in st.session_state:
            image_name = getattr(
                st.session_state.get('uploaded_image_file'), 
                'name', 
                'unknown.jpg'
            )
            st.session_state.current_chat_session = ChatService.create_session(image_name)
            st.session_state.chat_messages = []
            
            if 'uploaded_image' in st.session_state:
                chat_id = st.session_state.current_chat_session['id']
                ImageService.save_image(st.session_state.uploaded_image, chat_id)
        
        display_image = ChatPage._get_display_image()
        
        if display_image:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                ChatPage._render_sidebar(display_image)
            
            with col2:
                ChatPage._render_chat_interface()
        
        ChatPage.apply_common_styles()
    
    @staticmethod
    def _get_display_image():
        if 'uploaded_image' not in st.session_state:
            return None
        
        image_path = st.session_state.current_chat_session.get('image_path')
        if image_path and os.path.exists(image_path):
            return ImageService.load_image(image_path)
        else:
            return st.session_state.uploaded_image
    
    @staticmethod
    def _render_sidebar(display_image):
        st.image(display_image, caption="Uploaded Image")
        
        st.markdown("---")
        
        if st.button("← Upload Different Image", use_container_width=True):
            ChatPage._handle_back_navigation()
        
        col_title, col_help = st.columns([2, 1])
        with col_title:
            st.markdown("### Previous Chats")
        with col_help:
            st.markdown("", help="Showing the 10 most recent chats")
        
        history = ChatService.load_history()
        
        if history:
            for i, chat in enumerate(reversed(history[-10:])):
                chat_label = f"📷 {chat['image_name'][:20]}..."
                chat_time = chat['timestamp']
                
                if st.button(
                    f"{chat_label}\n{chat_time}", 
                    key=f"chat_{i}", 
                    use_container_width=True
                ):
                    st.session_state.current_chat_session = chat
                    st.session_state.chat_messages = chat['messages']
                    st.rerun()
        else:
            st.info("No previous chats yet")
    
    @staticmethod
    def _render_chat_interface():
        st.write("### Ask questions about your image")
        
        for msg in st.session_state.chat_messages:
            with st.chat_message("user"):
                st.write(msg['question'])
            with st.chat_message("assistant"):
                st.write(msg['answer'])
        
        prompt = st.chat_input("What do you see in this image?")
        if prompt:
            ChatPage._handle_chat_input(prompt)
    
    @staticmethod
    def _handle_chat_input(prompt: str):
        answer = f"Model integration coming soon! Your question: {prompt}"
        
        message = {
            'question': prompt,
            'answer': answer,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
        
        st.session_state.chat_messages.append(message)
        
        ChatService.add_message(
            st.session_state.current_chat_session, 
            prompt, 
            answer
        )
        
        history = ChatService.load_history()
        history = ChatService.update_or_append_session(
            history, 
            st.session_state.current_chat_session
        )
        ChatService.save_history(history)
        
        st.rerun()
    
    @staticmethod
    def _handle_back_navigation():
        if st.session_state.current_chat_session['messages']:
            history = ChatService.load_history()
            history.append(st.session_state.current_chat_session)
            ChatService.save_history(history)
        
        if 'current_chat_session' in st.session_state:
            del st.session_state.current_chat_session
        if 'chat_messages' in st.session_state:
            del st.session_state.chat_messages
        
        st.session_state.page = PAGE_MAIN
        st.rerun()