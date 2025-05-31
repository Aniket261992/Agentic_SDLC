from configparser import ConfigParser

class Config:

    def __init__(self,config_file = "src/SDLC/ui/uiconfig.ini"):
        self.config = ConfigParser()
        self.config.read(config_file)

    def get_llm_options(self):
        return self.config["DEFAULT"].get("LLM_OPTIONS").split(", ")
