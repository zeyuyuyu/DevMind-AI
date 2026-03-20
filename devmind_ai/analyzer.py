"""DevMind AI code analyzer module for measuring code quality metrics."""

import ast
import math
from typing import Dict, List, Optional

class CodeAnalyzer:
    def __init__(self, code: str):
        self.code = code
        self.ast_tree = ast.parse(code)
        
    def analyze(self) -> Dict[str, float]:
        """Analyze code and return various complexity metrics."""
        metrics = {
            'cyclomatic_complexity': self.calculate_cyclomatic_complexity(),
            'maintainability_index': self.calculate_maintainability_index(),
            'cognitive_complexity': self.calculate_cognitive_complexity(),
            'lines_of_code': len(self.code.splitlines())
        }
        return metrics
    
    def calculate_cyclomatic_complexity(self) -> int:
        """Calculate McCabe's cyclomatic complexity."""
        complexity = 1  # Base complexity
        
        class ComplexityVisitor(ast.NodeVisitor):
            def __init__(self):
                self.complexity = 0
                
            def visit_If(self, node):
                self.complexity += 1
                self.generic_visit(node)
                
            def visit_While(self, node):
                self.complexity += 1
                self.generic_visit(node)
                
            def visit_For(self, node):
                self.complexity += 1
                self.generic_visit(node)
                
            def visit_Try(self, node):
                self.complexity += 1
                self.generic_visit(node)
                
            def visit_ExceptHandler(self, node):
                self.complexity += 1
                self.generic_visit(node)
                
            def visit_BoolOp(self, node):
                self.complexity += len(node.values) - 1
                self.generic_visit(node)
        
        visitor = ComplexityVisitor()
        visitor.visit(self.ast_tree)
        return complexity + visitor.complexity
    
    def calculate_maintainability_index(self) -> float:
        """Calculate maintainability index based on Halstead Volume and cyclomatic complexity."""
        halstead_volume = self._calculate_halstead_volume()
        cyclomatic = self.calculate_cyclomatic_complexity()
        loc = len(self.code.splitlines())
        
        mi = 171 - 5.2 * math.log(halstead_volume) - 0.23 * cyclomatic - 16.2 * math.log(loc)
        return max(0, min(100, mi))  # Normalize between 0 and 100
    
    def calculate_cognitive_complexity(self) -> int:
        """Calculate cognitive complexity based on nested control flow structures."""
        class CognitiveComplexityVisitor(ast.NodeVisitor):
            def __init__(self):
                self.complexity = 0
                self.nesting_level = 0
                
            def visit_If(self, node):
                self.complexity += (1 + self.nesting_level)
                self.nesting_level += 1
                self.generic_visit(node)
                self.nesting_level -= 1
                
            def visit_While(self, node):
                self.complexity += (1 + self.nesting_level)
                self.nesting_level += 1
                self.generic_visit(node)
                self.nesting_level -= 1
                
            def visit_For(self, node):
                self.complexity += (1 + self.nesting_level)
                self.nesting_level += 1
                self.generic_visit(node)
                self.nesting_level -= 1
        
        visitor = CognitiveComplexityVisitor()
        visitor.visit(self.ast_tree)
        return visitor.complexity
    
    def _calculate_halstead_volume(self) -> float:
        """Helper method to calculate Halstead Volume metric."""
        class HalsteadVisitor(ast.NodeVisitor):
            def __init__(self):
                self.operators = set()
                self.operands = set()
                
            def visit_BinOp(self, node):
                self.operators.add(type(node.op).__name__)
                self.generic_visit(node)
                
            def visit_Name(self, node):
                self.operands.add(node.id)
                self.generic_visit(node)
                
            def visit_Num(self, node):
                self.operands.add(str(node.n))
                self.generic_visit(node)
        
        visitor = HalsteadVisitor()
        visitor.visit(self.ast_tree)
        
        n1 = len(visitor.operators)
        n2 = len(visitor.operands)
        if n1 == 0 or n2 == 0:
            return 0
        
        N = n1 + n2
        n = len(visitor.operators) + len(visitor.operands)
        return N * math.log2(n) if n > 0 else 0
