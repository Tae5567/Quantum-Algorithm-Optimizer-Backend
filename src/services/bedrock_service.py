import boto3
import json
from typing import Dict, Any, List
from src.config import settings

class BedrockService:
    """Enhanced Bedrock service for multi-agent communication"""
    
    def __init__(self):
        self.client = boto3.client(
            service_name='bedrock-runtime',
            region_name=settings.bedrock_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key
        )
        
        self.agent_client = boto3.client(
            service_name='bedrock-agent-runtime',
            region_name=settings.bedrock_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key
        )
        
        self.model_id = settings.bedrock_model_id
    
    def invoke_with_system_prompt(
        self, 
        system_prompt: str, 
        user_message: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """Invoke Nova with system prompt for agent behavior"""
        
        request_body = {
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": user_message}]
                }
            ],
            "system": [{"text": system_prompt}],
            "inferenceConfig": {
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "top_p": 0.9
            }
        }
        
        try:
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response['body'].read())
            
            if 'output' in response_body and 'message' in response_body['output']:
                content = response_body['output']['message']['content']
                if isinstance(content, list) and len(content) > 0:
                    return content[0].get('text', '')
            
            return ""
            
        except Exception as e:
            print(f"Error invoking Bedrock: {str(e)}")
            raise
    
    def invoke_with_tools(
        self,
        system_prompt: str,
        user_message: str,
        tools: List[Dict[str, Any]],
        max_iterations: int = 5
    ) -> Dict[str, Any]:
        """Invoke Nova with function calling for tool use"""
        
        messages = [{"role": "user", "content": [{"text": user_message}]}]
        
        for iteration in range(max_iterations):
            request_body = {
                "messages": messages,
                "system": [{"text": system_prompt}],
                "inferenceConfig": {
                    "max_new_tokens": 2000,
                    "temperature": 0.7
                },
                "toolConfig": {
                    "tools": tools
                }
            }
            
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response['body'].read())
            output_message = response_body['output']['message']
            messages.append(output_message)
            
            # Check if tool use is requested
            if 'stopReason' in response_body['output']:
                stop_reason = response_body['output']['stopReason']
                
                if stop_reason == 'tool_use':
                    # Process tool calls
                    tool_results = self._process_tool_calls(output_message)
                    messages.append({
                        "role": "user",
                        "content": tool_results
                    })
                    continue
                elif stop_reason == 'end_turn':
                    # Agent is done
                    return {
                        'response': output_message['content'][0]['text'],
                        'iterations': iteration + 1
                    }
        
        return {
            'response': messages[-1]['content'][0]['text'],
            'iterations': max_iterations
        }
    
    def _process_tool_calls(self, message: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process tool calls from agent response"""
        # This will be implemented by each agent
        return []