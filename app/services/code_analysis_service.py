"""
Code analysis service.
Handles code parsing, AST generation, and structure extraction.
"""

import ast
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class FunctionInfo:
    """Function information structure."""
    name: str
    lineno: int
    end_lineno: Optional[int]
    args: List[str]
    defaults: List[str]
    return_type: Optional[str]
    docstring: Optional[str]
    decorators: List[str]
    is_async: bool = False


@dataclass
class ClassInfo:
    """Class information structure."""
    name: str
    lineno: int
    end_lineno: Optional[int]
    bases: List[str]
    methods: List[FunctionInfo]
    attributes: List[str]
    docstring: Optional[str]
    decorators: List[str]


@dataclass
class ImportInfo:
    """Import information structure."""
    module: str
    names: List[str]
    alias: Optional[str]
    lineno: int
    is_from: bool = False


@dataclass
class CodeStructure:
    """Complete code structure."""
    classes: List[ClassInfo]
    functions: List[FunctionInfo]
    variables: List[Dict[str, Any]]
    imports: List[ImportInfo]
    errors: List[str]


class PythonCodeAnalyzer(ast.NodeVisitor):
    """Python code AST analyzer."""

    def __init__(self, source_code: str):
        self.source_code = source_code
        self.source_lines = source_code.split("\n")
        self.classes: List[ClassInfo] = []
        self.functions: List[FunctionInfo] = []
        self.variables: List[Dict[str, Any]] = []
        self.imports: List[ImportInfo] = []
        self.errors: List[str] = []
        self._current_class: Optional[str] = None

    def analyze(self) -> CodeStructure:
        """
        Analyze Python source code.

        Returns:
            CodeStructure containing analysis results
        """
        try:
            tree = ast.parse(self.source_code)
            self.visit(tree)
        except SyntaxError as e:
            self.errors.append(f"Syntax error at line {e.lineno}: {e.msg}")

        return CodeStructure(
            classes=self.classes,
            functions=self.functions,
            variables=self.variables,
            imports=self.imports,
            errors=self.errors
        )

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Process class definition."""
        self._current_class = node.name

        # Extract base classes
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(f"{self._get_attr_name(base)}")

        # Extract methods and attributes
        methods = []
        attributes = []

        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(self._extract_function_info(item))
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        attributes.append(target.id)

        # Extract decorators
        decorators = [self._get_decorator_name(d) for d in node.decorator_list]

        class_info = ClassInfo(
            name=node.name,
            lineno=node.lineno,
            end_lineno=getattr(node, "end_lineno", None),
            bases=bases,
            methods=methods,
            attributes=attributes,
            docstring=ast.get_docstring(node),
            decorators=decorators
        )

        self.classes.append(class_info)
        self._current_class = None
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Process function definition."""
        if self._current_class is None:
            func_info = self._extract_function_info(node)
            self.functions.append(func_info)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Process async function definition."""
        if self._current_class is None:
            func_info = self._extract_function_info(node, is_async=True)
            self.functions.append(func_info)
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        """Process variable assignment."""
        if self._current_class is None:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.variables.append({
                        "name": target.id,
                        "lineno": node.lineno,
                        "value_type": self._get_value_type(node.value)
                    })
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        """Process import statement."""
        for alias in node.names:
            self.imports.append(ImportInfo(
                module=alias.name,
                names=[alias.name],
                alias=alias.asname,
                lineno=node.lineno,
                is_from=False
            ))

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Process from-import statement."""
        names = [alias.name for alias in node.names]
        self.imports.append(ImportInfo(
            module=node.module or "",
            names=names,
            alias=None,
            lineno=node.lineno,
            is_from=True
        ))

    def _extract_function_info(
        self,
        node: ast.FunctionDef,
        is_async: bool = False
    ) -> FunctionInfo:
        """Extract function information from AST node."""
        # Get arguments
        args = []
        for arg in node.args.args:
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {ast.unparse(arg.annotation)}"
            args.append(arg_str)

        # Get default values
        defaults = [ast.unparse(d) for d in node.args.defaults]

        # Get return type
        return_type = None
        if node.returns:
            return_type = ast.unparse(node.returns)

        # Get decorators
        decorators = [self._get_decorator_name(d) for d in node.decorator_list]

        return FunctionInfo(
            name=node.name,
            lineno=node.lineno,
            end_lineno=getattr(node, "end_lineno", None),
            args=args,
            defaults=defaults,
            return_type=return_type,
            docstring=ast.get_docstring(node),
            decorators=decorators,
            is_async=is_async or isinstance(node, ast.AsyncFunctionDef)
        )

    def _get_attr_name(self, node: ast.Attribute) -> str:
        """Get full attribute name."""
        parts = []
        current = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        return ".".join(reversed(parts))

    def _get_decorator_name(self, node: ast.expr) -> str:
        """Get decorator name."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return self._get_attr_name(node)
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                return node.func.id
            elif isinstance(node.func, ast.Attribute):
                return self._get_attr_name(node.func)
        return str(node)

    def _get_value_type(self, node: ast.expr) -> str:
        """Get value type from AST node."""
        if isinstance(node, ast.Constant):
            return type(node.value).__name__
        elif isinstance(node, ast.List):
            return "list"
        elif isinstance(node, ast.Dict):
            return "dict"
        elif isinstance(node, ast.Set):
            return "set"
        elif isinstance(node, ast.Tuple):
            return "tuple"
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                return node.func.id
        return "unknown"


class CodeAnalysisService:
    """Service for code analysis operations."""

    LANGUAGE_EXTENSIONS = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".jsx": "javascript",
        ".tsx": "typescript",
        ".java": "java",
        ".go": "go",
        ".rs": "rust",
        ".cpp": "cpp",
        ".c": "c",
        ".rb": "ruby",
        ".php": "php"
    }

    def detect_language(self, file_path: str) -> Optional[str]:
        """
        Detect programming language from file extension.

        Args:
            file_path: Path to the file

        Returns:
            Language name or None
        """
        ext = os.path.splitext(file_path)[1].lower()
        return self.LANGUAGE_EXTENSIONS.get(ext)

    def analyze_python_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a Python file.

        Args:
            file_path: Path to Python file

        Returns:
            Analysis results
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source_code = f.read()
            return self.analyze_python_code(source_code)
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def analyze_python_code(self, source_code: str) -> Dict[str, Any]:
        """
        Analyze Python source code.

        Args:
            source_code: Python source code string

        Returns:
            Analysis results with code structure
        """
        analyzer = PythonCodeAnalyzer(source_code)
        structure = analyzer.analyze()

        # Convert to dictionary for JSON serialization
        result = {
            "status": "success" if not structure.errors else "partial",
            "structure": {
                "classes": [asdict(c) for c in structure.classes],
                "functions": [asdict(f) for f in structure.functions],
                "variables": structure.variables,
                "imports": [asdict(i) for i in structure.imports]
            },
            "errors": structure.errors,
            "metrics": self._calculate_metrics(source_code, structure)
        }

        return result

    def _calculate_metrics(
        self,
        source_code: str,
        structure: CodeStructure
    ) -> Dict[str, Any]:
        """Calculate code metrics."""
        lines = source_code.split("\n")
        non_empty_lines = [l for l in lines if l.strip()]
        comment_lines = [l for l in lines if l.strip().startswith("#")]

        return {
            "total_lines": len(lines),
            "code_lines": len(non_empty_lines) - len(comment_lines),
            "comment_lines": len(comment_lines),
            "blank_lines": len(lines) - len(non_empty_lines),
            "classes_count": len(structure.classes),
            "functions_count": len(structure.functions),
            "imports_count": len(structure.imports)
        }

    def analyze_repository(
        self,
        repo_path: str,
        extensions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze all code files in a repository.

        Args:
            repo_path: Path to repository
            extensions: File extensions to analyze

        Returns:
            Repository analysis results
        """
        if extensions is None:
            extensions = [".py"]

        results = {
            "files": [],
            "summary": {
                "total_files": 0,
                "total_lines": 0,
                "total_classes": 0,
                "total_functions": 0,
                "languages": {}
            }
        }

        for root, dirs, files in os.walk(repo_path):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith(".")]

            for filename in files:
                ext = os.path.splitext(filename)[1]
                if ext not in extensions:
                    continue

                file_path = os.path.join(root, filename)
                rel_path = os.path.relpath(file_path, repo_path)
                language = self.detect_language(filename)

                if language == "python":
                    analysis = self.analyze_python_file(file_path)
                    if analysis.get("status") in ["success", "partial"]:
                        file_result = {
                            "path": rel_path,
                            "language": language,
                            "structure": analysis.get("structure"),
                            "metrics": analysis.get("metrics"),
                            "errors": analysis.get("errors", [])
                        }
                        results["files"].append(file_result)

                        # Update summary
                        results["summary"]["total_files"] += 1
                        metrics = analysis.get("metrics", {})
                        results["summary"]["total_lines"] += metrics.get("total_lines", 0)
                        results["summary"]["total_classes"] += metrics.get("classes_count", 0)
                        results["summary"]["total_functions"] += metrics.get("functions_count", 0)

                        if language not in results["summary"]["languages"]:
                            results["summary"]["languages"][language] = 0
                        results["summary"]["languages"][language] += 1

        return results

    def get_code_context(
        self,
        file_path: str,
        start_line: int,
        end_line: Optional[int] = None,
        context_lines: int = 5
    ) -> Dict[str, Any]:
        """
        Get code context around specific lines.

        Args:
            file_path: Path to file
            start_line: Starting line number (1-indexed)
            end_line: Ending line number
            context_lines: Number of context lines before/after

        Returns:
            Code context with surrounding lines
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            end_line = end_line or start_line
            context_start = max(0, start_line - context_lines - 1)
            context_end = min(len(lines), end_line + context_lines)

            return {
                "status": "success",
                "file_path": file_path,
                "start_line": start_line,
                "end_line": end_line,
                "context": {
                    "before": "".join(lines[context_start:start_line - 1]),
                    "target": "".join(lines[start_line - 1:end_line]),
                    "after": "".join(lines[end_line:context_end])
                },
                "full_context": "".join(lines[context_start:context_end])
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }


# Global service instance
code_analysis_service = CodeAnalysisService()
