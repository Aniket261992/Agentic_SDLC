from langgraph.types import Command
from src.SDLC.graph.graph_builder import GraphBuilder

class DisplayResult:

    def __init__(self):
        self.graph_builder = GraphBuilder()
        self.graph = self.graph_builder.create_sdlc_workflow()
        self.config = {"configurable": {"thread_id": "1"}}

    def start_pipeline(self,user_input: str):
        return self.graph.invoke({"user_input_req": user_input}, config=self.config)

    def resume_pipeline(self,payload: dict):
        return self.graph.invoke(Command(resume=payload), config=self.config)