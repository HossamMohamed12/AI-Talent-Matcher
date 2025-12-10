"""
CV Evaluator API Module
Handles all DeepSeek API interactions and CV evaluation logic
"""

import os
import json
from datetime import datetime
from pathlib import Path
import PyPDF2
import requests

class CVEvaluator:
    def __init__(self, api_key, job_description=None):
        """
        Initialize CV Evaluator with DeepSeek API

        Args:
            api_key: DeepSeek API key
            job_description: Optional job description text or file path
        """
        self.api_key = api_key
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.job_description = job_description

    def extract_text_from_pdf(self, pdf_path):
        """Extract text content from PDF file"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {e}")
            return None

    def create_evaluation_prompt(self, cv_text, candidate_name, job_title, company, department):
        """Create a structured prompt for DeepSeek API that ensures consistent output"""

        prompt = f"""You are an expert HR analyst evaluating candidate CVs for a specific role.

**JOB DETAILS:**
- Role: {job_title}
- Company: {company}
- Department: {department}
{f"- Job Description: {self.job_description}" if self.job_description else ""}

**CANDIDATE CV:**
{cv_text}

**YOUR TASK:**
Evaluate this candidate against the role requirements and provide a structured assessment.

**SCORING SYSTEM (Total: 100 points):**
- Core Skills Match: 35 points (How well technical/functional skills align with role)
- Experience Relevance: 25 points (Relevance of past work to this position)
- Experience Level: 15 points (Years of experience and seniority level)
- Education and Certifications: 5 points (Academic background and professional certifications)
- Soft Skills and Competencies: 10 points (Leadership, communication, problem-solving)
- Bonus Fit Indicators: 10 points (Cultural fit, additional value-adds, achievements)

**IMPORTANT:** Be lenient in scoring. Most qualified candidates should score 65-85. Only truly exceptional candidates score 90+. Only severely mismatched candidates score below 50.

**OUTPUT FORMAT (You MUST respond with valid JSON only):**
{{
  "candidate_name": "{candidate_name}",
  "match_score": <number>,
  "rating_summary": "<exactly 50 words>",
  "strengths": [
    "<strength 1>",
    "<strength 2>",
    "<strength 3>",
    "<strength 4>"
  ],
  "potential_gaps": [
    "<gap 1>",
    "<gap 2>"
  ]
}}

