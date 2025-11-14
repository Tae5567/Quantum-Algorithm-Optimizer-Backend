"""
Orchestrator Agent (Bedrock Agent with Function Calling)

Coordinates all other agents
Manages conversation flow
Synthesizes final recommendation
"""

from typing import Dict, Any
from src.agents.complexity_agent import ComplexityAnalyzerAgent
from src.agents.cost_agent import CostEstimatorAgent
from src.agents.quantum_agent import QuantumFeasibilityAgent
from src.agents.decision_agent import DecisionAgent
from src.services.bedrock_service import BedrockService
from src.services.braket_service import BraketService
import time

class AgentOrchestrator:
    """
    Master orchestrator that coordinates all specialist agents.
    Implements multi-agent workflow with parallel execution where possible.
    """
    
    def __init__(self):
        # Initialize services
        self.bedrock_service = BedrockService()
        self.braket_service = BraketService()
        
        # Initialize specialist agents
        self.complexity_agent = ComplexityAnalyzerAgent(self.bedrock_service)
        self.cost_agent = CostEstimatorAgent(self.bedrock_service)
        self.quantum_agent = QuantumFeasibilityAgent(
            self.bedrock_service,
            self.braket_service
        )
        self.decision_agent = DecisionAgent(self.bedrock_service)
    
    async def analyze_problem(self, problem: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate multi-agent analysis workflow.
        
        Workflow:
        1. Complexity Agent analyzes problem
        2. Quantum Agent & Cost Agent run in parallel (depend on complexity)
        3. Decision Agent synthesizes all outputs
        """
        
        start_time = time.time()
        
        print(f"\n🤖 Starting multi-agent analysis...")
        print(f"📋 Problem: {problem.get('description')}")
        
        # Step 1: Complexity Analysis (sequential - required first)
        print("\n[1/4] 🧠 Complexity Agent analyzing...")
        complexity_analysis = self.complexity_agent.analyze(problem)
        print(f"  ✓ Complexity: {complexity_analysis.get('complexity_class')}")
        print(f"  ✓ Confidence: {complexity_analysis.get('confidence', 0):.2%}")
        
        # Step 2 & 3: Parallel execution (both depend on complexity)
        print("\n[2/4] 💰 Cost Agent estimating...")
        cost_analysis = self.cost_agent.estimate_costs(problem, complexity_analysis)
        print(f"  ✓ ROI Recommendation: {cost_analysis.get('roi_analysis', {}).get('recommendation')}")
        
        print("\n[3/4] ⚛️  Quantum Agent assessing feasibility...")
        feasibility_analysis = self.quantum_agent.assess_feasibility(
            problem,
            complexity_analysis
        )
        print(f"  ✓ Feasible: {feasibility_analysis.get('is_feasible')}")
        print(f"  ✓ Algorithm: {feasibility_analysis.get('algorithm_recommendation')}")
        
        # Step 4: Decision Making (sequential - synthesizes all inputs)
        print("\n[4/4] 🎯 Decision Agent making final recommendation...")
        final_decision = self.decision_agent.make_decision(
            problem,
            complexity_analysis,
            cost_analysis,
            feasibility_analysis
        )
        print(f"  ✓ Recommendation: {final_decision.get('final_recommendation').upper()}")
        print(f"  ✓ Confidence: {final_decision.get('confidence', 0):.2%}")
        
        total_time = time.time() - start_time
        
        # Compile comprehensive result
        result = {
            'problem': problem,
            'analysis': {
                'complexity': complexity_analysis,
                'cost': cost_analysis,
                'feasibility': feasibility_analysis,
                'decision': final_decision
            },
            'metadata': {
                'total_analysis_time': round(total_time, 2),
                'agents_involved': [
                    'Complexity Analyzer',
                    'Cost Estimator',
                    'Quantum Feasibility',
                    'Decision Maker'
                ],
                'workflow': 'multi-agent-orchestration'
            }
        }
        
        print(f"\n✅ Analysis complete in {total_time:.2f}s")
        print(f"🎯 Final Recommendation: {final_decision.get('final_recommendation').upper()}")
        
        return result