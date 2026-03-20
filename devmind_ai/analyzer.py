"""DevMind AI code analyzer module for providing intelligent code insights."""

from typing import Dict, List, Optional
import ast
import statistics

class CodeAnalyzer:
    def __init__(self):
        self.metrics = {}
        self.suggestions = []

    def analyze_code(self, code: str) -> Dict:
        """Analyze code and return metrics and suggestions."""
        try:
            tree = ast.parse(code)
            self._reset_analysis()
            self._collect_metrics(tree)
            self._generate_suggestions()
            return {
                'metrics': self.metrics,
                'suggestions': self.suggestions
            }
        except SyntaxError as e:
            return {'error': f'Syntax error in code: {str(e)}'}

    def _reset_analysis(self) -> None:
        """Reset analysis state."""
        self.metrics = {
            'num_functions': 0,
            'num_classes': 0,
            'avg_function_complexity': 0,
            'avg_line_length': 0,
            'docstring_coverage': 0
        }
        self.suggestions = []

    def _collect_metrics(self, tree: ast.AST) -> None:
        """Collect code metrics from AST."""
        # Count functions and classes
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        
        self.metrics['num_functions'] = len(functions)
        self.metrics['num_classes'] = len(classes)

        # Calculate cyclomatic complexity
        complexities = [self._calculate_complexity(func) for func in functions]
        self.metrics['avg_function_complexity'] = (
            statistics.mean(complexities) if complexities else 0
        )

        # Calculate docstring coverage
        documented = sum(1 for node in functions + classes if ast.get_docstring(node))
        total = len(functions) + len(classes)
        self.metrics['docstring_coverage'] = (
            documented / total * 100 if total > 0 else 0
        )

    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity of an AST node."""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity

    def _generate_suggestions(self) -> None:
        """Generate improvement suggestions based on metrics."""
        if self.metrics['avg_function_complexity'] > 10:
            self.suggestions.append(
                'Consider breaking down complex functions into smaller ones'
            )

        if self.metrics['docstring_coverage'] < 80:
            self.suggestions.append(
                'Improve documentation coverage by adding docstrings'
            )

        if self.metrics['num_functions'] > 20:
            self.suggestions.append(
                'Consider splitting the module into smaller ones'
            )

    def get_code_quality_score(self) -> float:
        """Calculate overall code quality score."""
        if not self.metrics:
            return 0.0

        scores = [
            min(100 - self.metrics['avg_function_complexity'] * 5, 100),
            self.metrics['docstring_coverage'],
            100 if self.metrics['num_functions'] < 20 else 80
        ]
        return statistics.mean(scores)

    def format_report(self) -> str:
        """Format analysis results as a readable report."""
        if not self.metrics:
            return 'No analysis results available'

        report = ['Code Analysis Report', '=' * 20]
        report.append('\nMetrics:')
        for metric, value in self.metrics.items():
            report.append(f'{metric}: {value}')

        report.append('\nQuality Score:')
        report.append(f'{self.get_code_quality_score():.1f}/100')

        if self.suggestions:
            report.append('\nSuggestions:')
            for suggestion in self.suggestions:
                report.append(f'- {suggestion}')

        return '\n'.join(report)