**RULES:**
1. Respond ONLY with valid JSON. No markdown, no explanations, just JSON.
2. Rating summary must be EXACTLY 50 words (±3 words acceptable) explaining the scoring logic.
3. Provide exactly 4 strengths and 2 potential gaps.
4. Be specific and reference actual experience from the CV.
5. Be lenient - focus on potential and transferable skills.
6. Match score should reflect overall evaluation across all criteria.
"""
        return prompt

    def call_deepseek_api(self, prompt, max_retries=3):
        """Call DeepSeek API with retry logic"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert HR analyst. You always respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 2000
        }

        for attempt in range(max_retries):
            try:
                response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
                response.raise_for_status()
                result = response.json()
                content = result['choices'][0]['message']['content']

                # Clean up response
                if content.startswith('```json'):
                    content = content[7:]
                if content.startswith('```'):
                    content = content[3:]
                if content.endswith('```'):
                    content = content[:-3]
                content = content.strip()

                # Parse JSON
                evaluation = json.loads(content)
                return evaluation

            except json.JSONDecodeError as e:
                print(f"Attempt {attempt + 1}: JSON parsing error - {e}")
                if attempt == max_retries - 1:
                    print(f"Raw response: {content}")
                    raise
            except requests.exceptions.RequestException as e:
                print(f"Attempt {attempt + 1}: API request error - {e}")
                if attempt == max_retries - 1:
                    raise

        return None

    def generate_overall_summary(self, evaluations, job_title):
        """Generate an overall summary comparing all candidates"""
        if not evaluations:
            return "No candidates were evaluated."

        if len(evaluations) == 1:
            candidate = evaluations[0]
            return f"{candidate['candidate_name']} is the only candidate evaluated with a match score of {candidate['match_score']}/100."

        # Create a summary prompt for all candidates
        candidates_info = "\n".join([
            f"- {eval['candidate_name']}: {eval['match_score']}/100 - {eval['rating_summary'][:100]}"
            for eval in evaluations
        ])

        prompt = f"""Based on the following candidate evaluations for the {job_title} role, write a concise 80-word overall summary comparing all candidates and providing a final recommendation.

CANDIDATES:
{candidates_info}

Provide an 80-word summary that:
1. Compares the candidates
2. Highlights the top candidate and why
3. Notes key differentiators
4. Provides a clear recommendation

Respond with ONLY the 80-word summary text, no JSON, no formatting."""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert HR analyst providing clear, concise summaries."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.4,
            "max_tokens": 200
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            summary = result['choices'][0]['message']['content'].strip()
            return summary
        except Exception as e:
            print(f"Error generating overall summary: {e}")
            # Fallback summary
            top_candidate = evaluations[0]
            return f"{top_candidate['candidate_name']} ranks highest with a score of {top_candidate['match_score']}/100, demonstrating the strongest alignment with role requirements across all evaluation criteria."

    def evaluate_candidates(self, cv_files, job_title, company, department, location="", work_mode=""):
        """
        Evaluate multiple CV files and generate structured report data

        Returns:
            Dictionary with report data sorted by match score
        """
        print(f"\n{'='*60}")
        print(f"Starting CV Evaluation for {job_title} at {company}")
        print(f"{'='*60}\n")

        evaluations = []

        for i, cv_file in enumerate(cv_files, 1):
            print(f"Processing CV {i}/{len(cv_files)}: {cv_file}")

            # Extract candidate name from filename
            candidate_name = Path(cv_file).stem.replace('_', ' ').replace('-', ' ')

            # Extract text from PDF
            cv_text = self.extract_text_from_pdf(cv_file)
            if not cv_text:
                print(f"  ❌ Failed to extract text from {cv_file}")
                continue

            print(f"  ✓ Extracted {len(cv_text)} characters")

            # Create prompt
            prompt = self.create_evaluation_prompt(
                cv_text, candidate_name, job_title, company, department
            )

            # Call API
            print(f"  → Calling DeepSeek API...")
            try:
                evaluation = self.call_deepseek_api(prompt)
                if evaluation:
                    evaluations.append(evaluation)
                    print(f"  ✓ Evaluation complete - Match Score: {evaluation['match_score']}/100\n")
                else:
                    print(f"  ❌ Failed to get evaluation\n")
            except Exception as e:
                print(f"  ❌ Error during evaluation: {e}\n")
                continue

        # Sort by match score
        evaluations.sort(key=lambda x: x['match_score'], reverse=True)

        # Generate overall summary
        print("\n→ Generating overall summary...")
        overall_summary = self.generate_overall_summary(evaluations, job_title)
        print("✓ Overall summary generated\n")

        # Create report data structure
        report_data = {
            "report_header": {
                "role": job_title,
                "department": department,
                "company": company,
                "location": location,
                "work_mode": work_mode,
                "report_date": datetime.now().strftime("%d %B %Y"),
                "assessment_method": "This report provides an AI-assisted evaluation of candidates against the role requirements. It summarizes estimated role fit, highlights strengths and potential risks, and presents a structured match score to support HR and hiring manager decisions."
            },
            "candidates": evaluations,
            "overall_summary": overall_summary,
            "total_candidates": len(evaluations)
        }

        return report_data

    def save_json_report(self, report_data, output_file="evaluation_report.json"):
        """Save report data as JSON"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        print(f"✅ JSON report saved: {output_file}")
        return output_file

    def generate_pdf_report(self, report_data, output_file="evaluation_report.pdf"):
        """
        Generate PDF report from evaluation data

        Args:
            report_data: Dictionary with report data
            output_file: Output PDF filename

        Returns:
            Path to generated PDF file
        """
        try:
            from pdf_generator import PDFReportGenerator

            print(f"\n→ Generating PDF report...")
            pdf_gen = PDFReportGenerator()
            pdf_path = pdf_gen.generate_pdf(report_data, output_file)
            print(f"✅ PDF report generated: {pdf_path}")

            return pdf_path
        except ImportError:
            print("❌ PDF generator module not found. Please ensure pdf_generator.py is available.")
            return None
        except Exception as e:
            print(f"❌ Error generating PDF: {e}")
            return None
