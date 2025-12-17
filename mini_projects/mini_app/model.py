from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableSequence
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from config import TEMPERATURE, MAX_TOKENS, CREDENTIAL, GPT4_MINI_MODEL_ID, GPT5_MINI_MODEL_ID

from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

def initialize_model(model_name: str) -> ChatOpenAI:
    return ChatOpenAI(
        temperature = TEMPERATURE,
        max_tokens=MAX_TOKENS,
        api_key=CREDENTIAL,
        model=model_name
    ) 

gpt4_model = initialize_model(GPT4_MINI_MODEL_ID)
gpt5_model = initialize_model(GPT5_MINI_MODEL_ID)

class city_description(BaseModel):
    city_name: str=Field(description="The name of the city")
    touristic_site_name: str=Field(description="The name of toursitic site to visit")
    free: bool=Field(description="If the entrance is free or not")

output_parser = JsonOutputParser(pydantic_object=city_description)
format_instructions = output_parser.get_format_instructions()

template="""You are a helpful AI bot that assits tourist in Cameroon.

Task: Help them choose the 4 best places to visit in {city} and cities near in Json format.

{format_instructions}
"""

prompt = PromptTemplate(
    template=template,
    input_variables=["city"],  
    partial_variables={"format_instructions": format_instructions},  
)

gpt4_chain = prompt | gpt4_model | output_parser
gpt5_chain = prompt | gpt5_model | output_parser