"""DevMind AI code analyzer module for generating insights and metrics."""

import ast
import os
from collections import defaultdict
from typing import Dict, List, Tuple

class CodeAnalyzer:
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.metrics = defaultdict(dict)
        self.insights = []

    def analyze_project(self) -> Tuple[Dict, List[str]]:
        """Analyze entire project and generate metrics and insights."""
        for root, _, files in os.walk(self.project_path):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    self._analyze_file(filepath)
        
        self._generate_insights()
        return dict(self.metrics), self.insights

    def _analyze_file(self, filepath: str) -> None:
        """Analyze a single Python file for various metrics."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()
            
            tree = ast.parse(code)
            analyzer = ASTAnalyzer()
            analyzer.visit(tree)
            
            rel_path = os.path.relpath(filepath, self.project_path)
            self.metrics[rel_path] = {
                'loc': len(code.splitlines()),
                'functions': analyzer.function_count,
                'classes': analyzer.class_count,
                'complexity': analyzer.complexity,
                'imports': len(analyzer.imports),
                'docstring_coverage': analyzer.docstring_coverage
            }
        except Exception as e:
            print(f'Error analyzing {filepath}: {str(e)}')

    def _generate_insights(self) -> None:
        """Generate insights based on collected metrics."""
        self.insights = []
        
        # Identify complex files
        for filepath, metrics in self.metrics.items():
            if metrics['complexity'] > 10:
                self.insights.append(
                    f'High complexity in {filepath} (score: {metrics["complexity"]}). '
                    'Consider refactoring into smaller functions.'
                )
            
            if metrics['docstring_coverage'] < 0.5:
                self.insights.append(
                    f'Low documentation coverage in {filepath} '
                    f'({metrics["docstring_coverage"]*100:.1f}%). Add more docstrings.'
                )

class ASTAnalyzer(ast.NodeVisitor):
    """AST visitor to collect code metrics."""
    
    def __init__(self):
        self.function_count = 0
        self.class_count = 0
        self.complexity = 0
        self.imports = set()
        self.has_docstring = 0
        self.needs_docstring = 0

    def visit_FunctionDef(self, node):
        """Analyze function definitions."""
        self.function_count += 1
        self.needs_docstring += 1
        if ast.get_docstring(node):
            self.has_docstring += 1
        self.complexity += self._count_branches(node)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        """Analyze class definitions."""
        self.class_count += 1
        self.needs_docstring += 1
        if ast.get_docstring(node):
            self.has_docstring += 1
        self.generic_visit(node)

    def visit_Import(self, node):
        """Track import statements."""
        for name in node.names:
            self.imports.add(name.name)

    def visit_ImportFrom(self, node):
        """Track from-import statements."""
        if node.module:
            self.imports.add(node.module)

    def _count_branches(self, node) -> int:
        """Count branching statements to estimate complexity."""
        count = 0
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.Try)):
                count += 1
        return count

    @property
    def docstring_coverage(self) -> float:
        """Calculate docstring coverage ratio."""
        if self.needs_docstring == 0:
            return 1.0
        return self.has_docstring / self.needs_docstring
