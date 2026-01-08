from config import MODEL_ID, MODEL_REVISION
from transformers import AutoModelForCausalLM
from PIL import Image
import streamlit as st

class Model:
    def __init__(self):
        self.model = None
        self.enc_image = None
    
    def load_model(self):
        try:
            model = AutoModelForCausalLM.from_pretrained(
                MODEL_ID, 
                revision=MODEL_REVISION,
                trust_remote_code=True, 
                device_map="cpu"
            )
            self.model = model
        except:
            self.model = None
    
    def encode_image(self,image_path: str):
        try:
            with st.spinner("Encoding image..."):
                if(self.model is not None):
                    image = Image.open(image_path)
                    enc_image = self.model.encode_image(image)
                    self.enc_image = enc_image
                else:
                    raise Exception()
        except:
            self.enc_image = None
    
    def get_answer(self, question: str):
        try:
            with st.spinner("Thinking..."):
                if(self.model is not None and self.enc_image is not None):
                    answer = self.model.query(self.enc_image, question)['answer']
                    return answer
                else:
                    raise Exception()
        except:
            return None