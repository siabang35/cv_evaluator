-- Seed Job Description
INSERT INTO reference_documents (document_type, title, content, metadata)
VALUES (
    'job_description',
    'Product Engineer (Backend) - 2025',
    'Rakamin is hiring a Product Engineer (Backend) to work on Rakamin. We''re looking for dedicated engineers who write code they''re proud of and who are eager to keep scaling and improving complex systems, including those powered by AI.

About the Job:
You''ll be building new product features alongside a frontend engineer and product manager using our Agile methodology, as well as addressing issues to ensure our apps are robust and our codebase is clean. As a Product Engineer, you''ll write clean, efficient code to enhance our product''s codebase in meaningful ways.

In addition to classic backend work, this role also touches on building AI-powered systems, where you''ll design and orchestrate how large language models (LLMs) integrate into Rakamin''s product ecosystem.

Key Responsibilities:
- Collaborating with frontend engineers and 3rd parties to build robust backend solutions
- Developing and maintaining server-side logic for central database
- Designing and fine-tuning AI prompts that align with product requirements
- Building LLM chaining flows
- Implementing Retrieval-Augmented Generation (RAG)
- Handling long-running AI processes gracefully
- Designing safeguards for uncontrolled scenarios
- Writing reusable, testable, and efficient code
- Strengthening test coverage with RSpec
- Conducting full product lifecycles

Required Skills:
- Backend languages and frameworks (Node.js, Django, Rails)
- Database management (MySQL, PostgreSQL, MongoDB)
- RESTful APIs
- Security compliance
- Cloud technologies (AWS, Google Cloud, Azure)
- Server-side languages (Java, Python, Ruby, or JavaScript)
- Understanding of frontend technologies
- User authentication and authorization
- Scalable application design principles
- Creating database schemas
- Implementing automated testing platforms
- Familiarity with LLM APIs, embeddings, vector databases and prompt design best practices',
    '{"job_title": "Product Engineer (Backend)", "department": "Engineering", "year": 2025}'::jsonb
);

-- Seed CV Scoring Rubric
INSERT INTO reference_documents (document_type, title, content, metadata)
VALUES (
    'cv_rubric',
    'CV Match Evaluation Rubric',
    'CV Match Evaluation (1-5 scale per parameter)

1. Technical Skills Match (Weight: 40%)
   Alignment with job requirements (backend, databases, APIs, cloud, AI/LLM).
   Scoring Guide:
   - 1 = Irrelevant skills
   - 2 = Few overlaps
   - 3 = Partial match
   - 4 = Strong match
   - 5 = Excellent match + AI/LLM exposure

2. Experience Level (Weight: 25%)
   Years of experience and project complexity.
   Scoring Guide:
   - 1 = <1 yr / trivial projects
   - 2 = 1-2 yrs
   - 3 = 2-3 yrs with mid-scale projects
   - 4 = 3-4 yrs solid track record
   - 5 = 5+ yrs / high-impact projects

3. Relevant Achievements (Weight: 20%)
   Impact of past work (scaling, performance, adoption).
   Scoring Guide:
   - 1 = No clear achievements
   - 2 = Minimal improvements
   - 3 = Some measurable outcomes
   - 4 = Significant contributions
   - 5 = Major measurable impact

4. Cultural / Collaboration Fit (Weight: 15%)
   Communication, learning mindset, teamwork/leadership.
   Scoring Guide:
   - 1 = Not demonstrated
   - 2 = Minimal
   - 3 = Average
   - 4 = Good
   - 5 = Excellent and well-demonstrated',
    '{"rubric_type": "cv_evaluation", "total_weight": 100}'::jsonb
);

-- Seed Project Scoring Rubric
INSERT INTO reference_documents (document_type, title, content, metadata)
VALUES (
    'project_rubric',
    'Project Deliverable Evaluation Rubric',
    'Project Deliverable Evaluation (1-5 scale per parameter)

1. Correctness (Prompt & Chaining) (Weight: 30%)
   Implements prompt design, LLM chaining, RAG context injection.
   Scoring Guide:
   - 1 = Not implemented
   - 2 = Minimal attempt
   - 3 = Works partially
   - 4 = Works correctly
   - 5 = Fully correct + thoughtful

2. Code Quality & Structure (Weight: 25%)
   Clean, modular, reusable, tested.
   Scoring Guide:
   - 1 = Poor
   - 2 = Some structure
   - 3 = Decent modularity
   - 4 = Good structure + some tests
   - 5 = Excellent quality + strong tests

3. Resilience & Error Handling (Weight: 20%)
   Handles long jobs, retries, randomness, API failures.
   Scoring Guide:
   - 1 = Missing
   - 2 = Minimal
   - 3 = Partial handling
   - 4 = Solid handling
   - 5 = Robust, production-ready

4. Documentation & Explanation (Weight: 15%)
   README clarity, setup instructions, trade-off explanations.
   Scoring Guide:
   - 1 = Missing
   - 2 = Minimal
   - 3 = Adequate
   - 4 = Clear
   - 5 = Excellent + insightful

5. Creativity / Bonus (Weight: 10%)
   Extra features beyond requirements.
   Scoring Guide:
   - 1 = None
   - 2 = Very basic
   - 3 = Useful extras
   - 4 = Strong enhancements
   - 5 = Outstanding creativity',
    '{"rubric_type": "project_evaluation", "total_weight": 100}'::jsonb
);

-- Seed Case Study Brief
INSERT INTO reference_documents (document_type, title, content, metadata)
VALUES (
    'case_study_brief',
    'Backend Developer Case Study Brief',
    'Objective:
Your mission is to build a backend service that automates the initial screening of a job application. The service will receive a candidate''s CV and a project report, evaluate them against a specific job description and a case study brief, and produce a structured, AI-generated evaluation report.

Core Logic & Data Flow:
The system operates with a clear separation of inputs and reference documents:

Candidate-Provided Inputs:
- Candidate CV: The candidate''s resume (PDF)
- Project Report: The candidate''s project report to our take-home case study (PDF)

System-Internal Documents:
- Job Description: A document detailing the requirements and responsibilities for the role
- Case Study Brief: This document used as ground truth for Project Report
- Scoring Rubric: A predefined set of parameters for evaluating CV and Report

Deliverables:
1. Backend Service (API endpoints)
   - POST /upload: Accepts CV and Project Report
   - POST /evaluate: Triggers async AI evaluation pipeline
   - GET /result/{id}: Retrieves evaluation status and results

2. Evaluation Pipeline
   - RAG (Context Retrieval): Ingest system documents into vector database
   - Prompt Design & LLM Chaining: CV evaluation, Project evaluation, Final analysis
   - Long-Running Process Handling: Async job processing
   - Error Handling & Randomness Control: Retries, backoff, temperature control

3. Standardized Evaluation Parameters
   - CV Evaluation: Technical Skills, Experience Level, Achievements, Cultural Fit
   - Project Evaluation: Correctness, Code Quality, Resilience, Documentation, Creativity',
    '{"brief_type": "case_study", "year": 2025}'::jsonb
);
