
import streamlit as st
import os
from datetime import datetime
from ui.base_page import BasePage
from services import ChatService, ImageService
from config import PAGE_MAIN
from model.model import Model


class ChatPage(BasePage):
    
    @staticmethod
    def render(model: Model):
        st.write("# ChatMoonVLM")
    
        if 'chat_messages' not in st.session_state:
            st.session_state.chat_messages = []
        
        display_image = ChatPage._get_display_image(model)
        
        if display_image:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                ChatPage._render_sidebar(display_image)
            
            with col2:
                ChatPage._render_chat_interface(model)
        
        ChatPage.apply_common_styles()
    
    @staticmethod
    def _get_display_image(model: Model):
        if 'uploaded_image' not in st.session_state:
            return None
        
        if 'encoded_images_cache' not in st.session_state:
            st.session_state.encoded_images_cache = {}
        
        image_path = st.session_state.current_chat_session.get('image_path')
        if image_path and os.path.exists(image_path):
            if image_path in st.session_state.encoded_images_cache:
                model.enc_image = st.session_state.encoded_images_cache[image_path]
            else:
                model.encode_image(image_path)
                if model.enc_image is not None:
                    st.session_state.encoded_images_cache[image_path] = model.enc_image
            
            return ImageService.load_image(image_path)
        else:
            if model.enc_image is None:
                model.encode_image(st.session_state.uploaded_image)
            return st.session_state.uploaded_image
    
    @staticmethod
    def _render_sidebar(display_image):
        st.image(display_image, caption="Uploaded Image")
        
        st.markdown("---")
        
        if st.button("Start New Chat", use_container_width=True):
            ChatPage._handle_back_navigation()
    
        st.markdown("### Recent Chats")
        st.caption("Showing the 10 most recent chats")
        
        history = ChatService.load_history()
        
        if history:
            for i, chat in enumerate(reversed(history[-10:])):
                chat_label = chat.get('chat_name', chat.get('image_name', 'Unnamed Chat')[:20])
        
                if st.button(
                    chat_label, 
                    key=f"chat_{i}", 
                    use_container_width=True
                ):
                    st.session_state.current_chat_session = chat
                    st.session_state.chat_messages = chat['messages']
                    st.rerun()
        else:
            st.info("No previous chats yet")
    
    
    @staticmethod
    def _render_chat_interface(model: Model):
        chat_name = st.session_state.current_chat_session.get('chat_name', 'Chat')
        timestamp = st.session_state.current_chat_session.get('timestamp', '')
        
        col_name, col_time = st.columns([3, 1])
        with col_name:
            st.write(f"### {chat_name}")
        with col_time:
            st.markdown(f"<div style='text-align: right; padding-top: 10px;'>{timestamp}</div>", unsafe_allow_html=True)
        
        for msg in st.session_state.chat_messages:
            with st.chat_message("user"):
                st.write(msg['question'])
            with st.chat_message("assistant"):
                st.write(msg['answer'])
        
        prompt = st.chat_input("Ask question about your image")
        if prompt:
            ChatPage._handle_chat_input(prompt, model)
    
    @staticmethod
    def _handle_chat_input(prompt: str, model: Model):
        with st.chat_message("user"):
            st.write(prompt)
        
        with st.chat_message("assistant"):
            answer_model = model.get_answer(prompt)
            if answer_model is not None:
                answer = answer_model
            else:
                answer = "There is an error. Please be sure the image is uploaded correctly."
            st.write(answer)
        
        message = {
            'question': prompt,
            'answer': answer,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
        
        if not st.session_state.chat_messages or st.session_state.chat_messages[-1]['question'] != prompt:
            st.session_state.chat_messages.append(message)
            
            if 'messages' not in st.session_state.current_chat_session:
                st.session_state.current_chat_session['messages'] = st.session_state.chat_messages
            elif st.session_state.current_chat_session['messages'] is not st.session_state.chat_messages:
                st.session_state.current_chat_session['messages'].append(message)
            
            current_name = st.session_state.current_chat_session.get('chat_name', '')
            if len(st.session_state.chat_messages) == 1 or current_name.startswith('New Chat - '):
                history = ChatService.load_history()
                new_name = ChatService.generate_chat_name(
                    st.session_state.current_chat_session, 
                    history
                )
                st.session_state.current_chat_session['chat_name'] = new_name
            
            history = ChatService.load_history()
            history = ChatService.update_or_append_session(
                history, 
                st.session_state.current_chat_session
            )
            ChatService.save_history(history)
        
        st.rerun()
    
    @staticmethod
    def _handle_back_navigation():
        if 'current_chat_session' in st.session_state:
            del st.session_state.current_chat_session
        if 'chat_messages' in st.session_state:
            del st.session_state.chat_messages
        
        st.session_state.page = PAGE_MAIN
        st.rerun()
