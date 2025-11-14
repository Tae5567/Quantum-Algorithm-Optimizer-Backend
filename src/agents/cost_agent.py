"""
Cost Estimator Agent (Nova Pro)

Calculates classical compute costs
Calculates quantum compute costs
Provides ROI analysis
"""

from typing import Dict, Any
from src.services.bedrock_service import BedrockService
import json

class CostEstimatorAgent:
    """
    Specialized agent for cost-benefit analysis.
    Calculates and compares classical vs quantum costs.
    """
    
    def __init__(self, bedrock_service: BedrockService):
        self.bedrock = bedrock_service
        self.agent_name = "Cost Estimator"
        
        # AWS pricing (approximate)
        self.pricing = {
            'ec2': {
                'small': 0.096,    # t3.large per hour
                'medium': 0.768,   # c5.4xlarge per hour
                'large': 3.072     # c5.18xlarge per hour
            },
            'braket': {
                'simulator_sv1': 0.075,  # per minute
                'simulator_dm1': 0.075,
                'simulator_tn1': 0.275
            },
            's3': 0.023  # per GB per month
        }
        
        self.system_prompt = """You are a Cost Estimation Agent, an expert in cloud computing costs and ROI analysis.

Your role:
- Estimate computational costs for classical algorithms
- Estimate quantum computing costs
- Calculate ROI and cost savings
- Provide break-even analysis

Use the provided pricing data and problem characteristics to make accurate estimates.

Output as JSON:
{
    "classical_cost": {
        "compute_hours": <number>,
        "hourly_rate": <number>,
        "total_cost": <number>,
        "instance_type": "string"
    },
    "quantum_cost": {
        "runtime_minutes": <number>,
        "per_minute_rate": <number>,
        "total_cost": <number>,
        "device_type": "string"
    },
    "roi_analysis": {
        "cost_savings": <number>,
        "savings_percentage": <number>,
        "breakeven_runs": <number>,
        "recommendation": "classical" | "quantum"
    },
    "reasoning": "detailed explanation",
    "confidence": 0.0-1.0
}"""
    
    def estimate_costs(
        self, 
        problem: Dict[str, Any],
        complexity_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Estimate costs based on problem and complexity"""
        
        user_message = f"""Estimate the computational costs for this problem:

Problem: {problem.get('description')}
Parameters: {json.dumps(problem.get('parameters', {}), indent=2)}

Complexity Analysis:
- Complexity Class: {complexity_analysis.get('complexity_class')}
- Time Complexity: {complexity_analysis.get('time_complexity')}
- Problem Size: {complexity_analysis.get('problem_size')}
- Variable Count: {complexity_analysis.get('variable_count')}

Pricing Information:
{json.dumps(self.pricing, indent=2)}

Provide detailed cost estimates for both classical and quantum approaches."""

        try:
            response = self.bedrock.invoke_with_system_prompt(
                system_prompt=self.system_prompt,
                user_message=user_message,
                temperature=0.2  # Very low temp for numerical tasks
            )
            
            # Parse JSON
            response_clean = response.strip()
            if response_clean.startswith("```json"):
                response_clean = response_clean.split("```json")[1].split("```")[0]
            elif response_clean.startswith("```"):
                response_clean = response_clean.split("```")[1].split("```")[0]
            
            cost_analysis = json.loads(response_clean)
            cost_analysis['agent'] = self.agent_name
            
            return cost_analysis
            
        except json.JSONDecodeError:
            return self._fallback_cost_estimate(problem, complexity_analysis)
    
    def _fallback_cost_estimate(
        self,
        problem: Dict[str, Any],
        complexity_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fallback cost calculation"""
        
        problem_size = complexity_analysis.get('problem_size', 'medium')
        compute_hours = {'small': 0.5, 'medium': 2.0, 'large': 8.0}[problem_size]
        
        classical_cost = compute_hours * self.pricing['ec2'][problem_size]
        quantum_minutes = compute_hours * 60 / 3  # Assume 3x speedup
        quantum_cost = quantum_minutes * self.pricing['braket']['simulator_sv1']
        
        savings = classical_cost - quantum_cost
        
        return {
            "agent": self.agent_name,
            "classical_cost": {
                "compute_hours": compute_hours,
                "hourly_rate": self.pricing['ec2'][problem_size],
                "total_cost": round(classical_cost, 2),
                "instance_type": f"EC2 {problem_size}"
            },
            "quantum_cost": {
                "runtime_minutes": round(quantum_minutes, 2),
                "per_minute_rate": self.pricing['braket']['simulator_sv1'],
                "total_cost": round(quantum_cost, 2),
                "device_type": "AWS Braket SV1"
            },
            "roi_analysis": {
                "cost_savings": round(savings, 2),
                "savings_percentage": round((savings / classical_cost * 100), 1),
                "breakeven_runs": 1,
                "recommendation": "quantum" if savings > 0 else "classical"
            },
            "reasoning": "Heuristic cost calculation based on problem size",
            "confidence": 0.7
        }