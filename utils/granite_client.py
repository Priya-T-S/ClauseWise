"""
IBM Granite Model Client for ClauseWise
Supports both IBM watsonx.ai and HuggingFace implementations
"""

import os
from typing import Optional, Dict, List
from dataclasses import dataclass

@dataclass
class GraniteConfig:
    """Configuration for Granite model"""
    model_id: str = "ibm/granite-13b-instruct-v2"
    max_tokens: int = 1024
    temperature: float = 0.1
    top_p: float = 0.95
    use_watsonx: bool = False  # Use HuggingFace by default for hackathon

class GraniteClient:
    """Client for IBM Granite models"""
    
    def __init__(self, config: Optional[GraniteConfig] = None):
        self.config = config or GraniteConfig()
        self.model = None
        self.tokenizer = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the Granite model based on configuration"""
        if self.config.use_watsonx:
            self._init_watsonx()
        else:
            self._init_huggingface()
    
    def _init_watsonx(self):
        """Initialize IBM watsonx.ai model"""
        try:
            from ibm_watsonx_ai.foundation_models import Model
            from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
            
            api_key = os.getenv("IBM_WATSONX_API_KEY")
            project_id = os.getenv("IBM_WATSONX_PROJECT_ID")
            
            if not api_key or not project_id:
                print("Warning: IBM watsonx credentials not found. Falling back to HuggingFace.")
                self._init_huggingface()
                return
            
            params = {
                GenParams.MAX_NEW_TOKENS: self.config.max_tokens,
                GenParams.TEMPERATURE: self.config.temperature,
                GenParams.TOP_P: self.config.top_p,
            }
            
            self.model = Model(
                model_id=self.config.model_id,
                params=params,
                credentials={
                    "apikey": api_key,
                    "url": "https://us-south.ml.cloud.ibm.com"
                },
                project_id=project_id
            )
            print(f"✓ Initialized IBM watsonx model: {self.config.model_id}")
        except Exception as e:
            print(f"Error initializing watsonx: {e}")
            print("Falling back to HuggingFace implementation")
            self._init_huggingface()
    
    def _init_huggingface(self):
        """Initialize HuggingFace model (fallback or default)"""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch
            
            # Use smaller Granite model or alternative for hackathon
            model_name = "ibm-granite/granite-3b-code-instruct"  # Smaller model
            
            print(f"Loading model from HuggingFace: {model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None,
                low_cpu_mem_usage=True
            )
            
            if not torch.cuda.is_available():
                print("Warning: CUDA not available. Using CPU (slower performance)")
            
            print(f"✓ Initialized HuggingFace model: {model_name}")
            self.config.use_watsonx = False
        except Exception as e:
            print(f"Error initializing HuggingFace model: {e}")
            raise
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text using Granite model"""
        try:
            if self.config.use_watsonx:
                return self._generate_watsonx(prompt, system_prompt)
            else:
                return self._generate_huggingface(prompt, system_prompt)
        except Exception as e:
            print(f"Error generating text: {e}")
            return f"Error: {str(e)}"
    
    def _generate_watsonx(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate using watsonx.ai"""
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        response = self.model.generate_text(prompt=full_prompt)
        return response
    
    def _generate_huggingface(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate using HuggingFace model"""
        import torch
        
        # Format prompt for Granite instruct models
        if system_prompt:
            formatted_prompt = f"System: {system_prompt}\n\nUser: {prompt}\n\nAssistant:"
        else:
            formatted_prompt = f"User: {prompt}\n\nAssistant:"
        
        inputs = self.tokenizer(formatted_prompt, return_tensors="pt")
        if torch.cuda.is_available():
            inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                top_p=self.config.top_p,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the assistant's response
        if "Assistant:" in response:
            response = response.split("Assistant:")[-1].strip()
        
        return response
    
    def batch_generate(self, prompts: List[str], system_prompt: Optional[str] = None) -> List[str]:
        """Generate multiple responses"""
        return [self.generate(prompt, system_prompt) for prompt in prompts]


# Singleton instance
_granite_client = None

def get_granite_client(config: Optional[GraniteConfig] = None) -> GraniteClient:
    """Get or create Granite client singleton"""
    global _granite_client
    if _granite_client is None:
        _granite_client = GraniteClient(config)
    return _granite_client