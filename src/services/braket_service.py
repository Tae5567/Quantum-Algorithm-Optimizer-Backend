import boto3
from braket.aws import AwsDevice
from braket.circuits import Circuit
from typing import Dict, Any, List
from src.config import settings

class BraketService:
    """Service for AWS Braket quantum computing operations"""
    
    def __init__(self):
        self.s3_bucket = settings.braket_s3_bucket
        self.s3_prefix = "quantum-optimizer"
        
        # Initialize Braket client
        self.braket_client = boto3.client(
            'braket',
            region_name=settings.braket_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key
        )
    
    def get_available_devices(self) -> Dict[str, Any]:
        """Get available quantum devices"""
        try:
            response = self.braket_client.search_devices(
                filters=[
                    {
                        'name': 'deviceType',
                        'values': ['QPU', 'SIMULATOR']
                    }
                ]
            )
            
            devices = []
            for device in response.get('devices', []):
                devices.append({
                    'arn': device['deviceArn'],
                    'name': device['deviceName'],
                    'type': device['deviceType'],
                    'status': device['deviceStatus'],
                    'provider': device.get('providerName', 'AWS')
                })
            
            return {'devices': devices, 'count': len(devices)}
            
        except Exception as e:
            print(f"Error fetching devices: {str(e)}")
            # Return default simulator info if API fails
            return {
                'devices': [
                    {
                        'arn': 'arn:aws:braket:::device/quantum-simulator/amazon/sv1',
                        'name': 'SV1',
                        'type': 'SIMULATOR',
                        'status': 'ONLINE',
                        'provider': 'Amazon Braket'
                    }
                ],
                'count': 1,
                'note': 'Showing default simulator - API call failed'
            }
    
    def create_qaoa_circuit(self, num_qubits: int, layers: int = 1) -> Circuit:
        """Create a QAOA circuit for optimization problems"""
        
        if num_qubits > 34:
            raise ValueError("SV1 simulator supports maximum 34 qubits")
        
        circuit = Circuit()
        
        # Initial Hadamard layer (superposition)
        for qubit in range(num_qubits):
            circuit.h(qubit)
        
        # QAOA layers
        for layer in range(layers):
            # Problem Hamiltonian (ZZ interactions)
            for i in range(num_qubits):
                for j in range(i + 1, num_qubits):
                    circuit.zz(i, j, angle=0.5)
            
            # Mixer Hamiltonian (X rotations)
            for qubit in range(num_qubits):
                circuit.rx(qubit, angle=0.3)
        
        return circuit
    
    def estimate_quantum_resources(self, problem_params: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate quantum resources needed for a problem"""
        
        # Extract problem size from parameters
        num_vars = problem_params.get(
            'num_assets',
            problem_params.get('num_molecules', 
            problem_params.get('num_cities',
            problem_params.get('num_nodes', 10)))
        )
        
        # Estimate qubits needed (usually 1 qubit per variable)
        num_qubits = num_vars
        
        # Estimate QAOA layers based on problem size
        qaoa_layers = min(3, max(1, num_vars // 10))
        
        # Estimate circuit depth (gates per layer * layers)
        # QAOA: H gates + ZZ gates + RX gates per layer
        gates_per_layer = num_qubits + (num_qubits * (num_qubits - 1) // 2) + num_qubits
        circuit_depth = qaoa_layers * gates_per_layer
        
        # Estimate total gate count
        gate_count = circuit_depth + num_qubits  # +initial H layer
        
        # Check feasibility (SV1 limit is 34 qubits)
        feasible = num_qubits <= 34
        
        # Recommend device
        if num_qubits <= 11:
            recommended_device = 'qpu'  # Could use real QPU
        elif num_qubits <= 34:
            recommended_device = 'simulator'  # Use SV1
        else:
            recommended_device = 'none'  # Too large
        
        return {
            'required_qubits': num_qubits,
            'circuit_depth': circuit_depth,
            'estimated_gates': gate_count,
            'qaoa_layers': qaoa_layers,
            'feasible': feasible,
            'recommended_device': recommended_device,
            'max_simulator_qubits': 34,
            'notes': self._get_feasibility_notes(num_qubits, feasible)
        }
    
    def _get_feasibility_notes(self, num_qubits: int, feasible: bool) -> List[str]:
        """Get notes about feasibility"""
        notes = []
        
        if num_qubits <= 11:
            notes.append("Problem size suitable for real quantum hardware (QPU)")
        elif num_qubits <= 34:
            notes.append("Problem requires simulator (SV1) - too large for current QPUs")
        else:
            notes.append(f"Problem requires {num_qubits} qubits - exceeds SV1 limit of 34")
            notes.append("Consider problem decomposition or classical approach")
        
        if feasible:
            notes.append("Ready for quantum simulation")
        else:
            notes.append("Not feasible with current quantum hardware")
        
        return notes
    
    def run_simulation(
        self, 
        circuit: Circuit, 
        shots: int = 100,
        device_arn: str = None
    ) -> Dict[str, Any]:
        """Run quantum circuit simulation on AWS Braket"""
        
        if device_arn is None:
            # Default to SV1 simulator
            device_arn = "arn:aws:braket:::device/quantum-simulator/amazon/sv1"
        
        try:
            # Initialize device
            device = AwsDevice(device_arn)
            
            # Submit task
            task = device.run(
                circuit, 
                shots=shots,
                s3_destination_folder=(self.s3_bucket, self.s3_prefix)
            )
            
            # Wait for result
            result = task.result()
            
            # Process measurements
            measurements = result.measurements
            counts = {}
            for measurement in measurements:
                bitstring = ''.join(map(str, measurement))
                counts[bitstring] = counts.get(bitstring, 0) + 1
            
            # Get most common result
            most_common = max(counts.items(), key=lambda x: x[1]) if counts else (None, 0)
            
            return {
                'success': True,
                'measurements': counts,
                'total_shots': shots,
                'most_common_result': most_common[0],
                'most_common_count': most_common[1],
                'task_arn': task.id,
                'device': device_arn.split('/')[-1]
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'note': 'Simulation failed - this is normal if AWS Braket is not fully configured'
            }
    
    def estimate_cost(
        self, 
        num_qubits: int, 
        shots: int = 1000,
        device_type: str = 'simulator'
    ) -> Dict[str, Any]:
        """Estimate cost for quantum computation"""
        
        if device_type == 'simulator':
            # SV1 pricing: $0.075 per minute
            # Estimate: 2^n complexity for state vector
            runtime_seconds = (2 ** num_qubits) / 1000000  # rough estimate
            runtime_minutes = runtime_seconds / 60
            cost = runtime_minutes * 0.075
            
            return {
                'device_type': 'AWS Braket SV1 Simulator',
                'estimated_cost_usd': round(cost, 4),
                'runtime_minutes': round(runtime_minutes, 2),
                'shots': shots,
                'pricing_per_minute': 0.075
            }
        else:
            # QPU pricing varies by provider
            # Rough estimate: $0.30 per task + $0.01 per shot
            task_cost = 0.30
            shot_cost = 0.01 * shots
            total_cost = task_cost + shot_cost
            
            return {
                'device_type': 'Quantum Processing Unit (QPU)',
                'estimated_cost_usd': round(total_cost, 2),
                'task_fee': task_cost,
                'shot_cost': round(shot_cost, 2),
                'shots': shots,
                'note': 'Actual cost varies by QPU provider'
            }