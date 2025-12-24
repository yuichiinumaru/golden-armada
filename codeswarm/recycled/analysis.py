import ast
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class CodeMetrics:
    """Represents code quality metrics."""
    lines_of_code: int
    cyclomatic_complexity: int
    maintainability_index: float
    function_count: int
    class_count: int
    import_count: int
    comment_ratio: float
    test_coverage: Optional[float] = None

@dataclass
class StaticAnalysisResult:
    """Represents static analysis results."""
    file_path: str
    metrics: CodeMetrics
    issues: List[Dict[str, Any]]
    suggestions: List[str]
    quality_score: float
    analysis_timestamp: str

class PythonASTAnalyzer:
    """Analyzes Python code using AST (Abstract Syntax Tree)."""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset analyzer state."""
        self.functions = []
        self.classes = []
        self.imports = []
        self.complexity_score = 0
        self.lines_of_code = 0
        self.comment_lines = 0
    
    def analyze_file(self, file_path: str) -> StaticAnalysisResult:
        """Analyze a Python file and return detailed metrics."""
        self.reset()
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        self.lines_of_code = len(content.splitlines())
        
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return self._create_error_result(file_path, f"Syntax error: {str(e)}")
            
        self._visit_tree(tree)
        
        metrics = self._calculate_metrics()
        issues = self._detect_issues()
        suggestions = self._generate_suggestions(metrics, issues)
        quality_score = self._calculate_quality_score(metrics, issues)
        
        return StaticAnalysisResult(
            file_path=file_path,
            metrics=metrics,
            issues=issues,
            suggestions=suggestions,
            quality_score=quality_score,
            analysis_timestamp=datetime.now().isoformat()
        )
    
    def _visit_tree(self, tree: ast.AST):
        """Walk the AST and collect information."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                self.functions.append({
                    "name": node.name,
                    "lineno": node.lineno,
                    "complexity": self._calculate_node_complexity(node)
                })
            elif isinstance(node, ast.ClassDef):
                self.classes.append({
                    "name": node.name,
                    "lineno": node.lineno
                })
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                self.imports.append(node)
                
    def _calculate_node_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity for a node."""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.With, ast.AsyncWith, ast.And, ast.Or, ast.ExceptHandler)):
                complexity += 1
        return complexity

    def _calculate_metrics(self) -> CodeMetrics:
        """Calculate aggregate metrics."""
        total_complexity = sum(f["complexity"] for f in self.functions)
        avg_complexity = total_complexity / max(1, len(self.functions))
        
        return CodeMetrics(
            lines_of_code=self.lines_of_code,
            cyclomatic_complexity=int(avg_complexity),
            maintainability_index=self._calculate_mi(avg_complexity),
            function_count=len(self.functions),
            class_count=len(self.classes),
            import_count=len(self.imports),
            comment_ratio=0.0 # Placeholder for actual logic
        )

    def _calculate_mi(self, complexity: float) -> float:
        """Calculate Maintainability Index (simplified)."""
        # Very simplified MI formula
        mi = 100 - (complexity * 5)
        return max(0, min(100, mi))

    def _detect_issues(self) -> List[Dict[str, Any]]:
        """Identify potential code issues."""
        issues = []
        for func in self.functions:
            if func["complexity"] > 10:
                issues.append({
                    "type": "complexity",
                    "severity": "high",
                    "message": f"Function '{func['name']}' is too complex (complexity: {func['complexity']})",
                    "line": func["lineno"]
                })
        return issues

    def _generate_suggestions(self, metrics: CodeMetrics, issues: List[Dict]) -> List[str]:
        """Generate improvement suggestions."""
        suggestions = []
        if metrics.cyclomatic_complexity > 7:
            suggestions.append("Refactor complex functions into smaller, more focused ones.")
        if len(issues) > 0:
            suggestions.append(f"Address the {len(issues)} high-priority issues identified.")
        return suggestions

    def _calculate_quality_score(self, metrics: CodeMetrics, issues: List[Dict]) -> float:
        """Calculate overall quality score (0-100)."""
        score = metrics.maintainability_index
        score -= len(issues) * 10
        return max(0, min(100, score))

    def _create_error_result(self, file_path: str, message: str) -> StaticAnalysisResult:
        """Create a result representing an error."""
        return StaticAnalysisResult(
            file_path=file_path,
            metrics=CodeMetrics(0, 0, 0.0, 0, 0, 0, 0.0),
            issues=[{"type": "error", "message": message}],
            suggestions=["Fix syntax errors before further analysis."],
            quality_score=0.0,
            analysis_timestamp=datetime.now().isoformat()
        )

if __name__ == "__main__":
    analyzer = PythonASTAnalyzer()
    # Simple self-test
    try:
        result = analyzer.analyze_file(__file__)
        print(f"File: {result.file_path}")
        print(f"Quality Score: {result.quality_score}")
        print(f"Functions: {result.metrics.function_count}")
        for issue in result.issues:
            print(f"Issue: {issue['message']} at line {issue.get('line')}")
    except Exception as e:
        print(f"Error: {e}")
