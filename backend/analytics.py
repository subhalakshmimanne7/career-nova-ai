"""
analytics.py
Dedicated module for Career Nova AI dataset analysis, data wrangling,
and numerical computations using Pandas and NumPy.
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np

DEFAULT_DATASET_PATH = Path(__file__).resolve().parent / 'datasets' / 'career_skills.csv'

def load_and_validate_dataset(csv_path: Optional[str] = None) -> pd.DataFrame:
    """
    1. Loads and validates career_skills.csv using Pandas.
    Ensures required columns exist: role, skill, category, weight.
    """
    path = csv_path or str(DEFAULT_DATASET_PATH)
    if not os.path.exists(path):
        return handle_empty_or_invalid_data()
    
    try:
        df = pd.read_csv(path)
        required_cols = {'role', 'skill', 'category', 'weight'}
        if not required_cols.issubset(set(df.columns)):
            return handle_empty_or_invalid_data()
        
        return clean_skill_data(df)
    except Exception as e:
        print(f"Error loading career dataset: {e}")
        return handle_empty_or_invalid_data()

def clean_skill_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    2. Cleans missing, duplicated, and inconsistent skill data using Pandas.
    Trims whitespace, normalizes text casing, validates numerical weights.
    """
    if df.empty:
        return df

    # Drop fully empty rows
    df = df.dropna(subset=['role', 'skill']).copy()

    # Strip whitespace & normalize types
    df['role'] = df['role'].astype(str).str.strip()
    df['skill'] = df['skill'].astype(str).str.strip()
    df['category'] = df['category'].fillna('General').astype(str).str.strip()
    
    # Ensure weight is numerical float in range [1.0, 5.0]
    df['weight'] = pd.to_numeric(df['weight'], errors='coerce').fillna(3.0).astype(float)
    df['weight'] = np.clip(df['weight'].to_numpy(), 1.0, 5.0)

    if 'description' not in df.columns:
        df['description'] = ''
    else:
        df['description'] = df['description'].fillna('').astype(str).str.strip()

    # Drop duplicates on (role, skill) keeping highest weight
    df = df.sort_values(by=['role', 'weight'], ascending=[True, False])
    df = df.drop_duplicates(subset=['role', 'skill'], keep='first').reset_index(drop=True)

    return df

def convert_skills_to_numerical(df: pd.DataFrame) -> Dict[str, Any]:
    """
    3. Converts skill information into numerical representations and matrices.
    Returns:
      - role_skill_matrix: pivot table of roles vs skills weighted numerically
      - skill_frequencies: count and frequency percentage of each skill
      - category_weights: mean weight per skill category
    """
    if df.empty:
        return {
            'matrix': {},
            'skill_frequencies': {},
            'category_weights': {},
            'total_roles': 0,
            'total_skills': 0
        }

    # Numerical pivot table: rows = roles, columns = skills, values = weight (or 0)
    pivot = pd.pivot_table(
        df,
        values='weight',
        index='role',
        columns='skill',
        fill_value=0.0,
        aggfunc='max'
    )

    # Skill frequency across all career roles
    skill_counts = df['skill'].value_counts()
    total_roles = df['role'].nunique()
    skill_freq = (skill_counts / total_roles * 100).round(1).to_dict()

    # Category weight averages using NumPy
    cat_summary = df.groupby('category')['weight'].agg(['count', 'mean']).round(2)
    cat_weights = {
        cat: {'count': int(row['count']), 'avg_weight': float(row['mean'])}
        for cat, row in cat_summary.iterrows()
    }

    return {
        'roles': pivot.index.tolist(),
        'skills': pivot.columns.tolist(),
        'matrix': pivot.to_dict(orient='index'),
        'skill_frequencies': skill_freq,
        'category_weights': cat_weights,
        'total_roles': int(total_roles),
        'total_skills': int(df['skill'].nunique())
    }

