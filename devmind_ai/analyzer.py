"""DevMind AI code analyzer module for evaluating code quality and complexity."""

from typing import Dict, List, Optional
import ast
import math

class CodeAnalyzer:
    def __init__(self):
        self.metrics = {}

    def analyze_code(self, code: str) -> Dict:
        """Analyze code and return comprehensive metrics."""
        try:
            tree = ast.parse(code)
            self.metrics = {
                'complexity': self._calculate_complexity(tree),
                'maintainability': self._calculate_maintainability(tree),
                'code_smells': self._detect_code_smells(tree),
                'documentation_score': self._assess_documentation(tree),
                'security_issues': self._check_security(tree)
            }
            return self.metrics
        except SyntaxError:
            return {'error': 'Invalid Python syntax'}

    def _calculate_complexity(self, tree: ast.AST) -> Dict:
        """Calculate cyclomatic complexity and cognitive complexity."""
        complexity = {'cyclomatic': 1, 'cognitive': 0}
        
        class ComplexityVisitor(ast.NodeVisitor):
            def __init__(self):
                self.cyclomatic = 1
                self.cognitive = 0
                self.nesting = 0

            def visit_If(self, node):
                self.cyclomatic += len(node.orelse) + 1
                self.cognitive += (1 + self.nesting)
                self.nesting += 1
                self.generic_visit(node)
                self.nesting -= 1

            def visit_While(self, node):
                self.cyclomatic += 1
                self.cognitive += (1 + self.nesting)
                self.nesting += 1
                self.generic_visit(node)
                self.nesting -= 1

            def visit_For(self, node):
                self.cyclomatic += 1
                self.cognitive += (1 + self.nesting)
                self.nesting += 1
                self.generic_visit(node)
                self.nesting -= 1

        visitor = ComplexityVisitor()
        visitor.visit(tree)
        complexity['cyclomatic'] = visitor.cyclomatic
        complexity['cognitive'] = visitor.cognitive
        return complexity

    def _calculate_maintainability(self, tree: ast.AST) -> float:
        """Calculate maintainability index based on various metrics."""
        loc = len(ast.unparse(tree).splitlines())
        complexity = self._calculate_complexity(tree)['cyclomatic']
        
        # Maintainability Index formula
        halstead_volume = math.log(loc) * complexity
        mi = max(0, (171 - 5.2 * math.log(halstead_volume) - 0.23 * complexity - 16.2 * math.log(loc)) * 100 / 171)
        return round(mi, 2)

    def _detect_code_smells(self, tree: ast.AST) -> List[Dict]:
        """Detect common code smells and anti-patterns."""
        smells = []
        
        class SmellDetector(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                # Check function length
                if len(node.body) > 20:
                    smells.append({
                        'type': 'long_function',
                        'message': f'Function {node.name} is too long ({len(node.body)} lines)',
                        'line': node.lineno
                    })
                
                # Check number of parameters
                args = len(node.args.args)
                if args > 5:
                    smells.append({
                        'type': 'too_many_parameters',
                        'message': f'Function {node.name} has too many parameters ({args})',
                        'line': node.lineno
                    })
                self.generic_visit(node)

        SmellDetector().visit(tree)
        return smells

    def _assess_documentation(self, tree: ast.AST) -> float:
        """Assess documentation coverage and quality."""
        class DocVisitor(ast.NodeVisitor):
            def __init__(self):
                self.doc_count = 0
                self.total_count = 0

            def visit_FunctionDef(self, node):
                self.total_count += 1
                if ast.get_docstring(node):
                    self.doc_count += 1
                self.generic_visit(node)

            def visit_ClassDef(self, node):
                self.total_count += 1
                if ast.get_docstring(node):
                    self.doc_count += 1
                self.generic_visit(node)

        visitor = DocVisitor()
        visitor.visit(tree)
        return round(visitor.doc_count / max(1, visitor.total_count) * 100, 2)

    def _check_security(self, tree: ast.AST) -> List[Dict]:
        """Check for basic security issues."""
        issues = []
        
        class SecurityVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['eval', 'exec']:
                        issues.append({
                            'type': 'security_risk',
                            'message': f'Usage of {node.func.id}() is potentially dangerous',
                            'line': node.lineno
                        })
                self.generic_visit(node)

        SecurityVisitor().visit(tree)
        return issues

    def get_summary(self) -> str:
        """Generate a human-readable summary of the analysis."""
        if not self.metrics:
            return "No analysis performed yet."

        summary = ["Code Analysis Summary:"]
        summary.append(f"Maintainability Index: {self.metrics['maintainability']}/100")
        summary.append(f"Cyclomatic Complexity: {self.metrics['complexity']['cyclomatic']}")
        summary.append(f"Cognitive Complexity: {self.metrics['complexity']['cognitive']}")
        summary.append(f"Documentation Coverage: {self.metrics['documentation_score']}%")
        
        if self.metrics['code_smells']:
            summary.append("\nCode Smells:")
            for smell in self.metrics['code_smells']:
                summary.append(f"- {smell['message']}")

        if self.metrics['security_issues']:
            summary.append("\nSecurity Issues:")
            for issue in self.metrics['security_issues']:
                summary.append(f"- {issue['message']}")

        return '\n'.join(summary)
