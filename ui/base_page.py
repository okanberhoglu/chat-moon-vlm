import streamlit as st


class BasePage:
    
    @staticmethod
    def apply_common_styles():
        st.markdown(
            """
            <style>
            /* Hide Streamlit header */
            header {visibility: hidden;}

            /* Hide the default footer */
            footer {visibility: hidden;}

            /* Remove top padding */
            .block-container {
                padding-top: 1rem;
            }
            
            /* Dark background */
            .stApp {
                background-color: #0e1117;
            }
            
            /* Custom footer styling */
            .footer {
                position: fixed;
                left: 0;
                bottom: 0;
                width: 100%;
                color: #fafafa;
                text-align: center;
                padding: 10px 0;
                border-top: 1px solid #2e3140;
                background-color: #0e1117;
            }
            </style>
            <div class="footer">
                <p>By Okan Berhoğlu</p>
            </div>
            """,
            unsafe_allow_html=True
        )