def calculate_skill_coverage_and_readiness(
    student_skills: List[str],
    target_role: str,
    df: Optional[pd.DataFrame] = None
) -> Dict[str, Any]:
    """
    4. Calculates skill coverage and weighted readiness scores using NumPy.
    Formula:
      Coverage % = (Demonstrated Weighted Points / Total Required Weighted Points) * 100
    """
    if df is None:
        df = load_and_validate_dataset()

    role_df = df[df['role'].str.lower() == target_role.lower()]
    if role_df.empty:
        # Unknown role fallback
        return {
            'role': target_role,
            'coverage_score': 0.0,
            'unweighted_coverage': 0.0,
            'total_skills_required': 0,
            'matched_skills_count': 0,
            'missing_skills_count': 0,
            'weights_demonstrated': 0.0,
            'total_weights_required': 0.0,
            'formula_explanation': "Target role was not found in the career dataset."
        }

    # Normalize student skills for case-insensitive matching
    normalized_student_skills = {s.strip().lower() for s in student_skills if s.strip()}

    required_skills = role_df['skill'].tolist()
    weights_array = role_df['weight'].to_numpy(dtype=np.float64)

    # Boolean mask: 1 if student has skill (fuzzy / substring matching supported)
    match_mask = np.zeros(len(required_skills), dtype=bool)
    for idx, req_skill in enumerate(required_skills):
        req_clean = req_skill.lower()
        # Direct match or substring match (e.g. 'Python' in 'Python 3')
        if any(req_clean == s or req_clean in s or s in req_clean for s in normalized_student_skills):
            match_mask[idx] = True

    # Vectorized weighted calculation using NumPy
    total_weights_required = float(np.sum(weights_array))
    weights_demonstrated = float(np.sum(weights_array[match_mask]))
    
    if total_weights_required > 0:
        coverage_score = float((weights_demonstrated / total_weights_required) * 100.0)
    else:
        coverage_score = 0.0

    matched_count = int(np.sum(match_mask))
    total_required = len(required_skills)
    unweighted_coverage = float((matched_count / total_required * 100.0)) if total_required > 0 else 0.0

    return {
        'role': role_df.iloc[0]['role'],
        'coverage_score': round(float(np.clip(coverage_score, 0.0, 100.0)), 1),
        'unweighted_coverage': round(unweighted_coverage, 1),
        'total_skills_required': total_required,
        'matched_skills_count': matched_count,
        'missing_skills_count': total_required - matched_count,
        'weights_demonstrated': round(weights_demonstrated, 1),
        'total_weights_required': round(total_weights_required, 1),
        'formula_explanation': (
            f"Skill Coverage Score = (Weighted Points Demonstrated ({weights_demonstrated:.1f}) / "
            f"Total Required Weighted Points ({total_weights_required:.1f})) × 100 = {coverage_score:.1f}%"
        )
    }

def compare_student_skills(
    student_skills: List[str],
    target_role: str,
    df: Optional[pd.DataFrame] = None
) -> Dict[str, Any]:
    """
    5. Compares student skills against career requirements.
    Categorizes into:
      - Mastered / Present Skills
      - Needs Improvement (basic knowledge indicated)
      - Completely Missing Skills
      - Priority Skills to Learn First (missing skills with weight >= 4)
      - Suggested Projects for missing skills
    """
    if df is None:
        df = load_and_validate_dataset()

    role_df = df[df['role'].str.lower() == target_role.lower()].copy()
    if role_df.empty:
        return {
            'role': target_role,
            'has_skills': [],
            'needs_improvement': [],
            'missing_skills': [],
            'priority_skills': [],
            'suggested_projects': [],
            'metrics': calculate_skill_coverage_and_readiness(student_skills, target_role, df)
        }

    normalized_student_skills = [s.strip().lower() for s in student_skills if s.strip()]

    has_skills = []
    needs_improvement = []
    missing_skills = []

    for _, row in role_df.iterrows():
        skill_name = row['skill']
        category = row['category']
        weight = int(row['weight'])
        desc = row.get('description', '')

        # Check for qualification level:
        # e.g. "Basic SQL" or "Beginner Python" means needs improvement
        match_found = False
        is_partial = False

        for s in normalized_student_skills:
            clean_s = s.lower()
            clean_target = skill_name.lower()
            if clean_target in clean_s or clean_s in clean_target:
                match_found = True
                if any(w in clean_s for w in ['basic', 'beginner', 'elementary', 'intro', 'familiar']):
                    is_partial = True
                break

        item = {
            'skill': skill_name,
            'category': category,
            'weight': weight,
            'description': desc
        }

        if match_found:
            if is_partial:
                needs_improvement.append(item)
            else:
                has_skills.append(item)
        else:
            missing_skills.append(item)

    # Priority skills: missing skills sorted descending by weight (>= 4 first)
    missing_df = pd.DataFrame(missing_skills) if missing_skills else pd.DataFrame(columns=['skill', 'category', 'weight', 'description'])
    if not missing_df.empty:
        missing_df = missing_df.sort_values(by='weight', ascending=False)
        priority_skills = missing_df[missing_df['weight'] >= 4].to_dict(orient='records')
    else:
        priority_skills = []

    # Map suggested projects tailored to the target role and missing skills
    suggested_projects = _generate_project_recommendations(target_role, missing_skills)

    metrics = calculate_skill_coverage_and_readiness(student_skills, target_role, df)

    return {
        'role': role_df.iloc[0]['role'],
        'has_skills': has_skills,
        'needs_improvement': needs_improvement,
        'missing_skills': missing_skills,
        'priority_skills': priority_skills,
        'suggested_projects': suggested_projects,
        'metrics': metrics
    }

