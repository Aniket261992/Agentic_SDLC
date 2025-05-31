from src.SDLC.LLM.configllm import LLMconfig
from langchain_core.messages import HumanMessage,SystemMessage,AIMessage
from src.SDLC.state.stateclasses import State,DocCreatorState,DocWrtierState,DocReviewerState,CodeGenerator
from langgraph.types import interrupt
from langgraph.constants import Send


class SDLC_Nodes:

    def __init__(self):
        self.llm_config = LLMconfig()
        self.llm_registry = self.llm_config.get_llm_registry()

    def user_story_generator(self,state:State):
        """Generate the user stories based on the given input user requirements or improve the user stories based on the feedback comments"""

        if state.get("feedback"):
            output = self.llm_registry['story_generator'].invoke(
                [
                    SystemMessage(content="You are a user stories generator in a software design cycle, you generate a list of user stories based on user requirements and also improve them based on the feedback provided"),
                    HumanMessage(f"Generate the user stories for the given user requirements: {state['user_input_req']}"),
                    AIMessage(f"{state['user_stories']}"),
                    HumanMessage(f"Please regenerate the stories again with the given feedback: {state['feedback']}")
                ]
            )
        else:

            output = self.llm_registry['story_generator'].invoke(
                [
                    SystemMessage(content="You are a user stories generator in a software design cycle, you generate a list of user stories based on user requirements and also improve them based on the feedback provided"),
                    HumanMessage(f"Generate the user stories for the given user requirements: {state['user_input_req']}")
                ]
            )

        return {"user_stories":output.stories}

    def product_owner_review(self,state:State):
        """Review the generated user stories and provide approval, if not approved provide feedback comments on the user stories and how it can be improved"""

        story_review = interrupt({
            "question": "Do you approve the following output?"
        })

        return{"approval":story_review['approval'],"feedback":story_review['feedback']}

    def router(self,state:State):
        """Route the flow back to the generator based on the approval"""
        
        if state['approval'] == "Approved":
            return "Accepted"
        else:
            return "Feedback"
        
    def doc_creator(self,state:DocCreatorState):
        """Decides what sections need to be included in the design document based on the user stories and feedback provided"""

        system_prompt = """You are an expert in technical documentation. Based on the user stories, generate a list of sections for a design document. Each section will be given to a writer who will look at the name and details of the section to write about it.

    Each section must have:
    - name (string): the section name
    - details (string): what it should cover
    - comments (string): how it should be improved based on feedback

    Return your response strictly as a JSON matching this structure:
    {
    "sections": [
        {
        "name": "string",
        "details": "string",
        "comments": "string"
        }
    ]
    }
    Do not include any explanation or text outside the JSON.

    Limit to 6 sections max.
    """

        if state.get("design_feedback"):
            state["completed_section"] = []
            state['final_doc']=""
            output = self.llm_registry['document_creator'].invoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Here are the user stories: {state['user_stories']}, provide the list of sections for the design document having detailed design specifications, outlining system architecture, data models, APIs, UI flows, etc."),
                AIMessage(f"{state['sections']}"),
                HumanMessage(f"Rewrite the sections with the given feedback and populate the comments based on the feedback for the section writer to rewrite the section, feedback: {state['design_feedback']}")
            ]
        )
        else:
            output = self.llm_registry['document_creator'].invoke(
                [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=f"Here are the user stories: {state['user_stories']}, provide the list of sections for the design document having detailed design specifications, outlining system architecture, data models, APIs, UI flows, etc.")
                ]
            )

        return {"sections":output.sections}

    def doc_writer(self,state:DocWrtierState):
        """Writes the section of the design document based on the description provided"""

        if state.get("design_feedback"):
            output = self.llm_registry['document_writer'].invoke(
                [
                    SystemMessage(content="Based on the provided section description and section comments of the design document which contains the design feedback, generate the body of the section, use markdown formatting"),
                    HumanMessage(content=f"Here is the name of the section: {state['section'].name}, generate the body of the section based on the description {state['section'].details} keeping in mind the comments: {state['section'].comments}")
                ]
            )
        else:
            output = self.llm_registry['document_writer'].invoke(
                [
                    SystemMessage(content="Based on the provided section description of the design document which contains the technical and functional details, generate the body of the section, use markdown formatting"),
                    HumanMessage(content=f"Here is the name of the section: {state['section'].name}, generate the body of the section based on the description {state['section'].details}")
                ]
            )

        return {"completed_section":[output.content]}

    def doc_compiler(self,state:State):
        """Compile all the sections generated by the document writer"""

        completed_sections = state['completed_section']

        final_doc = "\n\n---\n\n".join(completed_sections)

        return {"final_doc":final_doc}

    def assign_writer(self,state:State):
        """Assigns a writer to write the section of the document"""

        return[Send("Document writer",{"section":s}) for s in state['sections']]

    def doc_reviewer(self,state:DocReviewerState):
        """Review the final design document and approve or deny it, if denied provide feedback"""

        design_review = interrupt({
            "question": "Do you approve the following output?"
        })
        
        return{"design_approval":design_review['design_approval'],"design_feedback":design_review['design_feedback']}



    def design_router(self,state:State):
        """Route the flow back to the document creator based on the approval"""
        
        if state['design_approval'] == "Approved":
            return "Accepted"
        else:
            return "Feedback"
        
    def code_generator(self,state:CodeGenerator):
        """Given the design document, write the source code"""

        if state.get("code_review_comments"):
            output = self.llm_registry['code_generator'].invoke(
                [
                    SystemMessage(content=f"You are a senior python code developer who is expert at coding, given the design document you write the source code in python, provide an executable output for a .py file, donot provide any non executable text in the output"),
                    HumanMessage(content=f"Here is the design document: {state['final_doc']}"),
                    AIMessage(f"{state['source_code']}"),
                    HumanMessage(f"Update the code based on the feedback provided: {state['code_review_comments']}")
                ]
            )
        else:
            output = self.llm_registry['code_generator'].invoke(
                    [
                        SystemMessage(content=f"You are a senior python code developer who is expert at coding, given the design document you write the source code in python, provide an executable output for a .py file, donot provide any non executable text in the output"),
                        HumanMessage(content=f"Here is the design document: {state['final_doc']}")
                    ]
                )
            
        return {"source_code":output.content}

    def code_reviewer(self,state:State):
        """Review the generated code and provide approval, if not approved provide review comments for the junior developer"""

        code_review = interrupt({
            "question": "Do you approve the following output?"
        })

        return{"code_approval":code_review['code_approval'],"code_review_comments":code_review['review_comments']}

    def code_security_reviewer(self,state:State):
        """Review the generated code from software security point of view and provide approval, if not approved provide review comments for the junior developer"""

        code_review = interrupt({
            "question": "Do you approve the following output?"
        })
        
        return{"code_approval":code_review['code_approval'],"code_review_comments":code_review['review_comments']}

    def code_router(self,state:State):
        """Route the flow back to the generator based on the approval"""
        
        if state['code_approval'] == "Approved":
            return "Accepted"
        else:
            return "Reiterate"
        
    def test_case_writer(self,state:State):
        """Write testcases for the source code"""

        test_case = self.llm_registry['test_writer'].invoke(
            [
                SystemMessage(content="""You are a senior QA engineer. Given a Python source, write unit tests for it using pytest. Ensure edge cases are tested. Donot provide non executable output
                            The output should be like below:
                            #Explanation of the test cases (should be in comments format in a python file)
                            
                            <Actual executable code> 
                            
                            #Explanation on what to keep in mind (should be in comments format in a python file)"""),
                HumanMessage(content=f"""Here is the source code: {state['source_code']}, Write 3 to 5 test cases as executable pytest functions""")
            ]
        )

        with open("test_generated.py", "w") as f:
            f.write(test_case.content)
        
        return {"testcases":test_case.content}

    def test_case_reviewer(self,state:State):
        """Review the generated test cases"""

        test_review = interrupt({
            "question": "Do you approve the following output?"
        })
        
        return{"testcase_approval":test_review['testcase_approval'],"testcase_comments":test_review['testcase_comments']}

    def test_case_router(self,state:State):
        """Route the flow back to the testcase writer based on the approval"""
        
        if state['code_approval'] == "Approved":
            return "Accepted"
        else:
            return "Reiterate"
        

