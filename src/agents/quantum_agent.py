"""
Quantum Feasibility Agent (Nova Pro + Braket API)

Checks qubit requirements
Validates circuit depth
Assesses hardware availability
"""

from typing import Dict, Any
from src.services.bedrock_service import BedrockService
from src.services.braket_service import BraketService
import json

class QuantumFeasibilityAgent:
    """
    Specialized agent for quantum hardware feasibility.
    Checks quantum resource requirements and availability.
    """
    
    def __init__(self, bedrock_service: BedrockService, braket_service: BraketService):
        self.bedrock = bedrock_service
        self.braket = braket_service
        self.agent_name = "Quantum Feasibility"
        
        self.system_prompt = """You are a Quantum Feasibility Agent, an expert in quantum computing hardware and algorithms.

Your role:
- Assess quantum algorithm suitability for problems
- Calculate qubit requirements
- Estimate circuit depth and gate counts
- Evaluate hardware availability and constraints

Output as JSON:
{
    "algorithm_recommendation": "QAOA" | "VQE" | "Grover" | "Quantum Annealing",
    "qubit_requirements": <number>,
    "circuit_depth": <number>,
    "gate_count": <number>,
    "is_feasible": true/false,
    "hardware_availability": "simulator" | "qpu" | "both",
    "limitations": ["list of limitations"],
    "advantages": ["list of advantages"],
    "reasoning": "detailed explanation",
    "confidence": 0.0-1.0
}"""
    
    def assess_feasibility(
        self,
        problem: Dict[str, Any],
        complexity_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess quantum feasibility"""
        
        # First check available devices
        devices = self.braket.get_available_devices()
        
        user_message = f"""Assess quantum computing feasibility for this problem:

Problem: {problem.get('description')}
Problem Type: {problem.get('problem_type')}
Parameters: {json.dumps(problem.get('parameters', {}), indent=2)}

Complexity Analysis:
- Complexity Class: {complexity_analysis.get('complexity_class')}
- Variable Count: {complexity_analysis.get('variable_count')}
- Is Combinatorial: {complexity_analysis.get('is_combinatorial')}
- Quantum Advantage Potential: {complexity_analysis.get('quantum_advantage_potential')}

Available Quantum Devices:
{json.dumps(devices, indent=2)}

Determine if quantum computing is feasible and which algorithm to use."""

        try:
            response = self.bedrock.invoke_with_system_prompt(
                system_prompt=self.system_prompt,
                user_message=user_message,
                temperature=0.3
            )
            
            # Parse JSON
            response_clean = response.strip()
            if response_clean.startswith("```json"):
                response_clean = response_clean.split("```json")[1].split("```")[0]
            elif response_clean.startswith("```"):
                response_clean = response_clean.split("```")[1].split("```")[0]
            
            feasibility = json.loads(response_clean)
            feasibility['agent'] = self.agent_name
            feasibility['available_devices'] = devices
            
            return feasibility
            
        except json.JSONDecodeError:
            return self._fallback_feasibility(problem, complexity_analysis, devices)
    
    def _fallback_feasibility(
        self,
        problem: Dict[str, Any],
        complexity_analysis: Dict[str, Any],
        devices: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fallback feasibility assessment"""
        
        num_vars = complexity_analysis.get('variable_count', 10)
        is_feasible = num_vars <= 34  # SV1 limit
        
        return {
            "agent": self.agent_name,
            "algorithm_recommendation": "QAOA",
            "qubit_requirements": num_vars,
            "circuit_depth": num_vars * 10,
            "gate_count": num_vars * 50,
            "is_feasible": is_feasible,
            "hardware_availability": "simulator",
            "limitations": [
                "Limited to 34 qubits on simulator",
                "No noise modeling in ideal simulation"
            ],
            "advantages": [
                "Potential speedup for combinatorial problems",
                "Scalable to larger problems"
            ],
            "reasoning": "Heuristic assessment based on qubit requirements",
            "confidence": 0.7,
            "available_devices": devices
        }