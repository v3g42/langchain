"""Toolkit for interacting with Dozer Pulse APIs."""
from typing import Dict, List, Optional

import yaml
from langchain_core.language_models import BaseLanguageModel
from langchain_core.pydantic_v1 import Field, root_validator

from langchain_community.agent_toolkits.base import BaseToolkit
from langchain_community.tools import BaseTool
from langchain_community.tools.dozer.tool import (
    DozerGenerateSqlQueryTool,
    DozerQueryEndpointTool,
    DozerRawQueryTool,
    DozerSemanticsTool,
)
from langchain_community.utilities.dozer import DozerPulseWrapper, Semantics


class DozerPulseToolkit(BaseToolkit):
    """Toolkit for querying Dozer Pulse Applications."""

    dozer: DozerPulseWrapper = Field(exclude=True)
    llm: BaseLanguageModel = Field(exclude=True)
    semantics: Optional[Semantics] = Field(exclude=True)

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        """Initialize semantics"""

        if not values["semantics"]:
            dozer: DozerPulseWrapper = values["dozer"]
            values["semantics"] = dozer.fetch_semantics()

        return values

    def get_tools(self) -> List[BaseTool]:
        """Get the tools in the toolkit."""
        raw_table_cubes = self.semantics.filter_tables().cubes;
        raw_tables_str = '';
        for cube in raw_table_cubes:
            table_description = cube['description'] if 'description' in cube else ''
            raw_tables_str += format(f"Name: {cube['sql_table']}\n");
            raw_tables_str += format(f"Description: {table_description}\n");
            raw_tables_str += format(f"Columns: \n");
            # get keys of dictionary
            dimensions = cube['dimensions'];
            keys = dimensions.keys();
            for key in keys:
                description = dimensions[key]['description'] if 'description' in dimensions[key] else ''
                raw_tables_str += format(f"    {key} {dimensions[key]['sql_type']}    {description} \n");
            raw_tables_str += format(f"==============================\n");

        
        generate_tool = DozerGenerateSqlQueryTool(
            dozer=self.dozer, llm=self.llm, raw_tables_yaml=raw_tables_str
        )
        query_endpoint_tool = DozerQueryEndpointTool(dozer=self.dozer)
        raw_query_tool = DozerRawQueryTool(dozer=self.dozer)

        return [generate_tool, query_endpoint_tool, raw_query_tool]

    def fetch_endpoints(self) -> str:
        """Return semantics for endpoints."""
        semantics = self.semantics.filter_endpoints()
        return yaml.dump(semantics)

    def fetch_tables(self) -> str:
        """Return semantics for raw_tables."""
        semantics = self.semantics.filter_tables()
        # format  table name, description, properties
        
        return yaml.dump(semantics.cubes)
