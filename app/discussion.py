from .adviser import Adviser


class DiscussionModule:
    """Creates useful discussion turns without deciding for the human."""

    def __init__(self, adviser: Adviser):
        self.adviser = adviser

    def discuss(self, question: str, context: dict) -> dict:
        response = self.adviser.answer(question, {**context, "mode": "general_discussion"})
        return {
            "question": question,
            "answer": response["answer"],
            "answer_source": response["answer_source"],
            "memories_used": response["memories_used"],
            "follow_up_questions": self._follow_ups(question),
            "human_role": "choose, correct, or continue the discussion",
            "decision_made_for_human": False,
        }

    @staticmethod
    def _follow_ups(question: str) -> list[str]:
        lowered = question.casefold()
        if any(word in lowered for word in ("incident", "failure", "outage", "error")):
            return [
                "What changed immediately before this happened?",
                "Who or what was affected?",
                "What evidence should we preserve before changing anything?",
            ]
        if any(word in lowered for word in ("plan", "project", "build", "deploy")):
            return [
                "What outcome would make this plan successful?",
                "What is the smallest reversible first step?",
                "What risks need human approval before execution?",
            ]
        if any(word in lowered for word in ("feel", "feeling", "worried", "stressed")):
            return [
                "What happened immediately before you felt this way?",
                "What support would be useful right now?",
                "Would you like this recorded as context for a later discussion?",
            ]
        return [
            "What matters most about this question?",
            "What facts or constraints should we consider?",
            "Would you like options, a plan, or a deeper explanation?",
        ]