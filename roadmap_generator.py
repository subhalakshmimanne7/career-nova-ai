"""
roadmap_generator.py
Generates personalized 30-day, 60-day, and 90-day learning roadmaps.
Supports deterministic rule-based templates tailored to target careers,
missing skills, experience levels, and study hours, with real reputable resources.
"""

from typing import List, Dict, Any, Optional

# Verified curated documentation and resource links (real, permanent educational resources)
CURATED_RESOURCES = {
    'python': {'title': 'Official Python Documentation & Tutorial', 'url': 'https://docs.python.org/3/tutorial/'},
    'pandas': {'title': 'Pandas Official 10-Minute User Guide', 'url': 'https://pandas.pydata.org/docs/user_guide/10min.html'},
    'numpy': {'title': 'NumPy Official Quickstart Tutorial', 'url': 'https://numpy.org/doc/stable/user/quickstart.html'},
    'scikit-learn': {'title': 'Scikit-learn Machine Learning Tutorials', 'url': 'https://scikit-learn.org/stable/tutorial/index.html'},
    'sql': {'title': 'PostgreSQL Tutorial & Interactive Exercises', 'url': 'https://www.postgresqltutorial.com/'},
    'git': {'title': 'Pro Git Book (Official Free Edition)', 'url': 'https://git-scm.com/book/en/v2'},
    'react': {'title': 'React.js Official Quick Start & Documentation', 'url': 'https://react.dev/learn'},
    'javascript': {'title': 'MDN Web Docs: Modern JavaScript Handbook', 'url': 'https://developer.mozilla.org/en-US/docs/Web/JavaScript'},
    'flask': {'title': 'Flask Official Quickstart & Documentation', 'url': 'https://flask.palletsprojects.com/en/latest/quickstart/'},
    'docker': {'title': 'Docker Official Getting Started Guide', 'url': 'https://docs.docker.com/get-started/'},
    'machine learning': {'title': 'Google Machine Learning Crash Course', 'url': 'https://developers.google.com/machine-learning/crash-course'},
    'deep learning': {'title': 'PyTorch Official Beginner Tutorials', 'url': 'https://pytorch.org/tutorials/beginner/basics/intro.html'},
    'cybersecurity': {'title': 'OWASP Top 10 Web Application Security', 'url': 'https://owasp.org/www-project-top-ten/'},
    'data structures': {'title': 'FreeCodeCamp DSA & Algorithmic Problem Solving', 'url': 'https://www.freecodecamp.org/news/learn-data-structures-and-algorithms/'}
}

class RoadmapGenerator:
    def __init__(self):
        pass

    def generate_roadmap(
        self,
        target_role: str,
        missing_skills: List[str],
        duration_days: int = 30,
        experience_level: str = 'Intermediate',
        study_hours_per_week: int = 15
    ) -> Dict[str, Any]:
        """
        Builds a customized roadmap broken down into progressive phases.
        duration_days: 30, 60, or 90.
        """
        # Determine number of phases and duration per phase
        if duration_days <= 30:
            num_phases = 3
            phase_duration_days = 10
            phase_titles = [
                "Phase 1: Core Foundation & Concept Clarification",
                "Phase 2: Deep Dive, Tools & Applied Techniques",
                "Phase 3: Portfolio Capstone & Interview Readiness"
            ]
        elif duration_days <= 60:
            num_phases = 4
            phase_duration_days = 15
            phase_titles = [
                "Phase 1: Fundamental Concepts & Skill Baseline",
                "Phase 2: Core Engineering & Algorithmic Practice",
                "Phase 3: Advanced Tools, Frameworks & Pipelines",
                "Phase 4: Capstone Engineering & Production Deployment"
            ]
        else:  # 90 days
            num_phases = 6
            phase_duration_days = 15
            phase_titles = [
                "Phase 1: Comprehensive Foundations & Tool Setup",
                "Phase 2: Data Wrangling & Algorithmic Modeling",
                "Phase 3: Framework Specialization & Best Practices",
                "Phase 4: System Architecture & Testing Pipelines",
                "Phase 5: Production Capstone Project",
                "Phase 6: Mock Interviews, Portfolio & System Review"
            ]

        # Allocate missing skills across early/middle phases
        skills_to_cover = missing_skills if missing_skills else [f"{target_role} Core Architecture"]
        
        phases = []
        task_counter = 1

        for p_idx in range(num_phases):
            p_start_day = (p_idx * phase_duration_days) + 1
            p_end_day = min((p_idx + 1) * phase_duration_days, duration_days)
            title = phase_titles[p_idx]

            # Pick target skills for this phase
            phase_skill = skills_to_cover[p_idx % len(skills_to_cover)]
            resource_item = self._find_best_resource(phase_skill)

            # Generate structured weekly tasks for this phase
            tasks = []
            
            task_1_id = f"task_{task_counter}"
            task_counter += 1
            tasks.append({
                'id': task_1_id,
                'title': f"Master fundamental principles of {phase_skill}",
                'description': f"Review official documentation and core conventions for {phase_skill}.",
                'topics': [f"{phase_skill} syntax/concepts", "Syntax structure", "Standard patterns"],
                'estimated_hours': round(study_hours_per_week / 3, 1),
                'practice_exercise': f"Complete 5 coding exercises or conceptual reviews on {phase_skill}."
            })

            task_2_id = f"task_{task_counter}"
            task_counter += 1
            tasks.append({
                'id': task_2_id,
                'title': f"Hands-on implementation lab for {phase_skill}",
                'description': f"Build a practical module integrating {phase_skill} with version control and testing.",
                'topics': ["Modular design", "Edge-case handling", "Unit testing"],
                'estimated_hours': round(study_hours_per_week / 3, 1),
                'practice_exercise': f"Write unit tests and commit working code to a GitHub repository."
            })

            if p_idx == num_phases - 1:
                # Final capstone task
                task_3_id = f"task_{task_counter}"
                task_counter += 1
                tasks.append({
                    'id': task_3_id,
                    'title': f"Publish {target_role} Capstone Portfolio & Documentation",
                    'description': "Document architecture, deploy the project, and prepare behavioral/technical talking points.",
                    'topics': ["README documentation", "Architecture diagram", "Interview prep"],
                    'estimated_hours': round(study_hours_per_week / 3, 1),
                    'practice_exercise': "Deploy your project live and perform a 5-minute recorded code walkthrough."
                })

            phase_obj = {
                'phase_number': p_idx + 1,
                'title': title,
                'day_range': f"Days {p_start_day} - {p_end_day}",
                'focus_skill': phase_skill,
                'learning_resource': resource_item,
                'milestone': f"Milestone {p_idx + 1}: Working code sample and verified proficiency in {phase_skill}.",
                'tasks': tasks
            }
            phases.append(phase_obj)

        total_tasks = task_counter - 1

        return {
            'target_role': target_role,
            'duration_days': duration_days,
            'experience_level': experience_level,
            'study_hours_per_week': study_hours_per_week,
            'total_phases': len(phases),
            'total_tasks': total_tasks,
            'completed_tasks': [],
            'progress_percentage': 0.0,
            'phases': phases
        }

    def _find_best_resource(self, skill_name: str) -> Dict[str, str]:
        s_lower = skill_name.lower()
        for key, res in CURATED_RESOURCES.items():
            if key in s_lower:
                return res
        return {
            'title': f'{skill_name} Official Reference & Guide',
            'url': 'https://developer.mozilla.org/' if 'web' in s_lower or 'css' in s_lower else 'https://docs.python.org/3/'
        }
