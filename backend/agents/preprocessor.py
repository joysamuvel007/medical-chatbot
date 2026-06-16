import re
import unicodedata
from langchain_core.runnables import RunnableLambda

from utils.models import PreprocessedInput
from utils.logger import logger
from config.settings import EMERGENCY_KEYWORDS_TIER1, EMERGENCY_KEYWORDS_TIER2


class InputPreprocessor:

    MAX_INPUT_LENGTH = 2000

    def process(self, raw_text: str) -> PreprocessedInput:
        logger.debug(
            f"Preprocessing: '{raw_text[:80]}...'" if len(raw_text) > 80
            else f"Preprocessing: '{raw_text}'"
        )

        if not raw_text or not raw_text.strip():
            raw_text = "(empty message)"

        if len(raw_text) > self.MAX_INPUT_LENGTH:
            logger.warning(f"Input truncated from {len(raw_text)} chars")
            raw_text = raw_text[:self.MAX_INPUT_LENGTH] + "..."

        normalized = unicodedata.normalize("NFKC", raw_text)

        cleaned = normalized.lower()
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        cleaned = re.sub(r'[\x00-\x1f\x7f]', '', cleaned)

        tokens = re.findall(r'\b[a-zA-Z0-9]+\b', cleaned)

        tier1_matches = [kw for kw in EMERGENCY_KEYWORDS_TIER1 if kw.lower() in cleaned]
        tier2_matches = [kw for kw in EMERGENCY_KEYWORDS_TIER2 if kw.lower() in cleaned]

        has_emergency = len(tier1_matches) > 0

        if tier1_matches:
            logger.warning(f"TIER 1 emergency keywords: {tier1_matches}")
        if tier2_matches:
            logger.info(f"TIER 2 (context-dependent) keywords: {tier2_matches}")

        return PreprocessedInput(
            original=raw_text,
            cleaned=cleaned,
            tokens=tokens,
            has_emergency_keyword=has_emergency,
            detected_emergency_words=tier1_matches,
            possible_emergency_words=tier2_matches,
            char_count=len(cleaned),
            word_count=len(tokens),
        )

    def as_runnable(self) -> RunnableLambda:
        return RunnableLambda(self.process)


preprocessor = InputPreprocessor()

preprocessor_runnable = preprocessor.as_runnable()