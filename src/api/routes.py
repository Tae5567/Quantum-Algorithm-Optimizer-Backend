from fastapi import APIRouter, HTTPException
from src.models import OptimizationProblem, SimulationRequest
from src.agents.orchestrator import AgentOrchestrator
from typing import Dict, Any

router = APIRouter()

# Initialize orchestrator (single instance)
orchestrator = AgentOrchestrator()

@router.post("/analyze/multi-agent", response_model=Dict[str, Any])
async def multi_agent_analysis(request: SimulationRequest):
    """
    Run full multi-agent analysis pipeline.
    
    This endpoint coordinates 4 specialist AI agents:
    1. Complexity Analyzer - Analyzes computational complexity
    2. Cost Estimator - Calculates classical vs quantum costs
    3. Quantum Feasibility - Assesses quantum hardware requirements
    4. Decision Maker - Synthesizes inputs and makes final recommendation
    """
    try:
        result = await orchestrator.analyze_problem(request.problem.dict())
        
        return {
            'success': True,
            'data': result,
            'message': 'Multi-agent analysis completed successfully'
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Multi-agent analysis failed: {str(e)}"
        )

@router.post("/analyze/agent/{agent_name}")
async def single_agent_analysis(
    agent_name: str,
    problem: OptimizationProblem
):
    """
    Query a specific agent directly (for debugging/education).
    
    Available agents:
    - complexity: Complexity Analyzer Agent
    - cost: Cost Estimator Agent
    - quantum: Quantum Feasibility Agent
    - decision: Decision Agent (requires other agent outputs)
    """
    try:
        if agent_name == 'complexity':
            agent = orchestrator.complexity_agent
            result = agent.analyze(problem.dict())
            
        elif agent_name == 'cost':
            # Need complexity first
            complexity = orchestrator.complexity_agent.analyze(problem.dict())
            agent = orchestrator.cost_agent
            result = agent.estimate_costs(problem.dict(), complexity)
            
        elif agent_name == 'quantum':
            # Need complexity first
            complexity = orchestrator.complexity_agent.analyze(problem.dict())
            agent = orchestrator.quantum_agent
            result = agent.assess_feasibility(problem.dict(), complexity)
            
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Agent '{agent_name}' not found"
            )
        
        return {
            'success': True,
            'agent': agent_name,
            'data': result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Agent analysis failed: {str(e)}"
        )

@router.get("/agents/info")
async def get_agents_info():
    """Get information about all available agents"""
    
    agents_info = {
        'orchestrator': {
            'name': 'Agent Orchestrator',
            'role': 'Coordinates all specialist agents in multi-agent workflow',
            'capabilities': [
                'Workflow management',
                'Parallel agent execution',
                'Result aggregation'
            ]
        },
        'agents': {
            'complexity': {
                'name': 'Complexity Analyzer Agent',
                'role': 'Analyzes computational complexity and problem characteristics',
                'outputs': [
                    'Complexity class (NP-Hard, etc.)',
                    'Time/space complexity',
                    'Quantum advantage potential'
                ],
                'model': 'Amazon Nova Pro'
            },
            'cost': {
                'name': 'Cost Estimator Agent',
                'role': 'Calculates and compares classical vs quantum costs',
                'outputs': [
                    'Classical compute costs',
                    'Quantum compute costs',
                    'ROI analysis and recommendations'
                ],
                'model': 'Amazon Nova Pro'
            },
            'quantum': {
                'name': 'Quantum Feasibility Agent',
                'role': 'Assesses quantum hardware requirements and availability',
                'outputs': [
                    'Qubit requirements',
                    'Circuit depth estimates',
                    'Hardware feasibility',
                    'Algorithm recommendations'
                ],
                'model': 'Amazon Nova Pro + AWS Braket API'
            },
            'decision': {
                'name': 'Decision Agent',
                'role': 'Synthesizes all agent inputs to make final recommendation',
                'outputs': [
                    'Final algorithm recommendation',
                    'Confidence score',
                    'Detailed reasoning',
                    'Actionable next steps'
                ],
                'model': 'Amazon Nova Pro (Chain-of-Thought)'
            }
        },
        'workflow': {
            'steps': [
                '1. Complexity Agent analyzes problem',
                '2. Cost & Quantum agents run in parallel',
                '3. Decision Agent synthesizes all outputs',
                '4. Return comprehensive recommendation'
            ],
            'average_time': '15-30 seconds'
        }
    }
    
    return {
        'success': True,
        'data': agents_info
    }

@router.get("/health")
async def health_check():
    """Health check with agent status"""
    return {
        'status': 'healthy',
        'service': 'quantum-optimizer-multi-agent-system',
        'agents': {
            'complexity': 'active',
            'cost': 'active',
            'quantum': 'active',
            'decision': 'active'
        },
        'orchestrator': 'active'
    }

@router.post("/playground/run/{problem_id}")
async def run_playground_problem(problem_id: str):
    """Run multi-agent analysis on famous problems"""
    
    famous_problems = {
        'traveling_salesman': {
            'problem_type': 'financial',
            'subtype': 'portfolio_optimization',
            'description': 'Traveling Salesman Problem: Find shortest route visiting 20 cities',
            'parameters': {
                'num_cities': 20,
                'problem_variant': 'symmetric_tsp'
            },
            'constraints': {
                'visit_each_once': True
            }
        },
        'max_cut': {
            'problem_type': 'financial',
            'subtype': 'risk_analysis',
            'description': 'Maximum Cut Problem: Partition 30-node graph to maximize edge cuts',
            'parameters': {
                'num_nodes': 30,
                'edge_density': 0.5
            }
        },
        'protein_folding': {
            'problem_type': 'molecular',
            'subtype': 'protein_folding',
            'description': 'Protein Folding: Predict structure of 20-amino acid peptide',
            'parameters': {
                'num_amino_acids': 20,
                'force_field': 'CHARMM',
                'temperature': 300
            }
        }
    }
    
    if problem_id not in famous_problems:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    problem = famous_problems[problem_id]
    result = await orchestrator.analyze_problem(problem)
    
    return {
        'success': True,
        'problem_id': problem_id,
        'data': result
    }