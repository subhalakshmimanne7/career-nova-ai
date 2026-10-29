"""
resume_analyzer.py
ATS Resume Analyzer for extracting text from PDF and DOCX files,
parsing sections, matching skills with target career roles,
and calculating compatibility metrics.
"""

import os
import re
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from pypdf import PdfReader
import docx
from analytics import load_and_validate_dataset

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

ACTION_VERBS = {
    'developed', 'designed', 'built', 'implemented', 'created', 'architected',
    'optimized', 'engineered', 'analyzed', 'automated', 'deployed', 'managed',
    'integrated', 'scaled', 'reduced', 'increased', 'accelerated', 'spearheaded'
}

ATS_DISCLAIMER = (
    "This ATS compatibility score is an indicative evaluation based on keyword coverage, "
    "structural sections, and actionable phrasing. It is an educational tool and does not "
    "replicate proprietary algorithms of commercial applicant tracking systems."
)

class ResumeAnalyzer:
    def __init__(self, dataset_path: Optional[str] = None):
        self.df = load_and_validate_dataset(dataset_path)
        # Unique list of known technical skills from dataset
        self.known_skills = sorted(list(self.df['skill'].unique()), key=len, reverse=True) if not self.df.empty else []

    @staticmethod
    def allowed_file(filename: str) -> bool:
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def extract_text(self, file_path: str) -> str:
        """Extracts text safely from PDF or DOCX file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError("The uploaded file does not exist.")

        file_size = os.path.getsize(file_path)
        if file_size > MAX_FILE_SIZE:
            raise ValueError(f"File size exceeds the 5MB limit ({file_size} bytes).")

        ext = file_path.rsplit('.', 1)[1].lower()
        text_content = []

        if ext == 'pdf':
            try:
                reader = PdfReader(file_path)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(page_text)
            except Exception as e:
                raise ValueError(f"Failed to read PDF document: {str(e)}")

        elif ext == 'docx':
            try:
                doc = docx.Document(file_path)
                for p in doc.paragraphs:
                    if p.text:
                        text_content.append(p.text)
                for table in doc.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            if cell.text:
                                text_content.append(cell.text)
            except Exception as e:
                raise ValueError(f"Failed to read DOCX document: {str(e)}")
        else:
            raise ValueError("Unsupported file format. Please upload a .pdf or .docx document.")

        full_text = "\n".join(text_content).strip()
        if not full_text:
            raise ValueError("The uploaded document appears to be empty or scanned as an image.")
        return full_text

    def parse_resume(self, text: str) -> Dict[str, Any]:
        """Extracts candidate contact details, sections, and mentioned skills."""
        # Contact extraction via regex
        email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
        phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}', text)
        linkedin_match = re.search(r'linkedin\.com/in/[a-zA-Z0-9_-]+', text, re.IGNORECASE)
        github_match = re.search(r'github\.com/[a-zA-Z0-9_-]+', text, re.IGNORECASE)

        # Section detection
        has_education = bool(re.search(r'\b(education|b\.?tech|b\.?e|m\.?tech|bachelor|master|degree|university|college|gpa|cgpa)\b', text, re.I))
        has_experience = bool(re.search(r'\b(experience|internship|work history|employment|position)\b', text, re.I))
        has_projects = bool(re.search(r'\b(projects|academic projects|portfolio|capstone)\b', text, re.I))
        has_certifications = bool(re.search(r'\b(certifications?|licenses?|credentials?|certificates?)\b', text, re.I))

        # Skill extraction
        extracted_skills = []
        text_lower = text.lower()

        # Match against known tech skills
        for skill in self.known_skills:
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower):
                extracted_skills.append(skill)

        # Additional common programming keywords
        extra_keywords = [
            'Python', 'JavaScript', 'TypeScript', 'Java', 'C++', 'C#', 'SQL',
            'HTML', 'CSS', 'React', 'Angular', 'Vue', 'Django', 'Flask', 'FastAPI',
            'Git', 'GitHub', 'Docker', 'Kubernetes', 'AWS', 'Azure', 'Linux',
            'MongoDB', 'PostgreSQL', 'MySQL', 'Pandas', 'NumPy', 'Scikit-learn',
            'TensorFlow', 'PyTorch', 'Data Structures', 'Algorithms'
        ]
        for kw in extra_keywords:
            if kw not in extracted_skills and re.search(r'\b' + re.escape(kw.lower()) + r'\b', text_lower):
                extracted_skills.append(kw)

        # Action verbs count and metrics count
        action_verb_count = sum(1 for v in ACTION_VERBS if re.search(r'\b' + v + r'\b', text_lower))
        metrics_found = len(re.findall(r'\b(\d+[\%kKmM]?|\$\d+|\d+\+)\b', text))

        return {
            'email': email_match.group(0) if email_match else None,
            'phone': phone_match.group(0) if phone_match else None,
            'linkedin': linkedin_match.group(0) if linkedin_match else None,
            'github': github_match.group(0) if github_match else None,
            'has_education': has_education,
            'has_experience': has_experience,
            'has_projects': has_projects,
            'has_certifications': has_certifications,
            'extracted_skills': extracted_skills,
            'action_verb_count': action_verb_count,
            'metrics_found': metrics_found,
            'word_count': len(text.split())
        }

    def analyze_against_role(self, text: str, target_role: str) -> Dict[str, Any]:
        """
        Analyzes resume text against the target role requirements using Pandas and NumPy.
        Calculates ATS compatibility score and targeted improvements.
        """
        parsed = self.parse_resume(text)
        extracted = parsed['extracted_skills']

        # Get role requirements from dataset
        role_df = self.df[self.df['role'].str.lower() == target_role.lower()]
        if role_df.empty:
            req_skills = []
            weights = np.array([])
        else:
            req_skills = role_df['skill'].tolist()
            weights = role_df['weight'].to_numpy(dtype=np.float64)

        matching_skills = []
        missing_skills = []

        extracted_lower = {s.lower() for s in extracted}

        if req_skills:
            match_mask = np.zeros(len(req_skills), dtype=bool)
            for i, req in enumerate(req_skills):
                req_clean = req.lower()
                if any(req_clean in s or s in req_clean for s in extracted_lower):
                    matching_skills.append(req)
                    match_mask[i] = True
                else:
                    missing_skills.append(req)

            # Keyword weighted match score using NumPy
            total_weight = np.sum(weights)
            matched_weight = np.sum(weights[match_mask])
            keyword_score = float((matched_weight / total_weight) * 100.0) if total_weight > 0 else 0.0
        else:
            keyword_score = 50.0

        # Section completeness score (out of 100)
        sections = [
            parsed['has_education'],
            parsed['has_projects'],
            bool(parsed['extracted_skills']),
            bool(parsed['email'] or parsed['phone']),
            parsed['has_experience']
        ]
        section_score = float(np.sum(sections) / len(sections) * 100.0)

        # Content phrasing score: action verbs and quantifiable metrics
        verb_score = min(100.0, parsed['action_verb_count'] * 15.0)
        metrics_score = min(100.0, parsed['metrics_found'] * 12.0)
        phrasing_score = float((verb_score + metrics_score) / 2.0)

        # Word count appropriateness (ideal: 300 - 800 words for student resume)
        wc = parsed['word_count']
        if 350 <= wc <= 800:
            length_score = 100.0
        elif 200 <= wc < 350 or 800 < wc <= 1100:
            length_score = 75.0
        else:
            length_score = 50.0

        # Overall ATS Score Formula:
        # 50% keyword match + 25% section completeness + 15% phrasing/metrics + 10% length balance
        ats_score = float(np.clip(
            (0.50 * keyword_score) +
            (0.25 * section_score) +
            (0.15 * phrasing_score) +
            (0.10 * length_score),
            0.0,
            100.0
        ))

        # Actionable improvements
        suggestions = self._generate_suggestions(parsed, missing_skills, target_role)

        return {
            'target_role': target_role,
            'ats_score': round(ats_score, 1),
            'keyword_match_score': round(keyword_score, 1),
            'section_completeness_score': round(section_score, 1),
            'phrasing_score': round(phrasing_score, 1),
            'length_score': round(length_score, 1),
            'extracted_skills': extracted,
            'matching_skills': matching_skills,
            'missing_skills': missing_skills,
            'completeness_breakdown': {
                'contact_info': bool(parsed['email'] or parsed['phone']),
                'education': parsed['has_education'],
                'projects': parsed['has_projects'],
                'experience': parsed['has_experience'],
                'certifications': parsed['has_certifications'],
                'word_count': parsed['word_count']
            },
            'suggestions': suggestions,
            'disclaimer': ATS_DISCLAIMER
        }

    def _generate_suggestions(self, parsed: Dict[str, Any], missing_skills: List[str], role: str) -> List[Dict[str, str]]:
        suggestions = []

        if missing_skills:
            top_missing = ", ".join(missing_skills[:3])
            suggestions.append({
                'category': 'Role Keywords',
                'recommendation': f"Integrate high-priority keywords for {role}: '{top_missing}' in your skills and project descriptions.",
                'priority': 'High'
            })

        if not parsed['has_projects']:
            suggestions.append({
                'category': 'Project Section',
                'recommendation': "Add a dedicated 'Projects' section showcasing 2-3 technical projects with GitHub repositories and live links.",
                'priority': 'High'
            })

        if parsed['action_verb_count'] < 4:
            suggestions.append({
                'category': 'Action Verbs',
                'recommendation': "Start bullet points with strong action verbs (e.g., 'Architected', 'Engineered', 'Optimized', 'Deployed') instead of passive phrases.",
                'priority': 'Medium'
            })

        if parsed['metrics_found'] < 3:
            suggestions.append({
                'category': 'Quantifiable Impact',
                'recommendation': "Add measurable metrics to project accomplishments (e.g., 'Achieved 92% classification accuracy', 'Reduced API latency by 35%').",
                'priority': 'Medium'
            })

        if not (parsed['email'] and parsed['phone']):
            suggestions.append({
                'category': 'Contact Details',
                'recommendation': "Ensure professional email address, phone number, and clickable GitHub / LinkedIn profiles are clearly visible in the header.",
                'priority': 'High'
            })

        if parsed['word_count'] < 250:
            suggestions.append({
                'category': 'Resume Depth',
                'recommendation': "Your resume appears too brief. Elaborate on project architectures, technologies utilized, and problem-solving methodologies.",
                'priority': 'Medium'
            })

        return suggestions
