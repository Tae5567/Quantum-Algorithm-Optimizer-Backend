"""
Complexity Analyzer Agent (Nova Pro)

Analyzes computational complexity
Identifies problem class (NP-hard, etc.)
Estimates variable/constraint counts
"""

from typing import Dict, Any
from src.services.bedrock_service import BedrockService
import json

class ComplexityAnalyzerAgent:
    """
    Specialized agent for analyzing computational complexity.
    Uses Nova Pro with structured reasoning.
    """
    
    def __init__(self, bedrock_service: BedrockService):
        self.bedrock = bedrock_service
        self.agent_name = "Complexity Analyzer"
        
        self.system_prompt = """You are a Complexity Analyzer Agent, an expert in computational complexity theory.

Your role:
- Analyze optimization problems to determine their computational complexity class
- Identify problem characteristics (variables, constraints, structure)
- Classify problems (P, NP, NP-Hard, NP-Complete, PSPACE, etc.)
- Assess scalability and computational requirements

Think step-by-step and provide detailed analysis with confidence scores.

Output your analysis as JSON with this structure:
{
    "complexity_class": "NP-Hard" | "NP-Complete" | "Polynomial" | "Exponential",
    "time_complexity": "O(...)",
    "space_complexity": "O(...)",
    "problem_size": "small" | "medium" | "large",
    "variable_count": <number>,
    "constraint_count": <number>,
    "is_combinatorial": true/false,
    "scalability": "excellent" | "good" | "poor",
    "quantum_advantage_potential": "high" | "medium" | "low",
    "reasoning": "detailed explanation",
    "confidence": 0.0-1.0
}"""
    
    def analyze(self, problem: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze problem complexity"""
        
        user_message = f"""Analyze the computational complexity of this optimization problem:

Problem Type: {problem.get('problem_type')}
Subtype: {problem.get('subtype')}
Description: {problem.get('description')}
Parameters: {json.dumps(problem.get('parameters', {}), indent=2)}
Constraints: {json.dumps(problem.get('constraints', {}), indent=2)}

Provide a comprehensive complexity analysis."""

        try:
            response = self.bedrock.invoke_with_system_prompt(
                system_prompt=self.system_prompt,
                user_message=user_message,
                temperature=0.3  # Lower temp for analytical tasks
            )
            
            # Parse JSON response
            response_clean = response.strip()
            if response_clean.startswith("```json"):
                response_clean = response_clean.split("```json")[1].split("```")[0]
            elif response_clean.startswith("```"):
                response_clean = response_clean.split("```")[1].split("```")[0]
            
            analysis = json.loads(response_clean)
            analysis['agent'] = self.agent_name
            
            return analysis
            
        except json.JSONDecodeError as e:
            print(f"Error parsing complexity analysis: {e}")
            return self._fallback_analysis(problem)
    
    def _fallback_analysis(self, problem: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback heuristic analysis"""
        params = problem.get('parameters', {})
        size = params.get('num_assets', params.get('num_molecules', 10))
        
        return {
            "agent": self.agent_name,
            "complexity_class": "NP-Hard",
            "time_complexity": "O(2^n)",
            "space_complexity": "O(n)",
            "problem_size": "medium" if size < 50 else "large",
            "variable_count": size,
            "constraint_count": len(problem.get('constraints', {})),
            "is_combinatorial": True,
            "scalability": "poor",
            "quantum_advantage_potential": "medium",
            "reasoning": "Heuristic analysis based on problem size",
            "confidence": 0.6
        }