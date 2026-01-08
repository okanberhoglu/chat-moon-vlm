from config import MODEL_ID, MODEL_REVISION

class ModelService:
    def __init__(self):
        self.model = None
        self.enc_image = None
    
    @staticmethod
    def load_model():
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
    
    @staticmethod
    def encode_image(image_path: str):
        try:
            if(self.model is not None):
                image = Image.open(image_path)
                enc_image = self.model.encode_image(image)
                self.enc_image = enc_image
            else:
                raise Exception()
        except:
            self.enc_image = None
    
    @staticmethod
    def get_answer(question: str):
        try:
            if(self.model is not None and self.enc_image is not None):
                answer = self.model.query(self.enc_image, question)['answer']
                return answer
            else:
                raise Exception()
        except:
            return None
    
    