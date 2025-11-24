# agents/recommend_agent.py
import uuid
from typing import List, Dict, Any, Optional

from agents.skill_agent import ALL_SKILLS, SKILL_CATALOG


# Map mastery -> difficulty suggestion
def mastery_to_difficulty(m: float) -> str:
    if m < 0.3:
        return "Easy"
    if m < 0.6:
        return "Medium"
    return "Hard"


class RecommendationAgent:
    """
    Generate practice-only recommendations.
    Each recommendation: NO explanations, only question + hint.
    Uses llm_agent.generate() and prevents repeating problems.
    """

    def __init__(self):
        pass

    def generate_recommendations(
        self,
        history: List[Dict[str, Any]],
        skill_estimates: Dict[str, float],
        llm_agent,
        top_k: int = 5,
        subject_filter: Optional[str] = None,
        difficulty_filter: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        history: student's session history
        skill_estimates: skill -> mastery score
        subject_filter: "Mathematics", "Physics", etc.
        difficulty_filter: "Easy", "Medium", "Hard"
        context: stores given_problems so questions don't repeat
        """

        if context is None:
            context = {}

        given_problems = context.get("given_problems", {})

        # Default mastery if none given
        estimates = skill_estimates or {s: 0.65 for s in ALL_SKILLS}

        # Sort by lowest mastery first
        sorted_skills = sorted(estimates.items(), key=lambda x: x[1])

        recommendations = []

        for skill, mastery in sorted_skills:

            # --- Subject Filtering ---
            if subject_filter:
                allowed_skills = SKILL_CATALOG.get(subject_filter, [])
                if skill not in allowed_skills:
                    continue

            # --- Difficulty Filtering ---
            difficulty = mastery_to_difficulty(mastery)
            if difficulty_filter and difficulty != difficulty_filter:
                continue

            # --- Build LLM Prompt (Practice Only) ---
            prompt = (
                f"Generate a practice exercise for skill '{skill}'. "
                f"The student's mastery is {mastery:.2f}. "
                f"Provide ONLY:\n"
                f"- one question\n"
                f"- one short hint\n"
                f"Do NOT give the solution. Do NOT add explanation."
            )

            lm_context = {
                "skill": skill,
                "difficulty": difficulty,
                "given_problems": given_problems
            }

            # --- Call LLM ---
            out = llm_agent.generate(prompt, context=lm_context)
            text = out.get("text", "")
            given_problems = out.get("given_problems", given_problems)

            # --- Create Recommendation Card ---
            recommendations.append({
                "id": str(uuid.uuid4()),
                "skill": skill,
                "estimated_mastery": mastery,
                "difficulty": difficulty,
                "title": text.splitlines()[0] if text else f"Practice: {skill}",
                "excerpt": text
            })

            if len(recommendations) >= top_k:
                break

        # Save updated non-repeat memory
        context["given_problems"] = given_problems

        return recommendations