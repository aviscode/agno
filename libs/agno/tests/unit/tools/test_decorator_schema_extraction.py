"""Test @tool decorator schema extraction fix."""

from typing import List
import pytest
from pydantic import BaseModel, Field
from agno.tools import tool


class SimpleModel(BaseModel):
    """Simple Pydantic model for testing."""
    
    name: str = Field(description="The name field")
    value: int = Field(description="The value field")


class NestedModel(BaseModel):
    """Nested Pydantic model for testing."""
    
    simple: SimpleModel = Field(description="A simple model")
    items: List[str] = Field(description="List of items")


class TestToolDecoratorSchemaExtraction:
    """Test that @tool() decorator immediately extracts parameter schemas."""

    def test_simple_pydantic_model_schema_extracted(self):
        """Test that simple Pydantic model schemas are extracted immediately."""
        
        @tool()
        def process_simple(data: SimpleModel) -> str:
            return f"Processing {data.name}"
        
        # Schema should be extracted immediately, not empty
        assert process_simple.parameters["type"] == "object"
        assert "properties" in process_simple.parameters
        assert len(process_simple.parameters["properties"]) > 0
        
        # Should have the 'data' parameter
        assert "data" in process_simple.parameters["properties"]
        
        # The 'data' parameter should contain the Pydantic model schema
        data_schema = process_simple.parameters["properties"]["data"]
        assert "properties" in data_schema
        assert "name" in data_schema["properties"]
        assert "value" in data_schema["properties"]
        
        # Check field descriptions are preserved
        assert data_schema["properties"]["name"]["description"] == "The name field"
        assert data_schema["properties"]["value"]["description"] == "The value field"

    def test_nested_pydantic_model_schema_extracted(self):
        """Test that nested Pydantic model schemas are extracted at all levels."""
        
        @tool()
        def process_nested(data: NestedModel) -> str:
            return f"Processing nested data"
        
        # Schema should be extracted immediately
        assert len(process_nested.parameters["properties"]) > 0
        
        # Navigate to nested structure
        data_schema = process_nested.parameters["properties"]["data"]
        assert "simple" in data_schema["properties"]
        assert "items" in data_schema["properties"]
        
        # Check nested SimpleModel schema is extracted
        simple_schema = data_schema["properties"]["simple"]
        assert "properties" in simple_schema
        assert "name" in simple_schema["properties"] 
        assert "value" in simple_schema["properties"]
        
        # Check array type for items
        items_schema = data_schema["properties"]["items"]
        assert items_schema["type"] == "array"
        assert items_schema["items"]["type"] == "string"

    def test_function_without_docstring_works(self):
        """Test that functions without docstrings still get proper schemas."""
        
        @tool()
        def no_docstring_func(data: SimpleModel) -> str:
            return "result"
        
        # Should still extract schema even without docstring
        assert len(no_docstring_func.parameters["properties"]) > 0
        assert "data" in no_docstring_func.parameters["properties"]
        
        # Pydantic fields should be extracted
        data_schema = no_docstring_func.parameters["properties"]["data"]
        assert "name" in data_schema["properties"]
        assert "value" in data_schema["properties"]

    def test_function_with_docstring_works(self):
        """Test that functions with docstrings work and get descriptions."""
        
        @tool()
        def with_docstring_func(data: SimpleModel) -> str:
            """Process some data with a docstring."""
            return "result"
        
        # Should extract both schema and description
        assert with_docstring_func.description == "Process some data with a docstring."
        assert len(with_docstring_func.parameters["properties"]) > 0
        assert "data" in with_docstring_func.parameters["properties"]

    def test_to_dict_includes_complete_schema(self):
        """Test that to_dict() method returns complete schema for LLM."""
        
        @tool()
        def test_func(data: SimpleModel) -> str:
            return "result"
        
        tool_dict = test_func.to_dict()
        
        # Should have all required fields for LLM
        assert "name" in tool_dict
        assert "parameters" in tool_dict
        assert tool_dict["name"] == "test_func"
        
        # Parameters should not be empty
        params = tool_dict["parameters"]
        assert len(params["properties"]) > 0
        assert "data" in params["properties"]
        
        # Should contain the full Pydantic schema
        data_schema = params["properties"]["data"]
        assert "properties" in data_schema
        assert len(data_schema["properties"]) == 2  # name and value fields