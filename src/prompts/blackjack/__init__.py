"""
Blackjack Twitter Engine - Prompts & Modes
Gambling wisdom for life, engineered for virality.
"""

# Mode definitions and constants
from .modes import (
    CORE_IDENTITY,
    MODE_PROMPTS,
    MODE_TEMPERATURES,
    MODE_COLORS,
    ALL_MODES,
    CHALLENGE_MODES,
    ALIGN_MODES,
    # Individual modes for direct import
    CARD_COUNTER_MODE,
    HIGH_ROLLER_MODE,
    TABLE_READER_MODE,
    SHARK_MODE,
    ODDS_VALIDATOR_MODE,
    BANKROLL_AMPLIFIER_MODE,
    BANKROLL_MANAGER_MODE,
    THE_DEALER_MODE,
)

# Prompt templates
from .prompts import (
    ANALYZER_PROMPT,
    IMAGE_ANALYZER_PROMPT,
    REPLY_GENERATOR_PROMPT,
    IMAGE_REPLY_GENERATOR_PROMPT,
    TWEET_GENERATOR_PROMPT,
    THREAD_GENERATOR_PROMPT,
)

__all__ = [
    # Core identity
    "CORE_IDENTITY",
    # Mode infrastructure
    "MODE_PROMPTS",
    "MODE_TEMPERATURES",
    "MODE_COLORS",
    "ALL_MODES",
    "CHALLENGE_MODES",
    "ALIGN_MODES",
    # Individual modes
    "CARD_COUNTER_MODE",
    "HIGH_ROLLER_MODE",
    "TABLE_READER_MODE",
    "SHARK_MODE",
    "ODDS_VALIDATOR_MODE",
    "BANKROLL_AMPLIFIER_MODE",
    "BANKROLL_MANAGER_MODE",
    "THE_DEALER_MODE",
    # Prompts
    "ANALYZER_PROMPT",
    "IMAGE_ANALYZER_PROMPT",
    "REPLY_GENERATOR_PROMPT",
    "IMAGE_REPLY_GENERATOR_PROMPT",
    "TWEET_GENERATOR_PROMPT",
    "THREAD_GENERATOR_PROMPT",
]
