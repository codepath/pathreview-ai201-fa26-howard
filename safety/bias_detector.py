"""Bias detection in generated feedback."""

import re

import structlog

logger = structlog.get_logger()


class BiasDetector:
    """Detect biased language in feedback."""

    # Genuinely dismissive phrases about educational background
    DISMISSIVE_PATTERNS = [
        r"(?:bootcamp|self-taught|online\s+course)\s+(?:education|training)\s+is\s+(?:insufficient|inadequate|lacks)",
        r"(?:bootcamp|self-taught)\s+(?:graduates?|developers?)\s+(?:lack|missing)\s+(?:rigor|fundamentals|proper\s+training)",
        r"(?:bootcamp|coding\s+bootcamp)\s+(?:doesn't|does\s+not)\s+prepare\s+(?:you|developers?)",
        r"(?:self-taught|bootcamp)\s+is\s+(?:not|never)\s+(?:equal|comparable)\s+to\s+(?:university|traditional|formal)",
        # Common alternative phrasings of dismissive education claims (issue #58).
        r"(?:coding\s+)?bootcamp\s+(?:graduates?|developers?|programmers?)\s+(?:can't|cannot|won't|will\s+not)\s+(?:write|handle|build|develop)\b",
        r"(?:bootcamp|self-taught|online\s+course)\s+(?:education|training)\s+(?:lacks?\s+(?:rigor|fundamentals)|means\s+(?:inadequate|insufficient|poor)\s+training)",
        r"bootcamp\s+programmers?\s+(?:lack|lacks|missing)\s+(?:rigor|fundamentals|proper\s+training)",
        r"(?:bootcamp|coding\s+bootcamp)\s+attendance\s+means\s+(?:inadequate|insufficient|poor)\s+training",
        r"\bbootcamp\b.{0,120}\blacks?\s+(?:the\s+)?rigor\b",
        r"self-taught\s+developers?\s+are\s+(?:not|never)\s+(?:equal|comparable)\s+to\s+(?:university|college|formal)\s+graduates?",
    ]

    # Demographic assumptions (about age, background, identity)
    DEMOGRAPHIC_PATTERNS = [
        r"(?:young|old|aged)\s+(?:person|developer|programmer)\s+(?:can't|cannot|won't|will\s+not)",
        r"(?:person\s+from|coming\s+from)\s+(?:poor|rich|working[\s-]?class)",
        r"(?:immigrant|international|foreign)\s+developers?.*(?:can't|cannot|won't|struggle)",
        # Common age and socioeconomic assumptions (issue #58).
        r"(?:young|old|aged)\s+(?:developers?|programmers?)\s+(?:can't|cannot|won't|will\s+not)\b",
        r"developers?\s+from\s+(?:poor|rich|working[\s-]?class)\s+backgrounds?\s+(?:can't|cannot|won't|will\s+not)\b",
        r"given\s+their\s+age.{0,60}(?:can't|cannot|won't|will\s+not|unable\s+to)\s+(?:keep\s+up|handle|learn)\b",
    ]

    @staticmethod
    def detect_bias(text: str) -> tuple[bool, str]:
        """Detect biased language in feedback.

        Args:
            text: Feedback text

        Returns:
            Tuple of (is_biased, reason)
        """
        # Check for dismissive language about education
        for pattern in BiasDetector.DISMISSIVE_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                reason = "Dismissive language about educational background"
                logger.warning("bias_detected", reason=reason)
                return True, reason

        # Check for demographic assumptions
        for pattern in BiasDetector.DEMOGRAPHIC_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                reason = "Demographic assumptions detected"
                logger.warning("bias_detected", reason=reason)
                return True, reason

        return False, ""
