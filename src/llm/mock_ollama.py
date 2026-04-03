"""
Mock Ollama Service - For development without Docker
"""

class MockOllama:
    def __init__(self, model="llama3.1:8b", base_url="http://localhost:11434"):
        self.model = model
        print(f"[MOCK OLLAMA] Initialized with model: {model}")
    
    def generate(self, prompt, system=None):
        print(f"[MOCK OLLAMA] Generating response for prompt: {prompt[:50]}...")
        
        # Mock responses based on prompt content
        prompt_lower = prompt.lower()
        
        if "user story" in prompt_lower or "requirement" in prompt_lower:
            return """
            **User Story:** As a user, I want the requested feature so that I can achieve my goal.
            
            **Acceptance Criteria:**
            1. Feature works as expected
            2. Edge cases handled
            3. Documentation updated
            4. Tests pass
            
            **Priority:** Medium
            **Estimate:** 3 story points
            """
        elif "gap" in prompt_lower or "missing" in prompt_lower:
            return """
            **Gap Analysis Results:**
            
            **Current State:** The requested functionality is not fully implemented
            **Desired State:** Complete solution meeting all requirements
            **Identified Gaps:** Implementation, Documentation, Testing
            **Recommendations:** Prioritize development, create test suite, update docs
            """
        else:
            return f"""
            I understand you're asking about: {prompt[:100]}
            
            As a Business Analyst, I recommend:
            1. Clarifying requirements with stakeholders
            2. Documenting the current process
            3. Identifying improvement opportunities
            4. Creating an implementation plan
            
            Would you like me to elaborate on any of these points?
            """
    
    def stream(self, prompt, system=None):
        yield self.generate(prompt, system)

def OllamaLLM(model="llama3.1:8b", base_url="http://localhost:11434"):
    return MockOllama(model, base_url)

print("✅ Mock Ollama loaded (Docker not required)")
