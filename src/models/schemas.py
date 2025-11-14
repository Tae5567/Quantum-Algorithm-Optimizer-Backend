from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict, Any, List
from enum import Enum

class ProblemType(str, Enum):
    FINANCIAL = "financial"
    MOLECULAR = "molecular"

class OptimizationProblem(BaseModel):
    problem_type: ProblemType
    subtype: str
    description: str
    constraints: Optional[Dict[str, Any]] = None
    parameters: Dict[str, Any]
    
    class Config:
        json_schema_extra = {
            "example": {
                "problem_type": "financial",
                "subtype": "portfolio_optimization",
                "description": "Optimize portfolio allocation for 50 assets",
                "constraints": {
                    "max_position": 0.1,
                    "min_return": 0.08
                },
                "parameters": {
                    "num_assets": 50,
                    "risk_tolerance": 0.5
                }
            }
        }

class SimulationRequest(BaseModel):
    problem: OptimizationProblem
    run_simulation: bool = False