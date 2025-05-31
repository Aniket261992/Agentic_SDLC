from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from src.SDLC.state.stateclasses import User_Stories,Sections


class LLMconfig:
    def __init__(self):
        self.llm_registry = {}

    def get_llm(self,model:str):
        if "gpt" in model or "o1" in model:
            return ChatOpenAI(model=model)
        elif "llama" in model or "gemma" in model:
            return ChatGroq(model=model)
        raise ValueError(f"Unsupported model: {model}")
    
    def configure_llms(self,model_config):

        self.llm_registry['story_generator'] = self.get_llm(model_config['user_story_model']).with_structured_output(User_Stories)
        self.llm_registry['document_creator'] = self.get_llm(model_config['doc_creator_model']).with_structured_output(Sections)
        self.llm_registry['document_writer'] = self.get_llm(model_config['doc_creator_model'])
        self.llm_registry['code_generator'] = self.get_llm(model_config['code_gen_model'])
        self.llm_registry['test_writer'] = self.get_llm(model_config['test_writer_model']) 

    def get_llm_registry(self):
        return self.llm_registry

