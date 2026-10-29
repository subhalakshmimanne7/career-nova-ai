"""
career_matcher.py
Career matching and recommendation engine using Scikit-learn TF-IDF,
Cosine Similarity, and NumPy numerical operations.
"""

from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from analytics import load_and_validate_dataset, calculate_skill_coverage_and_readiness

DISCLAIMER_TEXT = (
    "Match percentages are algorithmic estimates generated using TF-IDF cosine similarity "
    "and weighted skill vector matching. They reflect profile alignment and do not represent "
    "guaranteed hiring probabilities or official job offers."
)

class CareerMatcher:
    def __init__(self, dataset_path: Optional[str] = None):
        self.df = load_and_validate_dataset(dataset_path)
        self._prepare_role_documents()

    def _prepare_role_documents(self):
        """Prepares aggregated text corpus for each career role."""
        if self.df.empty:
            self.role_profiles = {}
            return

        # Group skills by role
        grouped = self.df.groupby('role')
        self.role_profiles = {}

        for role_name, group in grouped:
            skills = group['skill'].tolist()
            categories = group['category'].tolist()
            descriptions = group['description'].tolist()

            # Create rich role document for TF-IDF representation
            doc_parts = [
                role_name,
                " ".join(skills),
                " ".join(categories),
                " ".join(descriptions)
            ]
            document = " ".join(doc_parts).lower()

            self.role_profiles[role_name] = {
                'skills': skills,
                'document': document,
                'categories': list(set(categories)),
                'group_df': group
            }

    def recommend_careers(
        self,
        student_skills: List[str],
        programming_languages: str = "",
        interests: str = "",
        projects: str = "",
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Ranks and returns career recommendations based on student's profile.
        Uses Scikit-learn TF-IDF + Cosine Similarity combined with NumPy weighted coverage.
        """
        if not self.role_profiles:
            return []

        roles_list = list(self.role_profiles.keys())
        role_docs = [self.role_profiles[r]['document'] for r in roles_list]

        # Student document combining all profile attributes
        student_tokens = [
            " ".join(student_skills),
            programming_languages,
            interests,
            projects
        ]
        student_doc = " ".join(student_tokens).lower().strip()

        if not student_doc:
            student_doc = "general technology computer science"

        # Fit TF-IDF Vectorizer
        corpus = [student_doc] + role_docs
        vectorizer = TfidfVectorizer(stop_words='english', token_pattern=r'(?u)\b[\w\+\#\.\-]+\b')
        tfidf_matrix = vectorizer.fit_transform(corpus)

        # Scikit-learn Cosine Similarity between student (index 0) and all roles (indices 1..N)
        student_vector = tfidf_matrix[0:1]
        role_vectors = tfidf_matrix[1:]
        cosine_scores = cosine_similarity(student_vector, role_vectors)[0]

        # Ensure cosine scores is a numpy array
        cosine_scores = np.asarray(cosine_scores, dtype=np.float64)

        recommendations = []
        normalized_student_skills = {s.strip().lower() for s in student_skills if s.strip()}

        for idx, role_name in enumerate(roles_list):
            cos_score = float(cosine_scores[idx])
            role_info = self.role_profiles[role_name]
            req_skills = role_info['skills']

            # Calculate exact weighted coverage using NumPy via analytics module
            coverage_data = calculate_skill_coverage_and_readiness(
                student_skills=student_skills,
                target_role=role_name,
                df=self.df
            )
            coverage_pct = coverage_data['coverage_score']

            # Match and missing skills breakdown
            matching_skills = []
            missing_skills = []

            for sk in req_skills:
                sk_clean = sk.lower()
                if any(sk_clean in s or s in sk_clean for s in normalized_student_skills):
                    matching_skills.append(sk)
                else:
                    missing_skills.append(sk)

            # Combined Score Formula using NumPy:
            # 60% direct weighted skill coverage + 40% TF-IDF semantic cosine similarity
            # Clipped between 0.0 and 100.0
            cos_pct = cos_score * 100.0
            combined_score = float(np.clip(
                (0.60 * coverage_pct) + (0.40 * cos_pct),
                0.0,
                100.0
            ))

            recommendations.append({
                'role': role_name,
                'match_percentage': round(combined_score, 1),
                'cosine_similarity': round(cos_score, 3),
                'skill_coverage_score': coverage_pct,
                'matching_skills': matching_skills,
                'missing_skills': missing_skills,
                'matched_count': len(matching_skills),
                'total_required_count': len(req_skills),
                'recommended_next_steps': self._get_next_steps(role_name, missing_skills),
                'disclaimer': DISCLAIMER_TEXT
            })

        # Sort descending by match percentage using Python / NumPy sorting
        recommendations.sort(key=lambda x: x['match_percentage'], reverse=True)
        return recommendations[:top_k]

    def _get_next_steps(self, role: str, missing_skills: List[str]) -> List[str]:
        """Provides tailored, practical next steps to bridge skills."""
        if not missing_skills:
            return [
                f"You have high alignment with {role}. Build a capstone project and prepare for technical interviews.",
                "Review system design and practice coding assessments.",
                "Polish your portfolio and resume with targeted job applications."
            ]

        top_missing = missing_skills[:2]
        return [
            f"Prioritize mastering {', '.join(top_missing)} through guided tutorials and documentation.",
            f"Build a portfolio project demonstrating hands-on application of {top_missing[0]}.",
            f"Generate a customized 30/60-day learning roadmap on Career Nova AI to track weekly progress."
        ]
