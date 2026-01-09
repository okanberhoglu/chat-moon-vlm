
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
            col1, col2 = st.columns([1, 3])
            
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
        st.image(display_image, caption="Your Image")
        
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
    
        if 'editing_chat_name' not in st.session_state:
            st.session_state.editing_chat_name = False
        
        col_name, col_time = st.columns([3, 1])
        with col_name:
            if st.session_state.editing_chat_name:
                col_input, col_save, col_cancel = st.columns([6, 1, 10])
                with col_input:
                    new_name = st.text_input(
                        "Chat Name", 
                        value=chat_name, 
                        label_visibility="collapsed",
                        key="chat_name_input"
                    )
                with col_save:
                    if st.button("✓", key="save_name", help="Save"):
                        if new_name.strip():
                            st.session_state.current_chat_session['chat_name'] = new_name.strip()
                            history = ChatService.load_history()
                            history = ChatService.update_or_append_session(
                                history, 
                                st.session_state.current_chat_session
                            )
                            ChatService.save_history(history)
                            st.session_state.editing_chat_name = False
                            st.rerun()
                with col_cancel:
                    if st.button("✗", key="cancel_name", help="Cancel"):
                        st.session_state.editing_chat_name = False
                        st.rerun()
            else:
                col_edit, col_title = st.columns([0.075, 1])
                with col_edit:
                    if st.button("✏️", key="edit_name", help="Edit chat name"):
                        st.session_state.editing_chat_name = True
                        st.rerun()
                with col_title:
                    st.write(f"### {chat_name}")
                
        with col_time:
            st.markdown(f"<div style='text-align: right; padding-top: 10px;'>{timestamp}</div>", unsafe_allow_html=True)
        
        if(len(st.session_state.chat_messages) > 0):
            chat_height = 700
        else:
            chat_height = 1
        
        with st.container(height=chat_height):
            ChatPage._render_msgs()

        with st.container():
            ChatPage._render_chat_input(model)
        
    @staticmethod
    def _render_msgs():
        for msg in st.session_state.chat_messages:
            with st.chat_message("user"):
                st.write(msg['question'])
            with st.chat_message("assistant"):
                st.write(msg['answer'])
    
    @staticmethod
    def _render_chat_input(model: Model):
        prompt = st.chat_input("Ask question about your image")
        if prompt:
            ChatPage._handle_chat_input(prompt, model)

    @staticmethod
    def _handle_chat_input(prompt: str, model: Model):
        answer_model = model.get_answer(prompt)
        if answer_model is not None:
            answer = answer_model
        else:
            answer = "There is an error. Please be sure the image is uploaded correctly."
       
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
        
