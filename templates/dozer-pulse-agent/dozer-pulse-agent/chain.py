from langchain_community.utilities import DozerPulseWrapper
from langchain_community.agent_toolkits import DozerPulseToolkit
from langchain_community.agent_toolkits.dozer.base import create_dozer_agent
from langchain_openai import ChatOpenAI
import os

dozer = DozerPulseWrapper(api_key=api_key, application_id=application_id)
llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-0125")
toolkit = DozerPulseToolkit(dozer=dozer, llm=llm)
chain = create_dozer_agent(llm=llm, toolkit=toolkit, verbose=True)

