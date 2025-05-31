import operator
from typing_extensions import Literal,TypedDict
from pydantic import BaseModel, Field
from typing import Annotated

class User_Stories(BaseModel):
    stories:list[str] = Field(
        description="List of user stories generated based on user requirements and feedback (if provided)"
    )

class Section(BaseModel):
    name: str = Field(
        description = "Name of the section of the design document" 
    )
    details: str = Field(
        description = "A brief description about the section"
    )
    comments: str = Field(
        description = "Comments on how to improve the section based on feedback provided"
    )

class Sections(BaseModel):
    sections: list[Section] = Field(
        description="List of sections that need to be written for the techincal and functional design document"
    )


class State(TypedDict):
    user_input_req: str
    user_stories:User_Stories
    approval: Literal["Approved","Denied"] = Field(description= "Decide if the user story can be approved or denied based on business needs")
    feedback: str = Field(description= "Give the feedback on the story based on alignment towards business goals")
    sections: list[Section]
    completed_section: Annotated[list,operator.add]
    final_doc: str
    design_approval: Literal["Approved","Denied"] = Field(description= "Decide if the design can be approved or denied based on business requirements")
    design_feedback: str = Field(description= "Give the feedback on the design document based on alignment towards business requirements")
    review_count: Annotated[int,operator.add]
    source_code: str
    code_approval : str
    code_review_comments: str
    testcases: str
    testcase_approval: str
    testcase_comments: str

class DocCreatorState(TypedDict):
    user_stories:User_Stories
    sections: list[Section]
    completed_section: Annotated[list,operator.add]
    design_feedback: str = Field(description= "The feedback on the design document based on alignment towards business requirements")
    final_doc: str

class DocWrtierState(TypedDict):
    section: Section
    completed_section: Annotated[list,operator.add]
    design_feedback: str = Field(description= "The feedback on the design document based on alignment towards business requirements")

class DocReviewerState(TypedDict):
    user_input_req: str
    user_stories:User_Stories
    final_doc: str
    design_approval: Literal["Approved","Denied"] = Field(description= "Decide if the design can be approved or denied based on business requirements")
    design_feedback: str = Field(description= "Give the feedback on the design document based on alignment towards business requirements")
    review_count: Annotated[int,operator.add]

class CodeGenerator(TypedDict):
    source_code: str
    final_doc: str
    code_review_comments: str