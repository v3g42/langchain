"""Tool for the Dozer Pulse"""

from typing import Any, Dict, Optional, Type

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.callbacks.manager import AsyncCallbackManagerForToolRun
from langchain_core.language_models.base import BaseLanguageModel
from langchain_core.prompts.prompt import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field, root_validator
from langchain_core.tools import BaseTool

from langchain_community.utilities.dozer import DozerPulseWrapper, EndpointQueryParams

from .prompt import (
    DOZER_GENERATE_QUERY,
    DOZER_GENERATE_QUERY_RESPONSE,
    DOZER_QUERY_PLAN_PROMPT,
    ENDPOINT_EXAMPLE,
    PLAN_OUTPUT_FORMAT,
    RAW_QUERY_EXAMPLE,
)


class DozerRawQueryInput(BaseModel):
    query: str = Field(..., description="should be a valid SQL")


class DozerRawQueryTool(BaseTool):
    """Tool that executes a raw query using Dozer Pulse APIs."""

    name: str = "dozer_raw_query"
    description: str = "Input is a valid SQL query to be executed against the database."
    dozer: DozerPulseWrapper
    args_schema: Type[BaseModel] = DozerRawQueryInput

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the DozerRawQueryTool"""
        return self.dozer.raw_query(query)


class DozerQueryEndpointInput(BaseModel):
    params: EndpointQueryParams = Field(..., description="")


class DozerQueryEndpointTool(BaseTool):
    """Tool that queries a Dozer Endpoint."""

    name: str = "dozer_query_endpoint"
    description: str = (
        "Input to this tool is a map {{'endpoint_name': endpoint_name, 'params': 'parameters'}}"
        "endpoint_name is the available endpoint_name"
        "params are parameters defined on that endpoint"
    )
    dozer: DozerPulseWrapper
    args_schema: Type[BaseModel] = DozerQueryEndpointInput

    def _run(
        self,
        params: EndpointQueryParams,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the DozerQueryEndpointTool."""
        return self.dozer.query_endpoint(params=params)


class DozerSemanticsTool(BaseTool):
    """Tool that fetches semantics of an application."""

    name: str = "dozer_semantics"
    description: str = "Fetch semantics of this application"
    dozer: DozerPulseWrapper

    def _run(
        self,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        return self.dozer.fetch_semantics()


class DozerGenerateQueryInput(BaseModel):
    input: str = Field(
        ..., description="input should be a request from user in plain text."
    )


class DozerGenerateSqlQueryTool(BaseTool):
    """Use an LLM to generate a valid SQL query"""

    name: str = "dozer_generate_query"
    description: str = (
        "Use this tool generate a valid SQL query based on user's request"
    )
    raw_tables_yaml: str
    llm: BaseLanguageModel
    llm_chain: Any = Field(init=False)
    args_schema: Type[BaseModel] = DozerGenerateQueryInput

    @root_validator(pre=True)
    def initialize_llm_chain(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if not values["raw_tables_yaml"]:
            raise "raw_tables_yaml is expected"
        if "llm_chain" not in values:
            from langchain.chains.llm import LLMChain
            values["llm_chain"] = LLMChain(
                llm=values.get("llm"),
                prompt=PromptTemplate(
                    template=DOZER_GENERATE_QUERY,
                    input_variables=["input"],
                    partial_variables={
                        "format_response": DOZER_GENERATE_QUERY_RESPONSE,
                        "raw_tables_yaml": values["raw_tables_yaml"],
                    },
                ),
            )
        return values

    def _run(
        self,
        input: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the LLM to check the query."""
        return self.llm_chain.predict(
            input=input,
            callbacks=run_manager.get_child() if run_manager else None,
        )

    async def _arun(
        self,
        input: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        return await self.llm_chain.apredict(
            input=input,
            callbacks=run_manager.get_child() if run_manager else None,
        )


class DozerQueryPlanTool(BaseTool):
    """Planning a process to get data to answer the question."""

    name: str = "dozer_plan"
    description: str = (
        "A wrapper around Dozer Pulse Semantic APIs."
        "Useful for when you need to query your data"
        "imported into Pulse environment"
        "Input should be a query related to your data."
    )
    template: str = DOZER_QUERY_PLAN_PROMPT
    llm: BaseLanguageModel
    llm_chain: Any = Field(init=False)

    @root_validator(pre=True)
    def initialize_llm_chain(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if "llm_chain" not in values:
            from langchain.chains.llm import LLMChain

            values["llm_chain"] = LLMChain(
                llm=values.get("llm"),
                prompt=PromptTemplate(
                    template=DOZER_QUERY_PLAN_PROMPT,
                    input_variables=["query"],
                    partial_variables={
                        "format_response": PLAN_OUTPUT_FORMAT,
                        "endpoint_example": ENDPOINT_EXAMPLE,
                        "raw_query_example": RAW_QUERY_EXAMPLE,
                    },
                ),
            )

        if values["llm_chain"].prompt.input_variables != ["query"]:
            raise ValueError(
                "LLM chain for DozerQueryTool must have input variables ['query']"
            )

        return values

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the LLM to check the query."""
        return self.llm_chain.predict(
            query=query,
            callbacks=run_manager.get_child() if run_manager else None,
        )

    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        return await self.llm_chain.apredict(
            query=query,
            callbacks=run_manager.get_child() if run_manager else None,
        )
