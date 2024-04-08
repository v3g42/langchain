from langchain_community.utilities import DozerPulseWrapper
from langchain_community.agent_toolkits import DozerPulseToolkit
from langchain_community.agent_toolkits.dozer.base import create_dozer_agent
from langchain_openai import ChatOpenAI

dozer = DozerPulseWrapper(application_id=1)
llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-0125")
toolkit = DozerPulseToolkit(dozer=dozer, llm=llm)
chain = create_dozer_agent(llm=llm, toolkit=toolkit, verbose=True)

