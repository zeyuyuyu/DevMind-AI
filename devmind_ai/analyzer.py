import ast
import os
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class CodeMetrics:
    cyclomatic_complexity: int
    number_of_lines: int
    number_of_functions: int
    cognitive_complexity: int
    maintainability_index: float

class CodeAnalyzer:
    def __init__(self, code: str):
        self.code = code
        self.tree = ast.parse(code)
    
    def analyze(self) -> CodeMetrics:
        """Analyze code and return comprehensive metrics."""
        metrics = CodeMetrics(
            cyclomatic_complexity=self._calculate_cyclomatic_complexity(),
            number_of_lines=self._count_lines(),
            number_of_functions=self._count_functions(),
            cognitive_complexity=self._calculate_cognitive_complexity(),
            maintainability_index=self._calculate_maintainability_index()
        )
        return metrics

    def _calculate_cyclomatic_complexity(self) -> int:
        """Calculate McCabe's cyclomatic complexity."""
        complexity = 1
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.Break,
                               ast.Continue, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        return complexity

    def _count_lines(self) -> int:
        """Count number of non-empty lines."""
        return len([line for line in self.code.splitlines() if line.strip()])

    def _count_functions(self) -> int:
        """Count number of function definitions."""
        return len([node for node in ast.walk(self.tree)
                   if isinstance(node, ast.FunctionDef)])

    def _calculate_cognitive_complexity(self) -> int:
        """Calculate cognitive complexity based on nesting and control flow."""
        complexity = 0
        nesting_level = 0

        class CognitiveComplexityVisitor(ast.NodeVisitor):
            def __init__(self):
                self.complexity = 0
                self.nesting = 0

            def visit_If(self, node):
                self.complexity += 1 + self.nesting
                self.nesting += 1
                self.generic_visit(node)
                self.nesting -= 1

            def visit_For(self, node):
                self.complexity += 1 + self.nesting
                self.nesting += 1
                self.generic_visit(node)
                self.nesting -= 1

            def visit_While(self, node):
                self.complexity += 1 + self.nesting
                self.nesting += 1
                self.generic_visit(node)
                self.nesting -= 1

        visitor = CognitiveComplexityVisitor()
        visitor.visit(self.tree)
        return visitor.complexity

    def _calculate_maintainability_index(self) -> float:
        """Calculate maintainability index based on various metrics."""
        # Simplified version of the maintainability index formula
        loc = self._count_lines()
        cc = self._calculate_cyclomatic_complexity()
        
        # MI = 171 - 5.2 * ln(HV) - 0.23 * CC - 16.2 * ln(LOC)
        # Using simplified version here
        mi = 171 - (0.23 * cc) - (16.2 * (loc and abs(log(loc)) or 0))
        return max(0.0, min(100.0, mi))

    @staticmethod
    def analyze_file(filepath: str) -> Optional[CodeMetrics]:
        """Analyze a Python file and return its metrics."""
        try:
            with open(filepath, 'r') as f:
                code = f.read()
            analyzer = CodeAnalyzer(code)
            return analyzer.analyze()
        except Exception as e:
            print(f"Error analyzing {filepath}: {str(e)}")
            return None

    @staticmethod
    def analyze_directory(directory: str) -> Dict[str, CodeMetrics]:
        """Analyze all Python files in a directory recursively."""
        results = {}
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    metrics = CodeAnalyzer.analyze_file(filepath)
                    if metrics:
                        results[filepath] = metrics
        return results