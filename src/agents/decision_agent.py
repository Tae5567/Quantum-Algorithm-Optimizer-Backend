"""
Decision Agent (Nova Pro with Chain-of-Thought)

Aggregates all agent inputs
Provides final recommendation with reasoning
Calculates confidence score
"""

from typing import Dict, Any
from src.services.bedrock_service import BedrockService
import json

class DecisionAgent:
    """
    Final decision-making agent that synthesizes all inputs.
    Uses chain-of-thought reasoning to make final recommendation.
    """
    
    def __init__(self, bedrock_service: BedrockService):
        self.bedrock = bedrock_service
        self.agent_name = "Decision Maker"
        
        self.system_prompt = """You are the Decision Agent, the final arbiter in a multi-agent system for algorithm recommendation.

Your role:
- Synthesize inputs from all specialist agents
- Weigh trade-offs between classical and quantum approaches
- Make a final, confident recommendation
- Provide clear, actionable reasoning

Consider:
1. Complexity analysis - Is the problem suitable for quantum?
2. Cost analysis - What's the ROI?
3. Feasibility - Is quantum hardware available and practical?
4. User context - What's best for their use case?

Output as JSON:
{
    "final_recommendation": "classical" | "quantum" | "hybrid",
    "confidence": 0.0-1.0,
    "primary_reasoning": "main reason for recommendation",
    "supporting_factors": ["list of supporting points"],
    "trade_offs": {
        "classical": {"pros": [...], "cons": [...]},
        "quantum": {"pros": [...], "cons": [...]}
    },
    "actionable_next_steps": ["what user should do"],
    "estimated_performance": {
        "speedup": <number>,
        "accuracy": "high" | "medium" | "low",
        "reliability": "high" | "medium" | "low"
    }
}"""
    
    def make_decision(
        self,
        problem: Dict[str, Any],
        complexity_analysis: Dict[str, Any],
        cost_analysis: Dict[str, Any],
        feasibility_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Make final recommendation based on all agent inputs"""
        
        user_message = f"""Make a final recommendation for this optimization problem.

PROBLEM:
{json.dumps(problem, indent=2)}

COMPLEXITY ANALYSIS (from Complexity Agent):
{json.dumps(complexity_analysis, indent=2)}

COST ANALYSIS (from Cost Agent):
{json.dumps(cost_analysis, indent=2)}

FEASIBILITY ANALYSIS (from Quantum Agent):
{json.dumps(feasibility_analysis, indent=2)}

Provide your final recommendation with detailed reasoning.
Think step-by-step through the decision process."""

        try:
            response = self.bedrock.invoke_with_system_prompt(
                system_prompt=self.system_prompt,
                user_message=user_message,
                temperature=0.5,
                max_tokens=3000
            )
            
            # Parse JSON
            response_clean = response.strip()
            if response_clean.startswith("```json"):
                response_clean = response_clean.split("```json")[1].split("```")[0]
            elif response_clean.startswith("```"):
                response_clean = response_clean.split("```")[1].split("```")[0]
            
            decision = json.loads(response_clean)
            decision['agent'] = self.agent_name
            
            # Add agent consensus metrics
            decision['agent_consensus'] = self._calculate_consensus(
                complexity_analysis,
                cost_analysis,
                feasibility_analysis
            )
            
            return decision
            
        except json.JSONDecodeError:
            return self._fallback_decision(
                complexity_analysis,
                cost_analysis,
                feasibility_analysis
            )
    
    def _calculate_consensus(
        self,
        complexity: Dict[str, Any],
        cost: Dict[str, Any],
        feasibility: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate agreement between agents"""
        
        # Simple voting mechanism
        votes = {
            'quantum': 0,
            'classical': 0
        }
        
        if complexity.get('quantum_advantage_potential') == 'high':
            votes['quantum'] += 1
        
        if cost.get('roi_analysis', {}).get('recommendation') == 'quantum':
            votes['quantum'] += 1
        else:
            votes['classical'] += 1
        
        if feasibility.get('is_feasible'):
            votes['quantum'] += 1
        else:
            votes['classical'] += 1
        
        total_votes = sum(votes.values())
        
        return {
            'votes': votes,
            'agreement_score': max(votes.values()) / total_votes if total_votes > 0 else 0,
            'majority': 'quantum' if votes['quantum'] > votes['classical'] else 'classical'
        }
    
    def _fallback_decision(
        self,
        complexity: Dict[str, Any],
        cost: Dict[str, Any],
        feasibility: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fallback decision logic"""
        
        consensus = self._calculate_consensus(complexity, cost, feasibility)
        recommendation = consensus['majority']
        
        return {
            "agent": self.agent_name,
            "final_recommendation": recommendation,
            "confidence": consensus['agreement_score'],
            "primary_reasoning": f"Based on majority vote from specialist agents: {consensus['votes']}",
            "supporting_factors": [
                f"Complexity agent: {complexity.get('quantum_advantage_potential')} quantum potential",
                f"Cost agent: {cost.get('roi_analysis', {}).get('recommendation')} recommended",
                f"Feasibility: {'Feasible' if feasibility.get('is_feasible') else 'Not feasible'}"
            ],
            "trade_offs": {
                "classical": {
                    "pros": ["Reliable", "Well-established"],
                    "cons": ["May be slower"]
                },
                "quantum": {
                    "pros": ["Potential speedup"],
                    "cons": ["Hardware constraints"]
                }
            },
            "actionable_next_steps": [
                f"Use {recommendation} algorithm",
                "Run comparative benchmarks",
                "Monitor performance metrics"
            ],
            "agent_consensus": consensus
        }