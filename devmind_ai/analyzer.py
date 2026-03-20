import ast
import asyncio
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from collections import defaultdict
import re

@dataclass
class CodeAnalysis:
    complexity: int
    sentiment: float
    patterns: Dict[str, int]
    suggestions: List[str]

class CodeAnalyzer:
    def __init__(self):
        self.negative_patterns = [
            r'hack', r'todo', r'fixme', r'workaround',
            r'temporary', r'legacy', r'deprecated'
        ]
        self.positive_patterns = [
            r'optimize', r'improve', r'enhance', r'clean',
            r'refactor', r'simplify', r'modernize'
        ]

    async def analyze_code(self, code: str) -> CodeAnalysis:
        """Analyzes code for complexity, patterns and generates suggestions."""
        tasks = [
            self._calculate_complexity(code),
            self._analyze_sentiment(code),
            self._detect_patterns(code)
        ]
        complexity, sentiment, patterns = await asyncio.gather(*tasks)
        suggestions = await self._generate_suggestions(complexity, sentiment, patterns)
        
        return CodeAnalysis(
            complexity=complexity,
            sentiment=sentiment,
            patterns=patterns,
            suggestions=suggestions
        )

    async def _calculate_complexity(self, code: str) -> int:
        """Calculate cyclomatic complexity of the code."""
        try:
            tree = ast.parse(code)
            visitor = ComplexityVisitor()
            visitor.visit(tree)
            return visitor.complexity
        except:
            return 0

    async def _analyze_sentiment(self, code: str) -> float:
        """Analyze code sentiment based on patterns and comments."""
        sentiment = 0.0
        
        # Analyze comments
        comments = re.findall(r'#.*$', code, re.MULTILINE)
        for comment in comments:
            sentiment += sum(1 for p in self.positive_patterns if re.search(p, comment.lower()))
            sentiment -= sum(1 for p in self.negative_patterns if re.search(p, comment.lower()))

        # Analyze variable names and function names
        names = re.findall(r'\b(?:def|class|var)\s+([a-zA-Z_]\w*)', code)
        for name in names:
            sentiment += 0.5 if any(p in name.lower() for p in ['good', 'better', 'best', 'improve'])
            sentiment -= 0.5 if any(p in name.lower() for p in ['temp', 'hack', 'fix'])

        return sentiment

    async def _detect_patterns(self, code: str) -> Dict[str, int]:
        """Detect common code patterns and anti-patterns."""
        patterns = defaultdict(int)
        
        # Detect long functions
        functions = re.finditer(r'def\s+\w+\s*\([^)]*\):\s*(?:[^\n]*\n+)+', code)
        for func in functions:
            lines = func.group().count('\n')
            if lines > 20:
                patterns['long_functions'] += 1

        # Detect nested loops
        nested_loops = len(re.findall(r'\s*for.*:\s*\n+\s*for.*:', code))
        patterns['nested_loops'] = nested_loops

        # Detect large try-except blocks
        try_blocks = re.finditer(r'try:\s*(?:[^\n]*\n+)+', code)
        for block in try_blocks:
            lines = block.group().count('\n')
            if lines > 15:
                patterns['large_try_blocks'] += 1

        return dict(patterns)

    async def _generate_suggestions(self
        self, complexity: int,
        sentiment: float,
        patterns: Dict[str, int]
    ) -> List[str]:
        """Generate improvement suggestions based on analysis."""
        suggestions = []

        if complexity > 10:
            suggestions.append(
                'Consider breaking down complex functions into smaller, more manageable pieces'
            )

        if patterns.get('long_functions', 0) > 0:
            suggestions.append(
                'Some functions are too long. Consider extracting functionality into helper methods'
            )

        if patterns.get('nested_loops', 0) > 0:
            suggestions.append(
                'Nested loops detected. Consider restructuring to improve performance'
            )

        if sentiment < 0:
            suggestions.append(
                'Code contains several temporary solutions or workarounds. Consider proper refactoring'
            )

        return suggestions

class ComplexityVisitor(ast.NodeVisitor):
    def __init__(self):
        self.complexity = 1

    def visit_If(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_While(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_For(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        self.complexity += 1
        self.generic_visit(node)
