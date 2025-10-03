import groq
from typing import Dict, Optional, List
import json
import time
from app.config import settings
from app.utils.retry_logic import retry_llm_call
from app.utils.error_handler import LLMError


class LLMService:
    def __init__(self):
        self.client = groq.Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.LLM_MODEL
        self.temperature = settings.LLM_TEMPERATURE
        self.max_tokens = settings.MAX_TOKENS
    
    @retry_llm_call
    def call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        response_format: Optional[Dict] = None
    ) -> Dict:
        """
        Call Groq LLM with retry logic and error handling.
        
        Returns:
            Dictionary with response content and usage statistics
        """
        start_time = time.time()
        
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature or self.temperature,
                "max_tokens": self.max_tokens
            }
            
            if response_format:
                kwargs["response_format"] = response_format
            
            response = self.client.chat.completions.create(**kwargs)
            
            end_time = time.time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            return {
                "content": response.choices[0].message.content,
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
                "response_time_ms": response_time_ms,
                "model": response.model
            }
        
        except Exception as e:
            raise LLMError(
                message=f"Groq API call failed: {str(e)}",
                step="llm_call",
                details={"model": self.model, "error": str(e)}
            )
    
    def parse_cv_to_structured_data(self, cv_text: str) -> Dict:
        """
        Step 1: Parse CV into structured data using LLM.
        """
        system_prompt = """You are an expert CV parser. Extract structured information from CVs.

Your task is to parse the CV and extract:
1. Personal Information (name, contact, location)
2. Technical Skills (programming languages, frameworks, tools, databases, cloud platforms)
3. Work Experience (companies, roles, durations, key responsibilities)
4. Education (degrees, institutions, years)
5. Projects (names, descriptions, technologies used)
6. Achievements (awards, certifications, notable accomplishments)

Return the information in a structured JSON format."""

        user_prompt = f"""Parse the following CV and extract structured information:

CV Content:
{cv_text}

Return a JSON object with the following structure:
{{
  "name": "candidate name",
  "contact": {{"email": "", "phone": "", "linkedin": ""}},
  "technical_skills": ["skill1", "skill2", ...],
  "experience": [
    {{"company": "", "role": "", "duration": "", "responsibilities": ["resp1", "resp2"]}}
  ],
  "education": [
    {{"degree": "", "institution": "", "year": ""}}
  ],
  "projects": [
    {{"name": "", "description": "", "technologies": ["tech1", "tech2"]}}
  ],
  "achievements": ["achievement1", "achievement2"]
}}"""

        response = self.call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.1
        )
        
        try:
            parsed_data = json.loads(response["content"])
        except json.JSONDecodeError:
            # Fallback: return raw content if JSON parsing fails
            parsed_data = {"raw_content": response["content"]}
        
        return {
            "parsed_data": parsed_data,
            "usage": {
                "prompt_tokens": response["prompt_tokens"],
                "completion_tokens": response["completion_tokens"],
                "response_time_ms": response["response_time_ms"]
            }
        }
    
    def evaluate_cv(
        self,
        cv_structured_data: Dict,
        job_title: str,
        rag_context: str
    ) -> Dict:
        """
        Step 2: Evaluate CV against job requirements using RAG context.
        
        Returns cv_match_rate (0-1) and cv_feedback.
        """
        system_prompt = """You are an expert technical recruiter evaluating candidates for backend engineering positions.

Your task is to evaluate a candidate's CV against job requirements and scoring rubrics.

Evaluation Criteria (from rubric):
1. Technical Skills Match (40% weight): Backend, databases, APIs, cloud, AI/LLM
   - Score 1-5 based on alignment with job requirements
2. Experience Level (25% weight): Years and project complexity
   - Score 1-5 based on experience depth
3. Relevant Achievements (20% weight): Impact, scaling, performance
   - Score 1-5 based on measurable outcomes
4. Cultural/Collaboration Fit (15% weight): Communication, learning, teamwork
   - Score 1-5 based on demonstrated soft skills

Calculate weighted average and convert to match rate (0-1 scale).
Provide detailed, constructive feedback."""

        user_prompt = f"""Evaluate this candidate for the position: {job_title}

CANDIDATE CV DATA:
{json.dumps(cv_structured_data, indent=2)}

RELEVANT JOB REQUIREMENTS AND RUBRIC:
{rag_context}

Provide your evaluation in the following JSON format:
{{
  "technical_skills_score": <1-5>,
  "technical_skills_reasoning": "explanation",
  "experience_level_score": <1-5>,
  "experience_level_reasoning": "explanation",
  "achievements_score": <1-5>,
  "achievements_reasoning": "explanation",
  "cultural_fit_score": <1-5>,
  "cultural_fit_reasoning": "explanation",
  "weighted_average": <calculated weighted average>,
  "match_rate": <0.00-1.00>,
  "overall_feedback": "3-5 sentences of constructive feedback highlighting strengths and areas for improvement"
}}

Calculate match_rate as: (weighted_average - 1) / 4 to convert 1-5 scale to 0-1 scale."""

        response = self.call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.3
        )
        
        try:
            evaluation = json.loads(response["content"])
        except json.JSONDecodeError:
            # Fallback parsing
            evaluation = {
                "match_rate": 0.5,
                "overall_feedback": response["content"]
            }
        
        return {
            "cv_match_rate": evaluation.get("match_rate", 0.5),
            "cv_feedback": evaluation.get("overall_feedback", "Evaluation completed."),
            "detailed_scores": evaluation,
            "usage": {
                "prompt_tokens": response["prompt_tokens"],
                "completion_tokens": response["completion_tokens"],
                "response_time_ms": response["response_time_ms"]
            }
        }
    
    def parse_project_report(self, project_text: str) -> Dict:
        """
        Step 3: Parse project report into structured data.
        """
        system_prompt = """You are an expert code reviewer analyzing project reports.

Extract structured information about:
1. Project Overview (objective, approach, technologies used)
2. System Architecture (design decisions, components, integrations)
3. Implementation Details (key features, code quality indicators)
4. Error Handling & Resilience (retry logic, failure handling, edge cases)
5. Documentation Quality (README, explanations, setup instructions)
6. Bonus Features (creative additions, extra functionality)

Return structured JSON."""

        user_prompt = f"""Parse the following project report and extract structured information:

PROJECT REPORT:
{project_text}

Return a JSON object with:
{{
  "project_overview": "summary of project objective and approach",
  "technologies_used": ["tech1", "tech2", ...],
  "architecture": "description of system design",
  "key_features": ["feature1", "feature2", ...],
  "error_handling": "description of resilience measures",
  "documentation_quality": "assessment of documentation",
  "bonus_features": ["bonus1", "bonus2", ...],
  "code_quality_indicators": ["indicator1", "indicator2", ...]
}}"""

        response = self.call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.1
        )
        
        try:
            parsed_data = json.loads(response["content"])
        except json.JSONDecodeError:
            parsed_data = {"raw_content": response["content"]}
        
        return {
            "parsed_data": parsed_data,
            "usage": {
                "prompt_tokens": response["prompt_tokens"],
                "completion_tokens": response["completion_tokens"],
                "response_time_ms": response["response_time_ms"]
            }
        }
    
    def evaluate_project_report(
        self,
        project_structured_data: Dict,
        rag_context: str
    ) -> Dict:
        """
        Step 4: Evaluate project report against case study requirements.
        
        Returns project_score (1-5) and project_feedback.
        """
        system_prompt = """You are an expert technical evaluator assessing project deliverables.

Evaluation Criteria (from rubric):
1. Correctness (30% weight): Prompt design, LLM chaining, RAG implementation
   - Score 1-5 based on requirement fulfillment
2. Code Quality (25% weight): Clean, modular, tested
   - Score 1-5 based on structure and maintainability
3. Resilience (20% weight): Error handling, retries, edge cases
   - Score 1-5 based on robustness
4. Documentation (15% weight): README, explanations, setup
   - Score 1-5 based on clarity
5. Creativity (10% weight): Bonus features, innovations
   - Score 1-5 based on extras

Calculate weighted average for final score (1-5 scale)."""

        user_prompt = f"""Evaluate this project report against the case study requirements.

PROJECT DATA:
{json.dumps(project_structured_data, indent=2)}

CASE STUDY REQUIREMENTS AND RUBRIC:
{rag_context}

Provide evaluation in JSON format:
{{
  "correctness_score": <1-5>,
  "correctness_reasoning": "explanation",
  "code_quality_score": <1-5>,
  "code_quality_reasoning": "explanation",
  "resilience_score": <1-5>,
  "resilience_reasoning": "explanation",
  "documentation_score": <1-5>,
  "documentation_reasoning": "explanation",
  "creativity_score": <1-5>,
  "creativity_reasoning": "explanation",
  "weighted_average": <calculated score 1-5>,
  "project_score": <1.00-5.00>,
  "overall_feedback": "3-5 sentences of constructive feedback on strengths and improvements"
}}"""

        response = self.call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.3
        )
        
        try:
            evaluation = json.loads(response["content"])
        except json.JSONDecodeError:
            evaluation = {
                "project_score": 3.0,
                "overall_feedback": response["content"]
            }
        
        return {
            "project_score": evaluation.get("project_score", 3.0),
            "project_feedback": evaluation.get("project_feedback", "Evaluation completed."),
            "detailed_scores": evaluation,
            "usage": {
                "prompt_tokens": response["prompt_tokens"],
                "completion_tokens": response["completion_tokens"],
                "response_time_ms": response["response_time_ms"]
            }
        }
    
    def generate_overall_summary(
        self,
        cv_evaluation: Dict,
        project_evaluation: Dict,
        job_title: str
    ) -> Dict:
        """
        Step 5: Synthesize all evaluations into final summary.
        """
        system_prompt = """You are a senior technical hiring manager making final candidate assessments.

Synthesize CV and project evaluations into a concise overall summary.

Your summary should:
1. Highlight key strengths (2-3 points)
2. Identify gaps or areas for improvement (1-2 points)
3. Provide a clear hiring recommendation
4. Be 3-5 sentences, professional and constructive"""

        user_prompt = f"""Create an overall candidate assessment for: {job_title}

CV EVALUATION:
- Match Rate: {cv_evaluation.get('cv_match_rate', 0):.2f}
- Feedback: {cv_evaluation.get('cv_feedback', 'N/A')}

PROJECT EVALUATION:
- Score: {project_evaluation.get('project_score', 0):.2f}/5.00
- Feedback: {project_evaluation.get('project_feedback', 'N/A')}

Provide a concise overall summary (3-5 sentences) that synthesizes both evaluations and gives a clear recommendation."""

        response = self.call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.4
        )
        
        return {
            "overall_summary": response["content"],
            "usage": {
                "prompt_tokens": response["prompt_tokens"],
                "completion_tokens": response["completion_tokens"],
                "response_time_ms": response["response_time_ms"]
            }
        }
