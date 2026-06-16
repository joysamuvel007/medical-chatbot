import json
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableLambda
from langchain_core.exceptions import OutputParserException

from utils.models import PreprocessedInput, ClassificationResult, IntentType, EmergencyLevel
from utils.logger import logger
from config.settings import OLLAMA_BASE_URL, CLASSIFIER_MODEL, VALID_INTENTS


CLASSIFICATION_SYSTEM_PROMPT = """You are a medical intent classifier.
Your ONLY job is to analyze a user message and return a JSON object.
You must return ONLY valid JSON — no explanation, no markdown, no extra text.

JSON schema to return:
{{
  "intent": string,
  "emergency_level": int,
  "needs_web_search": bool,
  "needs_memory": bool,
  "confidence": float,
  "keywords_detected": []
}}

Valid intents:
- greeting, symptom_check, medication_info, appointment,
  wellness_advice, mental_health, emergency, general_medical,
  farewell, out_of_scope

Emergency level calibration (CRITICAL — read carefully):
- 0: Not urgent (greeting, wellness, mild single symptom with no details)
- 1: Mild — a single symptom mentioned with NO severity/duration details
     e.g. "I have chest pain" alone → level 1, ask follow-up questions
     e.g. "I have a headache" alone → level 1
- 2: Moderate — symptoms + some detail, needs doctor but not today
     e.g. "I've had a fever and cough for 3 days" → level 2
- 3: Urgent — multiple symptoms OR concerning descriptions (go to ER today)
     e.g. "high fever, can't keep food down, very weak for 2 days" → level 3
- 4: Critical — MULTIPLE unambiguous red-flag signs together
     e.g. "chest pain radiating to my arm AND can't breathe AND sweating" → level 4
     e.g. "someone is unconscious and not breathing" → level 4
     DO NOT assign level 4 for a single symptom keyword alone.

Tier 2 context flags (may be present in the input):
If the message contains context-dependent keywords like "chest pain",
"shortness of breath", "confusion", etc., you will see them listed.
Use the FULL message context to decide the level — not just the keyword.
"I have chest pain" alone → level 1 (ask questions).
"Crushing chest pain, radiating to jaw, sweating" → level 4.

Return ONLY the JSON object. Nothing before or after it."""


class OllamaClassifier:

    def __init__(self):
        self.llm = ChatOllama(
            base_url=OLLAMA_BASE_URL,
            model=CLASSIFIER_MODEL,
            temperature=0.1,
            num_predict=300,
        )

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", CLASSIFICATION_SYSTEM_PROMPT),
            ("human", (
                'Message: "{message}"\n'
                '{tier2_context}'
            )),
        ])

        self.parser = JsonOutputParser()
        self.chain = self.prompt | self.llm | self.parser

    def _build_emergency_result(self, keywords: list) -> ClassificationResult:
        return ClassificationResult(
            intent=IntentType.EMERGENCY,
            emergency_level=EmergencyLevel.CRITICAL,
            needs_web_search=False,
            needs_memory=False,
            confidence=1.0,
            keywords_detected=keywords,
            raw_llm_output="[FAST PATH: tier1 emergency keyword]"
        )

    def _build_fallback_result(self, error: str) -> ClassificationResult:
        return ClassificationResult(
            intent=IntentType.GENERAL_MEDICAL,
            emergency_level=EmergencyLevel.NONE,
            needs_web_search=False,
            needs_memory=False,
            confidence=0.3,
            keywords_detected=[],
            raw_llm_output=error
        )

    def _validate(self, parsed: dict, raw: str) -> ClassificationResult:
        raw_intent = parsed.get("intent", "general_medical")
        if raw_intent not in VALID_INTENTS:
            raw_intent = "general_medical"

        raw_level = max(0, min(4, int(parsed.get("emergency_level", 0))))

        def to_bool(v):
            return v.lower() == "true" if isinstance(v, str) else bool(v)

        confidence = max(0.0, min(1.0, float(parsed.get("confidence", 0.5))))
        keywords = parsed.get("keywords_detected", [])
        if not isinstance(keywords, list):
            keywords = []

        return ClassificationResult(
            intent=IntentType(raw_intent),
            emergency_level=EmergencyLevel(raw_level),
            needs_web_search=to_bool(parsed.get("needs_web_search", False)),
            needs_memory=to_bool(parsed.get("needs_memory", False)),
            confidence=confidence,
            keywords_detected=keywords,
            raw_llm_output=raw,
        )

    async def classify(self, preprocessed: PreprocessedInput) -> ClassificationResult:
        if preprocessed.has_emergency_keyword:
            logger.warning(f"Tier1 fast-path: {preprocessed.detected_emergency_words}")
            return self._build_emergency_result(preprocessed.detected_emergency_words)
        
        tier2_context = ""
        if preprocessed.possible_emergency_words:
            tier2_context = (
                f"Context-dependent keywords detected: "
                f"{', '.join(preprocessed.possible_emergency_words)}. "
                f"Use the full message to calibrate emergency_level — "
                f"do NOT auto-assign level 4 for these alone."
            )

        logger.info(f"Classifying with LangChain [{CLASSIFIER_MODEL}]...")

        try:
            parsed: dict = await self.chain.ainvoke({
                "message": preprocessed.cleaned,
                "tier2_context": tier2_context,
            })
            raw = json.dumps(parsed)
            result = self._validate(parsed, raw)
            logger.info(
                f"Classification → intent={result.intent.value}, "
                f"emergency={result.emergency_level.value}, "
                f"confidence={result.confidence:.2f}"
            )
            return result

        except (OutputParserException, Exception) as e:
            logger.error(f"Classifier error: {e}")
            return self._build_fallback_result(str(e))

    def as_runnable(self) -> RunnableLambda:
        return RunnableLambda(self.classify)

classifier = OllamaClassifier()
classifier_runnable = classifier.as_runnable()