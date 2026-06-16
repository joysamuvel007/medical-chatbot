from langchain_core.runnables import RunnableLambda

from utils.models import ClassificationResult, IntentType, EmergencyLevel
from utils.logger import logger
from config.settings import EMERGENCY_ALERT_LEVEL, EMERGENCY_NUMBERS_BY_REGION


def get_emergency_phrase(region: str = None) -> str:
    if region:
        number = EMERGENCY_NUMBERS_BY_REGION.get(region.strip().lower())
        if number:
            return f"call {number} (your local emergency number)"
    return (
        "call your local emergency number "
        "(e.g. 911 in the US, 112 in the EU/India, 999 in the UK, 000 in Australia)"
    )


def build_emergency_message(level: EmergencyLevel, region: str = None) -> str:
    phrase = get_emergency_phrase(region)
    if level == EmergencyLevel.CRITICAL:
        return (
            f"This sounds like it could be a medical emergency. "
            f"Please {phrase} immediately or go to your nearest "
            f"emergency room right away. Do not wait."
        )
    if level == EmergencyLevel.URGENT:
        return (
            f"Based on what you've described, please seek medical attention "
            f"soon — urgent care or an emergency room. If symptoms worsen "
            f"suddenly, {phrase}."
        )
    return ""


class DecisionEngine:
    def decide(
        self,
        classification: ClassificationResult,
        session_has_history: bool = False,
        region: str = None,
    ) -> dict:

        intent = classification.intent
        level = classification.emergency_level

        logger.info(f"Decision Engine: intent={intent.value}, level={level.value}")
        if level == EmergencyLevel.CRITICAL:
            logger.warning("CRITICAL → emergency_stop route")
            return {
                "action": "emergency_stop",
                "needs_search": False,
                "needs_memory": False,
                "emergency_message": build_emergency_message(EmergencyLevel.CRITICAL, region),
                "emergency_level": level.value,
                "skip_llm": True,
                "intent": intent,
            }
        if level >= EMERGENCY_ALERT_LEVEL:
            logger.warning("URGENT → respond with warning banner")
            return {
                "action": "respond",
                "needs_search": False,
                "needs_memory": False,
                "emergency_message": build_emergency_message(EmergencyLevel.URGENT, region),
                "emergency_level": level.value,
                "skip_llm": False,
                "intent": intent,
            }

        if intent in (IntentType.GREETING, IntentType.FAREWELL):
            return {
                "action": "respond",
                "needs_search": False,
                "needs_memory": False,
                "emergency_message": None,
                "emergency_level": 0,
                "skip_llm": False,
                "intent": intent,
            }

        if intent == IntentType.OUT_OF_SCOPE:
            return {
                "action": "respond",
                "needs_search": False,
                "needs_memory": False,
                "emergency_message": None,
                "emergency_level": 0,
                "skip_llm": False,
                "intent": intent,
            }

        emergency_message = None
        if level == EmergencyLevel.MODERATE:
            emergency_message = (
                "Some of what you've described may benefit from a doctor's "
                "evaluation. I'll ask a few questions to help assess urgency."
            )

        needs_memory = classification.needs_memory and session_has_history

        logger.info(
            f"Medical route: search={classification.needs_web_search}, "
            f"memory={needs_memory}"
        )

        return {
            "action": "respond",
            "needs_search": classification.needs_web_search,
            "needs_memory": needs_memory,
            "emergency_message": emergency_message,
            "emergency_level": level.value,
            "skip_llm": False,
            "intent": intent,
        }

    def as_runnable(self, session_has_history: bool = False, region: str = None) -> RunnableLambda:
        def _decide(classification: ClassificationResult) -> dict:
            return self.decide(classification, session_has_history, region)

        return RunnableLambda(_decide)


decision_engine = DecisionEngine()