def summarize_missing_skills_across_roles(
    student_skills: List[str],
    df: Optional[pd.DataFrame] = None
) -> Dict[str, Any]:
    """
    6. Summarizes missing skills across all career roles in the dataset using Pandas and NumPy.
    Finds the most universally missing skills across tech careers.
    """
    if df is None:
        df = load_and_validate_dataset()

    if df.empty:
        return {'top_universal_gaps': [], 'role_summaries': {}}

    normalized_student = {s.strip().lower() for s in student_skills if s.strip()}

    # Compute missing indicator column using Pandas vectorized lambda
    def is_present(skill: str) -> bool:
        s_clean = skill.lower()
        return any(s_clean in st or st in s_clean for st in normalized_student)

    df_copy = df.copy()
    df_copy['is_present'] = df_copy['skill'].apply(is_present)
    missing_subset = df_copy[~df_copy['is_present']]

    # Universal missing skills count across roles
    if not missing_subset.empty:
        gap_counts = missing_subset.groupby('skill').agg(
            role_count=('role', 'count'),
            avg_weight=('weight', 'mean')
        ).reset_index()

        # Weighted gap urgency = role_count * avg_weight
        gap_counts['urgency_score'] = np.round(gap_counts['role_count'] * gap_counts['avg_weight'], 1)
        gap_counts = gap_counts.sort_values(by='urgency_score', ascending=False).head(8)
        top_universal_gaps = gap_counts.to_dict(orient='records')
    else:
        top_universal_gaps = []

    # Role-level summaries
    role_group = df_copy.groupby('role').agg(
        total_skills=('skill', 'count'),
        matched_skills=('is_present', 'sum'),
        total_weight=('weight', 'sum')
    ).reset_index()

    role_group['coverage_pct'] = np.round(
        (role_group['matched_skills'] / role_group['total_skills']) * 100, 1
    )

    return {
        'top_universal_gaps': top_universal_gaps,
        'role_summaries': role_group.to_dict(orient='records')
    }

