import streamlit as st
from ui.main_page import MainPage
from ui.chat_page import ChatPage
from config import PAGE_MAIN, PAGE_CHAT
from model.model import Model
import time

def init_session_state():
    if 'page' not in st.session_state:
        st.session_state.page = PAGE_MAIN


def main():
    init_session_state()
    
    if 'model' not in st.session_state:
        st.session_state.model = Model()
        st.session_state.model.load_model()
    
    model = st.session_state.model
    
    if model.is_model_loaded():
        if st.session_state.page == PAGE_MAIN:
            MainPage.render()
        elif st.session_state.page == PAGE_CHAT:
            ChatPage.render(model)
        else:
            st.session_state.page = PAGE_MAIN
            MainPage.render()
    else:
        st.stop()


if __name__ == "__main__":
    main()