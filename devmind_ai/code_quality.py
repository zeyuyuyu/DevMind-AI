import ast
from typing import Dict, List, Optional

class CodeQualityAnalyzer:
    def __init__(self):
        self.metrics = {}

    def analyze_file(self, file_path: str) -> Dict:
        """Analyze a Python file for various code quality metrics."""
        try:
            with open(file_path, 'r') as f:
                code = f.read()
            return self.analyze_code(code)
        except Exception as e:
            return {'error': str(e)}

    def analyze_code(self, code: str) -> Dict:
        """Analyze code string for quality metrics."""
        try:
            tree = ast.parse(code)
            metrics = {
                'cyclomatic_complexity': self._calculate_complexity(tree),
                'function_metrics': self._analyze_functions(tree),
                'maintainability_index': self._calculate_maintainability(code),
                'code_smells': self._detect_code_smells(tree)
            }
            return metrics
        except Exception as e:
            return {'error': str(e)}

    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        return complexity

    def _analyze_functions(self, tree: ast.AST) -> List[Dict]:
        """Analyze metrics for each function."""
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_metrics = {
                    'name': node.name,
                    'args_count': len(node.args.args),
                    'complexity': self._calculate_complexity(node),
                    'line_count': node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                }
                functions.append(func_metrics)
        return functions

    def _calculate_maintainability(self, code: str) -> float:
        """Calculate maintainability index (simplified version)."""
        lines = code.split('\n')
        loc = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
        comments = len([l for l in lines if l.strip().startswith('#')])
        if loc == 0:
            return 100.0
        
        # Simplified maintainability calculation
        comment_ratio = comments / max(loc, 1)
        base_score = 100.0
        complexity_penalty = self._calculate_complexity(ast.parse(code)) * 0.5
        length_penalty = (loc / 100.0) * 2
        
        maintainability = base_score - complexity_penalty - length_penalty + (comment_ratio * 10)
        return max(0.0, min(100.0, maintainability))

    def _detect_code_smells(self, tree: ast.AST) -> List[str]:
        """Detect common code smells."""
        smells = []
        
        for node in ast.walk(tree):
            # Check for long functions
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if hasattr(node, 'end_lineno') and (node.end_lineno - node.lineno) > 30:
                    smells.append(f'Long function {node.name}: {node.end_lineno - node.lineno} lines')
                
                # Check for too many arguments
                if len(node.args.args) > 5:
                    smells.append(f'Too many arguments in function {node.name}: {len(node.args.args)}')
            
            # Check for deep nesting
            if isinstance(node, (ast.If, ast.For, ast.While)):
                depth = self._get_nesting_depth(node)
                if depth > 3:
                    smells.append(f'Deep nesting detected: depth {depth}')
        
        return smells

    def _get_nesting_depth(self, node: ast.AST, depth: int = 1) -> int:
        """Calculate the nesting depth of a node."""
        max_depth = depth
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While)):
                child_depth = self._get_nesting_depth(child, depth + 1)
                max_depth = max(max_depth, child_depth)
        return max_depth