def generate_analytics_summary(df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
    """
    7. Generates structured data for charts, reports, and the analytics demonstration page.
    Includes:
      - Total career roles
      - Total unique skills
      - Top 10 most in-demand skills across roles
      - Category distribution
      - Skill weight distribution
      - Average required skills per role
    """
    if df is None:
        df = load_and_validate_dataset()

    if df.empty:
        return {
            'total_roles': 0,
            'total_skills': 0,
            'top_skills': [],
            'category_breakdown': [],
            'role_skill_counts': [],
            'weight_distribution': []
        }

    total_roles = int(df['role'].nunique())
    total_skills = int(df['skill'].nunique())

    # Top in-demand skills
    skill_demand = df.groupby('skill').agg(
        frequency=('role', 'count'),
        avg_weight=('weight', 'mean')
    ).reset_index().sort_values(by=['frequency', 'avg_weight'], ascending=[False, False]).head(10)

    top_skills = [
        {
            'skill': row['skill'],
            'roles_count': int(row['frequency']),
            'percentage': round((int(row['frequency']) / total_roles) * 100, 1),
            'avg_weight': round(float(row['avg_weight']), 2)
        }
        for _, row in skill_demand.iterrows()
    ]

    # Category breakdown for Pie / Doughnut charts
    cat_summary = df.groupby('category').size().reset_index(name='count')
    category_breakdown = [
        {'name': row['category'], 'value': int(row['count'])}
        for _, row in cat_summary.iterrows()
    ]

    # Role skill counts for Bar charts
    role_counts = df.groupby('role').size().reset_index(name='skill_count')
    role_skill_counts = [
        {'role': row['role'], 'skills': int(row['skill_count'])}
        for _, row in role_counts.iterrows()
    ]

    # Skill weight distribution using NumPy histogram
    weights = df['weight'].to_numpy()
    hist, bin_edges = np.histogram(weights, bins=[1, 2, 3, 4, 5, 6])
    weight_distribution = [
        {'rating': f'{int(bin_edges[i])} Star', 'count': int(hist[i])}
        for i in range(len(hist))
    ]

    return {
        'total_roles': total_roles,
        'total_skills': total_skills,
        'top_skills': top_skills,
        'category_breakdown': category_breakdown,
        'role_skill_counts': role_skill_counts,
        'weight_distribution': weight_distribution,
        'avg_skills_per_role': round(float(len(df) / total_roles), 1) if total_roles > 0 else 0.0
    }

def handle_empty_or_invalid_data() -> pd.DataFrame:
    """
    8. Handles empty datasets and invalid inputs safely with a resilient default schema.
    """
    return pd.DataFrame(columns=['role', 'skill', 'category', 'weight', 'description'])

def _generate_project_recommendations(target_role: str, missing_skills: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Helper to generate contextual project ideas addressing missing skills."""
    role_lower = target_role.lower()
    missing_names = [m['skill'] for m in missing_skills]
    missing_str = ", ".join(missing_names[:3]) if missing_names else "Core skills"

    projects_by_role = {
        'machine learning engineer': [
            {
                'title': 'End-to-End Predictive ML Pipeline with FastAPI & Docker',
                'description': f'Build and containerize a customer churn or credit risk prediction model. Focuses on: {missing_str}.',
                'difficulty': 'Intermediate',
                'estimated_hours': 20
            },
            {
                'title': 'Model Evaluation & Drift Monitoring Dashboard',
                'description': 'Develop automated cross-validation, ROC-AUC tracking, and data drift detection.',
                'difficulty': 'Advanced',
                'estimated_hours': 25
            }
        ],
        'data analyst': [
            {
                'title': 'E-Commerce Sales Performance & Retention Dashboard',
                'description': f'Analyze 100K+ transactional rows with SQL and Pandas, presenting insights via interactive charts. Addresses: {missing_str}.',
                'difficulty': 'Beginner - Intermediate',
                'estimated_hours': 15
            },
            {
                'title': 'A/B Testing & Statistical Hypothesis Experiment',
                'description': 'Design statistical significance tests, p-value calculations, and conversion rate analysis.',
                'difficulty': 'Intermediate',
                'estimated_hours': 18
            }
        ],
        'data scientist': [
            {
                'title': 'Customer Segmentation & Clustering Engine',
                'description': f'Implement PCA and K-Means/DBSCAN clustering with feature engineering. Solves gaps in: {missing_str}.',
                'difficulty': 'Intermediate',
                'estimated_hours': 22
            }
        ],
        'web developer': [
            {
                'title': 'Responsive SaaS Analytics Web Portal',
                'description': f'Modern React.js web application with Tailwind CSS, REST API integration, and dynamic charts. Covers: {missing_str}.',
                'difficulty': 'Intermediate',
                'estimated_hours': 18
            }
        ],
        'python developer': [
            {
                'title': 'High-Throughput RESTful Microservice with Flask & SQLAlchemy',
                'description': f'Develop a modular API with JWT authentication, database migrations, and PyTest coverage. Targets: {missing_str}.',
                'difficulty': 'Intermediate',
                'estimated_hours': 16
            }
        ]
    }

    # Match role or provide generic project
    for key, projs in projects_by_role.items():
        if key in role_lower:
            return projs

    return [
        {
            'title': f'{target_role} Hands-On Portfolio Application',
            'description': f'Build a practical application integrating key role requirements, specifically addressing: {missing_str}.',
            'difficulty': 'Intermediate',
            'estimated_hours': 20
        }
    ]
