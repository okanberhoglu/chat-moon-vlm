import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from config import CHAT_HISTORY_FILE, MAX_CHAT_HISTORY, IMAGE_STORAGE_DIR


class ChatService:
    @staticmethod
    def load_history() -> List[Dict]:
        if os.path.exists(CHAT_HISTORY_FILE):
            try:
                with open(CHAT_HISTORY_FILE, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []
    
    @staticmethod
    def save_history(history: List[Dict]) -> None:
        old_chat_ids = {chat['id'] for chat in history}
        
        history = history[-MAX_CHAT_HISTORY:]
        new_chat_ids = {chat['id'] for chat in history}
        
        removed_chat_ids = old_chat_ids - new_chat_ids
        for chat_id in removed_chat_ids:
            for ext in ['.png', '.jpg', '.jpeg']:
                img_path = os.path.join(IMAGE_STORAGE_DIR, f"{chat_id}{ext}")
                if os.path.exists(img_path):
                    try:
                        os.remove(img_path)
                    except OSError:
                        pass
        
        os.makedirs(os.path.dirname(CHAT_HISTORY_FILE), exist_ok=True)
        with open(CHAT_HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
    
    @staticmethod
    def create_session(image_name: str) -> Dict:
        chat_id = datetime.now().isoformat()
        return {
            'id': chat_id,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'image_name': image_name,
            'image_path': os.path.join(IMAGE_STORAGE_DIR, f"{chat_id}.png"),
            'messages': []
        }
    
    @staticmethod
    def add_message(session: Dict, question: str, answer: str) -> None:
        session['messages'].append({
            'question': question,
            'answer': answer,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
    
    @staticmethod
    def find_session_index(history: List[Dict], session_id: str) -> Optional[int]:
        for i, chat in enumerate(history):
            if chat['id'] == session_id:
                return i
        return None
    
    @staticmethod
    def update_or_append_session(history: List[Dict], session: Dict) -> List[Dict]:
        existing_index = ChatService.find_session_index(history, session['id'])
        
        if existing_index is not None:
            history[existing_index] = session
        else:
            history.append(session)
        
        return history
    
    @staticmethod
    def generate_chat_name(session: Dict, history: List[Dict]) -> str:
        image_name = session.get('image_name', '')
        
        if image_name:
            base_name = os.path.splitext(image_name)[0]
        else:
            return ChatService.get_next_new_chat_number(history)
        
        if len(base_name) > 40:
            base_name = base_name[:37] + "..."
        
        return ChatService.generate_unique_name(base_name, history, session['id'])
    
    @staticmethod
    def generate_unique_name(base_name: str, history: List[Dict], current_session_id: str) -> str:
        
        existing_names = {
            chat['chat_name'] 
            for chat in history 
            if chat['id'] != current_session_id and 'chat_name' in chat
        }

        if base_name not in existing_names:
            return base_name
        
        counter = 1
        while f"{base_name} {counter}" in existing_names:
            counter += 1
        
        return f"{base_name} {counter}"
    
    @staticmethod
    def get_next_new_chat_number(history: List[Dict]) -> str:

        new_chat_numbers = []
        for chat in history:
            chat_name = chat.get('chat_name', '')
            if chat_name.startswith('New Chat - '):
                try:
                    num = int(chat_name.replace('New Chat - ', ''))
                    new_chat_numbers.append(num)
                except ValueError:
                    pass
        
        if not new_chat_numbers:
            return "New Chat - 1"
        
        next_num = max(new_chat_numbers) + 1
        return f"New Chat - {next_num}"
