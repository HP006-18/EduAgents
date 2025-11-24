# agents/llm_agent.py
import uuid
import random
from typing import Dict, Any, List, Tuple, Optional


class LLMAgent:
    def __init__(self, mock: bool = True, model_name: str = "mock"):
        self.mock = mock
        self.model_name = model_name

        self.current_subject: Optional[str] = None
        self.current_topic: Optional[str] = None

        # Stores problems already given: { "Subject|Topic": [(q,h)] }
        self.given_problems: Dict[str, List[Tuple[str, str]]] = {}

    # MAIN GENERATE FUNCTION --------------------------------------------------
    def generate(self, prompt: str, context: Dict[str, Any] = None, max_tokens: int = 200) -> Dict[str, Any]:
        if context is None:
            context = {}

        if self.mock:
            text = self._mock_response(prompt, context)
            return {
                "id": str(uuid.uuid4()),
                "text": text,
                "raw": text,
                "given_problems": self.given_problems
            }

        return {"id": str(uuid.uuid4()), "text": "Real LLM not configured.", "raw": ""}

    # -------------------------------------------------------------------------
    # MOCK LOGIC
    # -------------------------------------------------------------------------
    def _mock_response(self, prompt: str, context: Dict[str, Any]) -> str:
        lower = (prompt.lower()).strip()

        # sync incoming given_problems
        incoming_given = context.get("given_problems")
        if isinstance(incoming_given, dict):
            for key, vals in incoming_given.items():
                exist = self.given_problems.setdefault(key, [])
                for item in vals:
                    if item not in exist:
                        exist.append(item)

        # TOPIC SETTING -------------------------------------------------------
        if lower.startswith("start topic:"):
            raw = prompt.split(":", 1)[1].strip()
            parts = [p.strip() for p in raw.split("|")]

            if len(parts) == 2:
                self.current_subject, self.current_topic = parts
            else:
                self.current_subject, self.current_topic = None, parts[0]

            return f"Topic set to '{self.current_topic}' (Subject: {self.current_subject}). You can now ask for explanations or practice problems."

        # PRACTICE PROBLEM ASKING --------------------------------------------
        practice_triggers = [
            "practice problem", "another problem", "practice exercise",
            "give me a basic problem"
        ]
        if any(t in lower for t in practice_triggers):
            return self._serve_practice_problem(context)

        # EXPLANATION REQUEST -------------------------------------------------
        explain_triggers = ["explain", "define", "what is", "explain more", "show me the solution"]
        if any(t in lower for t in explain_triggers):
            direct = self._direct_answer(prompt)
            if direct:
                return direct
            return self._topic_explanation(context)

        # RECOMMENDATION HOOK -------------------------------------------------
        if "generate a practice" in lower:
            skill = context.get("skill") or "General"
            difficulty = context.get("difficulty")
            q, h = self._sample_for_skill(skill, difficulty)
            return f"Practice Question for {skill}:\n• {q}\nHint: {h}"

        # Weak skill fallback
        if isinstance(context.get("skill_estimates"), dict):
            se = context["skill_estimates"]
            top3 = sorted(se.items(), key=lambda x: x[1])[:3]
            if top3:
                return "Top weak skills: " + ", ".join([f"{k}({v:.2f})" for k, v in top3])

        # Default fallback
        return "I'm here to help! Start with 'Start topic: Subject|Topic' or ask for a practice problem."

    # -------------------------------------------------------------------------
    # PRACTICE PROBLEM ENGINE
    # -------------------------------------------------------------------------
    def _serve_practice_problem(self, context: Dict[str, Any]) -> str:
        subj = context.get("subject") or self.current_subject
        topic = context.get("topic") or self.current_topic

        key = f"{subj}|{topic}" if subj else (topic or "General")

        pool = self._get_problem_bank(subj, topic)

        # Filter out previously given problems
        used = self.given_problems.get(key, [])
        remaining = [p for p in pool if p not in used]

        # If exhausted, reset
        if not remaining:
            remaining = pool[:]
            self.given_problems[key] = []

        q, h = random.choice(remaining)
        self.given_problems.setdefault(key, []).append((q, h))

        subj_display = subj or "General"
        topic_display = topic or "General"

        return f"Practice Question for {topic_display} (Subject: {subj_display}):\n• {q}\nHint: {h}"

    # -------------------------------------------------------------------------
    # DIRECT SHORT EXPLANATIONS
    # -------------------------------------------------------------------------
    def _direct_answer(self, prompt: str) -> Optional[str]:
        p = prompt.lower()
        if "newton" in p and "law" in p:
            return "Newton’s laws: (1) Inertia, (2) F = m·a, (3) Action–Reaction."
        if "what is integration" in p:
            return "Integration finds areas, volumes, or antiderivatives."
        if "what is derivative" in p:
            return "The derivative measures rate of change: d/dx xⁿ = n·xⁿ⁻¹."
        return None

    # -------------------------------------------------------------------------
    # TOPIC EXPLANATION ENGINE
    # -------------------------------------------------------------------------
    def _topic_explanation(self, context: Dict[str, Any]) -> str:
        subj = context.get("subject") or self.current_subject
        topic = context.get("topic") or self.current_topic
        return self._get_explanation(subj, topic)

    def _get_explanation(self, subject: Optional[str], topic: Optional[str]) -> str:
        explanations = {
            "fractions": "Fractions represent parts of a whole. Always make denominators equal before operating.",
            "algebra": "Algebra is about solving for unknowns using equations.",
            "integration": "Integration accumulates quantities—area under curves, volumes, etc.",
            "calculus": "Calculus deals with derivatives (rates) and integrals (accumulations).",
            "mechanics": "Mechanics studies forces, motion, and Newton’s laws.",
            "geometry": "Geometry covers shapes, angles, area, perimeter, and volume.",
            "chemistry": "Chemistry studies atoms, molecules, reactions, and equations.",
            "biology": "Biology studies life processes, cells, genetics, and evolution.",
            "history": "History deals with past events, civilizations, and timelines.",
        }

        key = (topic or subject or "").lower()
        return explanations.get(
            key,
            f"Explanation for {topic or 'General'} (Subject: {subject or 'General'}) not available. Try a practice problem!"
        )

    # -------------------------------------------------------------------------
    # SAMPLE PROBLEMS FOR RECOMMENDATION MODE
    # -------------------------------------------------------------------------
    def _sample_for_skill(self, skill: str, difficulty: Optional[str]) -> Tuple[str, str]:
        skill = skill.lower()

        bank = {
            "fractions": ("Add 1/2 + 3/4", "Find a common denominator."),
            "algebra": ("Solve 2x + 5 = 11", "Isolate x."),
            "integration": ("∫ x ln(x) dx", "Use integration by parts."),
            "calculus": ("Differentiate x³", "Use power rule."),
            "mechanics": ("F=20N, m=4kg → a?", "Use a=F/m."),
            "geometry": ("Find area of triangle base=5, height=6", "Use ½bh."),
            "chemistry": ("Balance: H₂ + O₂ → H₂O", "Balance atoms."),
            "biology": ("What is a cell?", "Basic structural unit of life."),
            "history": ("When did India gain independence?", "1947.")
        }

        for k, v in bank.items():
            if k in skill:
                return v

        return ("Solve a basic problem.", "Think carefully!")

    # -------------------------------------------------------------------------
    # PROBLEM BANK FOR NON-REPEATING QUESTIONS
    # -------------------------------------------------------------------------
    def _get_problem_bank(self, subject: Optional[str], topic: Optional[str]) -> List[Tuple[str, str]]:
        pools = {
            "Math|fractions": [
                ("1/2 + 3/4 = ?", "Use common denominator."),
                ("5/6 - 1/3 = ?", "Convert to like terms.")
            ],
            "Math|algebra": [
                ("Solve 2x + 5 = 11", "Isolate x."),
                ("Factor x² - 5x + 6", "Find two numbers that multiply to 6.")
            ],
            "Physics|mechanics": [
                ("F=10N, m=2kg → a=?", "Use a=F/m."),
                ("A car accelerates from 0–20 m/s in 4s → a=?", "Use Δv / t.")
            ],
            "Chemistry|atomic structure": [
                ("How many electrons fit in n=3 shell?", "Use 2n²."),
                ("Define valence shell.", "Outer electron shell.")
            ],
            "Biology|genetics": [
                ("Probability of AB in AaBb x AaBb?", "Use Punnett square."),
                ("Define genotype.", "Genetic makeup.")
            ],
        }

        key = f"{subject}|{topic}"
        return pools.get(key, [("Solve a basic problem.", "Think carefully!")])

    # -------------------------------------------------------------------------
    # PUBLIC HELPER
    # -------------------------------------------------------------------------
    def generate_practice_question(self, skill_name: str, difficulty: Optional[str] = None) -> str:
        return self.generate(
            f"generate a practice exercise for {skill_name}",
            context={"skill": skill_name, "difficulty": difficulty}
        )["text"]

