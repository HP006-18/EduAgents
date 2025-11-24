# agents/skill_agent.py
from typing import Dict, List, Any
import statistics

# Full skill list for Class 8–12
SKILL_CATALOG = {
    "Mathematics": [
        "algebra", "geometry", "trigonometry", "mensuration", "coordinate_geometry",
        "calculus", "probability", "statistics", "fractions", "addition",
        "subtraction", "multiplication", "division", "exponents", "integration"
    ],
    "Physics": [
        "mechanics", "motion", "force_and_laws", "gravitation", "work_energy_power",
        "electricity", "magnetism", "light", "thermodynamics", "optics"
    ],
    "Chemistry": [
        "atomic_structure", "chemical_bonding", "acids_bases_salts", "metals_nonmetals",
        "carbon_compounds", "periodic_table", "solutions", "chemical_reactions"
    ],
    "Biology": [
        "cell", "tissues", "reproduction", "genetics", "evolution",
        "life_processes", "environment", "human_body"
    ],
    "History": ["ancient_india", "medieval_india", "modern_india", "world_history"],
    "Geography": ["climate", "resources", "agriculture", "population", "natural_disasters"],
    "English": ["grammar", "writing", "reading_comprehension", "literature"],
    "CS": ["variables", "basic_programming", "data_structures", "algorithms"]
}

# Flattened skill list
ALL_SKILLS = [skill for skills in SKILL_CATALOG.values() for skill in skills]

class SkillAgent:
    """
    Tracks skill mastery per student dynamically.
    No pre-stored student statistics; all students start with default mastery.
    """

    def __init__(self, default_mastery: float = 0.65):
        self.default_mastery = default_mastery

    def estimate_from_df(self, df) -> Dict[str, float]:
        """
        Accepts a pandas DataFrame with columns 'student_id', 'skill', 'score'.
        Returns dict {skill_name: mastery (0–1)}. Missing skills get default mastery.
        """
        try:
            skills = {}
            for _, row in df.iterrows():
                skill = str(row.get("skill")).strip()
                val = float(row.get("score", 0))
                if val > 1.0:
                    val /= 100.0
                skills.setdefault(skill, []).append(val)
            mastery = {}
            for s in ALL_SKILLS:
                if s in skills:
                    mastery[s] = max(0.0, min(1.0, statistics.mean(skills[s])))
                else:
                    mastery[s] = self.default_mastery
            return mastery
        except Exception:
            return {s: self.default_mastery for s in ALL_SKILLS}

    def estimate_from_history(self, history: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Accepts a list of dicts [{'skill':..., 'score':...}, ...] and returns mastery dict.
        """
        skills = {}
        for row in history:
            skill = str(row.get("skill")).strip()
            val = float(row.get("score", 0))
            if val > 1.0:
                val /= 100.0
            skills.setdefault(skill, []).append(val)
        mastery = {}
        for s in ALL_SKILLS:
            if s in skills:
                mastery[s] = max(0.0, min(1.0, statistics.mean(skills[s])))
            else:
                mastery[s] = self.default_mastery
        return mastery