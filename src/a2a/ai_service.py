"""AI Service for intelligent analysis"""
import os
import httpx
import json
from typing import Dict, Any, List, Optional
import structlog
from dotenv import load_dotenv

load_dotenv()
logger = structlog.get_logger(__name__)


class AIService:
    """Service for AI-powered analysis"""
    
    def __init__(self):
        self.provider = os.getenv('AI_PROVIDER', 'google')
        self.google_key = os.getenv('GOOGLE_AI_API_KEY')
        
        self.enable_ai = os.getenv('ENABLE_AI_ANALYSIS', 'false').lower() == 'true'
        
        if self.enable_ai and not self.google_key:
            logger.warning("AI analysis enabled but Google AI API key not provided")
    
    async def analyze_project_requirements(self, mission: str) -> Dict[str, Any]:
        """AI-powered analysis of project requirements"""
        if not self.enable_ai:
            return self._fallback_analysis(mission)
        
        prompt = f"""
        Analyze this project mission and provide detailed insights:
        
        Mission: {mission}
        
        Please provide analysis in this JSON format:
        {{
            "complexity": "simple|medium|complex|enterprise",
            "estimated_weeks": number,
            "key_technologies": ["tech1", "tech2"],
            "required_skills": ["skill1", "skill2"],
            "project_type": "web|mobile|desktop|ai|data",
            "priority_phases": ["phase1", "phase2"],
            "risk_factors": ["risk1", "risk2"],
            "recommended_team_size": number,
            "budget_category": "small|medium|large|enterprise"
        }}
        """
        
        try:
            if self.provider == 'google' and self.google_key:
                return await self._call_google(prompt)
            else:
                logger.warning(f"AI provider {self.provider} not configured")
                return self._fallback_analysis(mission)
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return self._fallback_analysis(mission)
    
    async def generate_smart_milestones(self, mission: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate intelligent milestone planning"""
        if not self.enable_ai:
            return self._fallback_milestones(analysis)
        
        prompt = f"""
        Create detailed milestone plan for this project:
        
        Mission: {mission}
        Analysis: {json.dumps(analysis, indent=2)}
        
        Generate realistic milestones with specific deliverables in JSON format:
        {{
            "milestones": [
                {{
                    "name": "milestone name",
                    "description": "detailed description",
                    "duration_weeks": number,
                    "deliverables": ["deliverable1", "deliverable2"],
                    "dependencies": ["dependency1"],
                    "critical_path": true/false
                }}
            ]
        }}
        """
        
        try:
            if self.provider == 'google' and self.google_key:
                result = await self._call_google(prompt)
                return result.get('milestones', [])
            else:
                return self._fallback_milestones(analysis)
        except Exception as e:
            logger.error(f"Smart milestone generation failed: {e}")
            return self._fallback_milestones(analysis)
    
    async def estimate_task_complexity(self, task_description: str, context: str) -> Dict[str, Any]:
        """AI-powered task complexity estimation"""
        if not self.enable_ai:
            return {"hours": 8, "difficulty": "medium", "skills": ["development"]}
        
        prompt = f"""
        Estimate complexity for this task:
        
        Task: {task_description}
        Context: {context}
        
        Provide estimation in JSON format:
        {{
            "estimated_hours": number,
            "difficulty": "easy|medium|hard|expert",
            "required_skills": ["skill1", "skill2"],
            "dependencies": ["dep1", "dep2"],
            "risk_level": "low|medium|high",
            "recommendations": ["rec1", "rec2"]
        }}
        """
        
        try:
            return await self._call_ai_provider(prompt)
        except Exception as e:
            logger.error(f"Task estimation failed: {e}")
            return {"hours": 8, "difficulty": "medium", "skills": ["development"]}
    
    async def _call_openai(self, prompt: str) -> Dict[str, Any]:
        """Call OpenAI API"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openai_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": os.getenv('OPENAI_MODEL', 'gpt-4o'),
                    "messages": [
                        {"role": "system", "content": "You are an expert project manager and technical analyst. Always respond with valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": int(os.getenv('OPENAI_MAX_TOKENS', '4000')),
                    "temperature": float(os.getenv('OPENAI_TEMPERATURE', '0.7'))
                },
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            
            content = result['choices'][0]['message']['content']
            
            # Try to parse JSON from response
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # Extract JSON from markdown code blocks
                if '```json' in content:
                    json_start = content.find('```json') + 7
                    json_end = content.find('```', json_start)
                    json_str = content[json_start:json_end].strip()
                    return json.loads(json_str)
                raise
    
    async def _call_google(self, prompt: str) -> Dict[str, Any]:
        """Call Google Gemini 2.0 Flash API"""
        model = os.getenv('GOOGLE_MODEL', 'gemini-2.0-flash-exp')
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        
        # Enhanced prompt for better JSON response
        enhanced_prompt = f"""
{prompt}

IMPORTANT: Respond ONLY with valid JSON. Do not include any explanation or markdown formatting.
Ensure the response is a properly formatted JSON object that can be parsed directly.
"""
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{api_url}?key={self.google_key}",
                    json={
                        "contents": [{
                            "parts": [{"text": enhanced_prompt}]
                        }],
                        "generationConfig": {
                            "maxOutputTokens": int(os.getenv('GOOGLE_MAX_TOKENS', '8000')),
                            "temperature": float(os.getenv('GOOGLE_TEMPERATURE', '0.7')),
                            "candidateCount": 1,
                            "stopSequences": [],
                            "topK": 40,
                            "topP": 0.95
                        },
                        "safetySettings": [
                            {
                                "category": "HARM_CATEGORY_HARASSMENT",
                                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                            },
                            {
                                "category": "HARM_CATEGORY_HATE_SPEECH", 
                                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                            },
                            {
                                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                            },
                            {
                                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                            }
                        ]
                    },
                    headers={
                        "Content-Type": "application/json"
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()
                
                if 'candidates' not in result or len(result['candidates']) == 0:
                    raise ValueError("No candidates in Gemini response")
                
                content = result['candidates'][0]['content']['parts'][0]['text']
                
                # Clean up the response and extract JSON
                content = content.strip()
                
                # Try to parse JSON directly
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    # Try to extract JSON from markdown code blocks
                    if '```json' in content:
                        json_start = content.find('```json') + 7
                        json_end = content.find('```', json_start)
                        json_str = content[json_start:json_end].strip()
                        return json.loads(json_str)
                    elif '```' in content:
                        # Handle generic code blocks
                        json_start = content.find('```') + 3
                        json_end = content.find('```', json_start)
                        json_str = content[json_start:json_end].strip()
                        return json.loads(json_str)
                    else:
                        # Try to find JSON-like content
                        import re
                        json_match = re.search(r'\{.*\}', content, re.DOTALL)
                        if json_match:
                            return json.loads(json_match.group())
                        raise ValueError(f"Could not extract valid JSON from Gemini response: {content}")
                        
            except httpx.HTTPStatusError as e:
                logger.error(f"Gemini API HTTP error: {e.response.status_code} - {e.response.text}")
                raise
            except Exception as e:
                logger.error(f"Gemini API call failed: {e}")
                raise
    
    async def _call_anthropic(self, prompt: str) -> Dict[str, Any]:
        """Call Anthropic Claude API"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.anthropic_key,
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": "claude-3-sonnet-20240229",
                    "max_tokens": 4000,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                },
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            
            content = result['content'][0]['text']
            return json.loads(content)
    
    async def analyze_text(self, prompt: str) -> str:
        """General purpose text analysis using AI"""
        if not self.enable_ai:
            return ""
        
        try:
            if self.provider == 'google' and self.google_key:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={self.google_key}",
                        json={
                            "contents": [{
                                "parts": [{"text": prompt}]
                            }]
                        },
                        timeout=60.0
                    )
                    response.raise_for_status()
                    result = response.json()
                    return result['candidates'][0]['content']['parts'][0]['text']
            else:
                logger.warning(f"AI provider {self.provider} not configured for text analysis")
                return ""
        except Exception as e:
            logger.error(f"AI text analysis failed: {e}")
            return ""

    async def _call_ai_provider(self, prompt: str) -> Dict[str, Any]:
        """Call the configured AI provider"""
        if self.provider == 'google' and self.google_key:
            return await self._call_google(prompt)
        else:
            raise ValueError(f"AI provider {self.provider} not configured or API key missing")
    
    def _fallback_analysis(self, mission: str) -> Dict[str, Any]:
        """Fallback analysis when AI is not available"""
        content_lower = mission.lower()
        
        # Simple heuristics
        complexity = "medium"
        if any(word in content_lower for word in ["simple", "basic", "minimal"]):
            complexity = "simple"
        elif any(word in content_lower for word in ["complex", "enterprise", "scalable", "distributed"]):
            complexity = "complex"
        
        return {
            "complexity": complexity,
            "estimated_weeks": 8 if complexity == "medium" else (4 if complexity == "simple" else 12),
            "key_technologies": ["web", "database"],
            "required_skills": ["development", "testing"],
            "project_type": "web",
            "priority_phases": ["planning", "development", "testing"],
            "risk_factors": ["timeline", "scope_creep"],
            "recommended_team_size": 3,
            "budget_category": "medium"
        }
    
    def _fallback_milestones(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fallback milestone generation"""
        return [
            {
                "name": "Planning & Analysis",
                "description": "Requirements gathering and project planning",
                "duration_weeks": 2,
                "deliverables": ["Requirements document", "Project plan"],
                "dependencies": [],
                "critical_path": True
            },
            {
                "name": "Development",
                "description": "Core development and implementation",
                "duration_weeks": 4,
                "deliverables": ["Core features", "MVP"],
                "dependencies": ["Planning & Analysis"],
                "critical_path": True
            },
            {
                "name": "Testing & Deployment",
                "description": "Testing, bug fixes and deployment",
                "duration_weeks": 2,
                "deliverables": ["Test results", "Production deployment"],
                "dependencies": ["Development"],
                "critical_path": True
            }
        ]


# Global AI service instance
ai_service = AIService()
