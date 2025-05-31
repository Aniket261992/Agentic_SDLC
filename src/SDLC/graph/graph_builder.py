from src.SDLC.nodes.sdlc_nodes import SDLC_Nodes
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph,START,END
from src.SDLC.state.stateclasses import State


class GraphBuilder:

    def __init__(self):
        self.sdlc_nodes = SDLC_Nodes()
        self.graph_builder = StateGraph(State)

    def create_sdlc_workflow(self):
        self.graph_builder.add_node("User Story Generator",self.sdlc_nodes.user_story_generator)
        self.graph_builder.add_node("Product Owner",self.sdlc_nodes.product_owner_review)
        self.graph_builder.add_node("Document creator",self.sdlc_nodes.doc_creator)
        self.graph_builder.add_node("Document writer",self.sdlc_nodes.doc_writer)
        self.graph_builder.add_node("Document compiler",self.sdlc_nodes.doc_compiler)
        self.graph_builder.add_node("Document Reviewer",self.sdlc_nodes.doc_reviewer)
        self.graph_builder.add_node("Code Generator",self.sdlc_nodes.code_generator)
        self.graph_builder.add_node("Code Reviewer",self.sdlc_nodes.code_reviewer)
        self.graph_builder.add_node("Security Reviewer",self.sdlc_nodes.code_security_reviewer)
        self.graph_builder.add_node("Test Writer",self.sdlc_nodes.test_case_writer)
        self.graph_builder.add_node("Testcase reviewer",self.sdlc_nodes.test_case_reviewer)

        self.graph_builder.add_edge(START,"User Story Generator")
        self.graph_builder.add_edge("User Story Generator","Product Owner")
        self.graph_builder.add_conditional_edges(
            "Product Owner",
            self.sdlc_nodes.router,
            {
                "Accepted":"Document creator",
                "Feedback":"User Story Generator",
            },
        )
        self.graph_builder.add_conditional_edges(
            "Document creator",
            self.sdlc_nodes.assign_writer,
            ["Document writer"]
        )
        self.graph_builder.add_edge("Document writer","Document compiler")
        self.graph_builder.add_edge("Document compiler","Document Reviewer")
        self.graph_builder.add_conditional_edges(
            "Document Reviewer",
            self.sdlc_nodes.design_router,
            {
                "Accepted":"Code Generator",
                "Feedback":"Document creator",
            },
        )
        self.graph_builder.add_edge("Code Generator","Code Reviewer")
        self.graph_builder.add_conditional_edges(
            "Code Reviewer",
            self.sdlc_nodes.code_router,
            {
                "Accepted":"Security Reviewer",
                "Reiterate":"Code Generator",
            },
        )
        self.graph_builder.add_conditional_edges(
            "Security Reviewer",
            self.sdlc_nodes.code_router,
            {
                "Accepted":"Test Writer",
                "Reiterate":"Code Generator",
            },
        )
        self.graph_builder.add_edge("Test Writer","Testcase reviewer")
        self.graph_builder.add_conditional_edges(
            "Testcase reviewer",
            self.sdlc_nodes.test_case_router,
            {
                "Accepted":END,
                "Reiterate":"Test Writer",
            },
        )

        checkpointer = MemorySaver()
        return self.graph_builder.compile(checkpointer=checkpointer)
