
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.runnables import RunnableLambda

from utils.models import BuiltContext, IntentType
from utils.logger import logger
from config.settings import OLLAMA_BASE_URL, RESPONDER_MODEL, DANGEROUS_RESPONSE_PATTERNS


SAFETY_FALLBACK = (
    "I'm not able to provide specific medical advice for this question. "
    "Please consult with a qualified healthcare professional who can "
    "evaluate your specific situation. If this is an emergency, "
    "call your local emergency number or go to your nearest emergency room."
)

TEMPERATURE_MAP = {
    IntentType.GREETING:        0.7,
    IntentType.FAREWELL:        0.7,
    IntentType.WELLNESS_ADVICE: 0.5,
    IntentType.MENTAL_HEALTH:   0.4,
    IntentType.APPOINTMENT:     0.4,
    IntentType.GENERAL_MEDICAL: 0.3,
    IntentType.OUT_OF_SCOPE:    0.6,
    IntentType.SYMPTOM_CHECK:   0.2,
    IntentType.MEDICATION_INFO: 0.1,
    IntentType.EMERGENCY:       0.1,
}


class ResponseGenerator:

    def _build_messages(self, context: BuiltContext) -> list:

        messages = [SystemMessage(content=context.system_prompt)]

        for msg in context.conversation_history:
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                messages.append(AIMessage(content=msg.content))

        return messages

    def _safety_check(self, response: str) -> tuple[bool, list[str]]:

        lower = response.lower()
        violations = [p for p in DANGEROUS_RESPONSE_PATTERNS if p.lower() in lower]
        is_safe = len(violations) == 0

        if not is_safe:
            logger.warning(f"Safety violations: {violations}")
        else:
            logger.debug("Safety check passed")

        return is_safe, violations

    async def generate(self, context: BuiltContext) -> tuple[str, bool]:

        logger.info(f"Generating response for intent={context.intent.value}")

        temperature = TEMPERATURE_MAP.get(context.intent, 0.3)

        llm = ChatOllama(
            base_url=OLLAMA_BASE_URL,
            model=RESPONDER_MODEL,
            temperature=temperature,
            num_predict=600,
        )

        messages = self._build_messages(context)

        try:
            ai_msg = await llm.ainvoke(messages)
            response = ai_msg.content.strip()

            if not response:
                raise RuntimeError("Ollama returned empty response")

        except Exception as e:
            logger.error(f"Responder LLM error: {e}")
            return (
                "I'm having trouble connecting to the AI model. "
                "Please ensure Ollama is running (`ollama serve`) and try again.",
                True
            )

        is_safe, violations = self._safety_check(response)

        if not is_safe:
            logger.warning(f"Unsafe response rejected. Violations: {violations}")
            logger.warning(f"Rejected text: {response[:200]}")
            return SAFETY_FALLBACK, False

        return response, True

    def as_runnable(self) -> RunnableLambda:
        return RunnableLambda(self.generate)

response_generator = ResponseGenerator()
responder_runnable = response_generator.as_runnable()