from transformers import AutoModelForCausalLM
from PIL import Image
import streamlit as st
import json
import os
from datetime import datetime
from datetime import datetime

# Chat history management
CHAT_HISTORY_FILE = "data/chat_history.json"
MAX_CHAT_HISTORY = 10

def load_chat_history():
    """Load chat history from JSON file"""
    if os.path.exists(CHAT_HISTORY_FILE):
        try:
            with open(CHAT_HISTORY_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_chat_history(history):
    """Save chat history to JSON file, keeping only the 10 most recent"""
    # Get list of chat IDs before pruning
    old_chat_ids = {chat['id'] for chat in history}
    
    # Keep only the most recent MAX_CHAT_HISTORY chats
    history = history[-MAX_CHAT_HISTORY:]
    new_chat_ids = {chat['id'] for chat in history}
    
    # Delete images for removed chats
    removed_chat_ids = old_chat_ids - new_chat_ids
    for chat_id in removed_chat_ids:
        # Try different extensions
        for ext in ['.png', '.jpg', '.jpeg']:
            img_path = f"data/images/{chat_id}{ext}"
            if os.path.exists(img_path):
                os.remove(img_path)
    
    os.makedirs(os.path.dirname(CHAT_HISTORY_FILE), exist_ok=True)
    with open(CHAT_HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def save_chat_image(image, chat_id):
    """Save PIL Image to disk"""
    os.makedirs("data/images", exist_ok=True)
    image_path = f"data/images/{chat_id}.png"
    image.save(image_path)
    return image_path

def load_chat_image(image_path):
    """Load image from disk"""
    if os.path.exists(image_path):
        return Image.open(image_path)
    return None

def create_new_chat_session(image_name):
    """Create a new chat session"""
    chat_id = datetime.now().isoformat()
    return {
        'id': chat_id,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'image_name': image_name,
        'image_path': f"data/images/{chat_id}.png",
        'messages': []
    }

def add_message_to_session(session, question, answer):
    """Add a Q&A pair to a chat session"""
    session['messages'].append({
        'question': question,
        'answer': answer,
        'timestamp': datetime.now().strftime('%H:%M:%S')
    })

def get_upload_page():
    """Display the image upload page"""
    st.write("# ChatMoonVLM")
    image_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    if(image_file is not None):
        image = Image.open(image_file)
        st.image(image, caption="Uploaded Image")
        if st.button("Proceed with that image"):
            # Store image and file info in session state and navigate to chat page
            st.session_state.uploaded_image = image
            st.session_state.uploaded_image_file = image_file
            st.session_state.page = "chat"
            st.rerun()
    
    # Apply custom styling
    st.markdown(
        """
        <style>
        /* Hide Streamlit header */
        header {visibility: hidden;}

        /* Hide the footer */
        footer {visibility: hidden;}

        /* Remove top padding */
        .block-container {
            padding-top: 1rem;
        }
        .stApp {
            background-color: #0e1117;
        }
        /* Footer styling */
        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            color: #fafafa;
            text-align: center;
            padding: 10px 0;
            border-top: 1px solid #2e3140;
        }
        </style>
        <div class="footer">
            <p>By Okan Berhoğlu</p>
        </div>
        """,
        unsafe_allow_html=True
    )

def get_chat_page():
    """Display the chat/interaction page"""
    st.write("# ChatMoonVLM - Chat")
    
    # Initialize current chat session if not exists
    if 'current_chat_session' not in st.session_state:
        image_name = getattr(st.session_state.get('uploaded_image_file'), 'name', 'unknown.jpg')
        st.session_state.current_chat_session = create_new_chat_session(image_name)
        st.session_state.chat_messages = []
        
        # Save the uploaded image to disk
        if 'uploaded_image' in st.session_state:
            chat_id = st.session_state.current_chat_session['id']
            save_chat_image(st.session_state.uploaded_image, chat_id)
    
    # Display the uploaded image and chat interface
    # Determine which image to display (from disk for loaded chats, from session for new)
    display_image = None
    if 'uploaded_image' in st.session_state:
        # Check if we're viewing a loaded chat from history 
        image_path = st.session_state.current_chat_session.get('image_path')
        if image_path and os.path.exists(image_path):
            display_image = load_chat_image(image_path)
        else:
            display_image = st.session_state.uploaded_image
    
    if display_image:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(display_image, caption="Uploaded Image")
            
            # Display chat history below the image
            st.markdown("---")
            if st.button("← Upload Different Image", use_container_width=True):
                # Save current chat before leaving
                if st.session_state.current_chat_session['messages']:
                    history = load_chat_history()
                    history.append(st.session_state.current_chat_session)
                    save_chat_history(history)
                
                # Clear session and go back
                if 'current_chat_session' in st.session_state:
                    del st.session_state.current_chat_session
                if 'chat_messages' in st.session_state:
                    del st.session_state.chat_messages
                st.session_state.page = "upload"
                st.rerun()
            
            # Display previous chats
            st.markdown("### Previous Chats")
            history = load_chat_history()
            if history:
                for i, chat in enumerate(reversed(history[-10:])):  # Show last 10
                    chat_label = f"📷 {chat['image_name'][:20]}..."
                    chat_time = chat['timestamp']
                    if st.button(f"{chat_label}\n{chat_time}", key=f"chat_{i}", use_container_width=True):
                        # Load this chat
                        st.session_state.current_chat_session = chat
                        st.session_state.chat_messages = chat['messages']
                        st.rerun()
            else:
                st.info("No previous chats yet")
        
        with col2:
            st.write("### Ask questions about your image")
            
            # Display chat messages
            for msg in st.session_state.chat_messages:
                with st.chat_message("user"):
                    st.write(msg['question'])
                with st.chat_message("assistant"):
                    st.write(msg['answer'])
            
            # Chat input
            prompt = st.chat_input("What do you see in this image?")
            if prompt:
                # Placeholder answer (will be replaced with model inference)
                answer = f"Model integration coming soon! Your question: {prompt}"
                
                # Add to session state
                st.session_state.chat_messages.append({
                    'question': prompt,
                    'answer': answer,
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                })
                
                # Update current chat session
                add_message_to_session(st.session_state.current_chat_session, prompt, answer)
                
                # Save to disk
                history = load_chat_history()
                # Check if this chat already exists in history
                existing_index = None
                for i, chat in enumerate(history):
                    if chat['id'] == st.session_state.current_chat_session['id']:
                        existing_index = i
                        break
                
                if existing_index is not None:
                    history[existing_index] = st.session_state.current_chat_session
                else:
                    history.append(st.session_state.current_chat_session)
                
                save_chat_history(history)
                st.rerun()
    
    
    # Apply custom styling
    st.markdown(
        """
        <style>
        /* Hide Streamlit header */
        header {visibility: hidden;}

        /* Hide the footer */
        footer {visibility: hidden;}

        /* Remove top padding */
        .block-container {
            padding-top: 1rem;
        }
        .stApp {
            background-color: #0e1117;
        }
        /* Footer styling */
        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            color: #fafafa;
            text-align: center;
            padding: 10px 0;
            border-top: 1px solid #2e3140;
        }
        </style>
        <div class="footer">
            <p>By Okan Berhoğlu</p>
        </div>
        """,
        unsafe_allow_html=True
    )

def main():
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = "upload"
    
    # Display the appropriate page based on session state
    if st.session_state.page == "upload":
        get_upload_page()
    elif st.session_state.page == "chat":
        get_chat_page()
    
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--image_path", type=str, required=True, help="Path to the image file")
    # args = parser.parse_args()
    # model_name = "vikhyatk/moondream2"
    # try:
    #     model = AutoModelForCausalLM.from_pretrained(
    #         model_name, 
    #         revision="2025-06-21",
    #         trust_remote_code=True, 
    #         device_map="cpu"
    #     )

    # except OSError as e:
    #     print(f"Error loading model: {e}")
    #     return

    # image = Image.open(args.image_path)
    # enc_image = model.encode_image(image)

    # print("Ask questions about your image.")
    # while True:
    #     try:
    #         question = input("Question: ")
    #         answer = model.query(enc_image, question)['answer']
    #         print(f"Answer: {answer}\n")
            
    #     except KeyboardInterrupt:
    #         print("\nExiting.")
    #         break

    #     except Exception as e:
    #         print(f"Error: {e}")
    #         break

if __name__ == "__main__":
    main()