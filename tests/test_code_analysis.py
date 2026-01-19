"""
Tests for the code analysis service.
"""

import pytest
from app.services.code_analysis_service import (
    PythonCodeAnalyzer,
    CodeAnalysisService,
    code_analysis_service
)


class TestPythonCodeAnalyzer:
    """Test cases for Python code analyzer."""

    def test_analyze_simple_function(self):
        """Test analyzing a simple function."""
        code = '''
def add(a: int, b: int = 0) -> int:
    """Add two numbers."""
    return a + b
'''
        analyzer = PythonCodeAnalyzer(code)
        result = analyzer.analyze()

        assert len(result.functions) == 1
        func = result.functions[0]
        assert func.name == "add"
        assert "a: int" in func.args
        assert "b: int" in func.args
        assert func.return_type == "int"
        assert func.docstring == "Add two numbers."

    def test_analyze_class(self):
        """Test analyzing a class."""
        code = '''
class Calculator:
    """A simple calculator."""

    def __init__(self):
        self.result = 0

    def add(self, x: int, y: int) -> int:
        """Add two numbers."""
        self.result = x + y
        return self.result
'''
        analyzer = PythonCodeAnalyzer(code)
        result = analyzer.analyze()

        assert len(result.classes) == 1
        cls = result.classes[0]
        assert cls.name == "Calculator"
        assert cls.docstring == "A simple calculator."
        assert len(cls.methods) == 2  # __init__ and add

    def test_analyze_imports(self):
        """Test analyzing imports."""
        code = '''
import os
import sys
from typing import List, Optional
from collections.abc import Mapping
'''
        analyzer = PythonCodeAnalyzer(code)
        result = analyzer.analyze()

        assert len(result.imports) == 4
        import_modules = [i.module for i in result.imports]
        assert "os" in import_modules
        assert "sys" in import_modules
        assert "typing" in import_modules

    def test_analyze_syntax_error(self):
        """Test handling syntax errors."""
        code = '''
def broken_function(
    # Missing closing parenthesis
'''
        analyzer = PythonCodeAnalyzer(code)
        result = analyzer.analyze()

        assert len(result.errors) > 0
        assert "Syntax error" in result.errors[0]


class TestCodeAnalysisService:
    """Test cases for code analysis service."""

    def test_detect_language(self):
        """Test language detection."""
        assert code_analysis_service.detect_language("main.py") == "python"
        assert code_analysis_service.detect_language("app.js") == "javascript"
        assert code_analysis_service.detect_language("Main.java") == "java"
        assert code_analysis_service.detect_language("main.go") == "go"
        assert code_analysis_service.detect_language("unknown.xyz") is None

    def test_analyze_python_code(self):
        """Test analyzing Python code."""
        code = '''
def greet(name: str) -> str:
    """Greet someone."""
    return f"Hello, {name}!"

class Greeter:
    def __init__(self, prefix: str = "Hi"):
        self.prefix = prefix

    def greet(self, name: str) -> str:
        return f"{self.prefix}, {name}!"
'''
        result = code_analysis_service.analyze_python_code(code)

        assert result["status"] == "success"
        assert len(result["structure"]["functions"]) == 1
        assert len(result["structure"]["classes"]) == 1
        assert result["metrics"]["functions_count"] == 1
        assert result["metrics"]["classes_count"] == 1

    def test_calculate_metrics(self):
        """Test metrics calculation."""
        code = '''# This is a comment
def foo():
    pass

class Bar:
    pass
'''
        result = code_analysis_service.analyze_python_code(code)
        metrics = result["metrics"]

        assert metrics["comment_lines"] >= 1
        assert metrics["functions_count"] == 1
        assert metrics["classes_count"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
