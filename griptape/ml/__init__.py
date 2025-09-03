"""
AMT Machine Learning Extensions for Griptape Core
Enhanced ML capabilities for the AnalyzeMyTeam bot ecosystem
"""

from .conversation_patterns import (
    ConversationPatternAnalyzer,
    AMTLearningCoordinator,
    InteractionOutcome,
    DomainCategory,
    LearningPattern,
    ConversationMetrics,
    create_amt_conversation_analyzer
)

__all__ = [
    "ConversationPatternAnalyzer",
    "AMTLearningCoordinator", 
    "InteractionOutcome",
    "DomainCategory",
    "LearningPattern",
    "ConversationMetrics",
    "create_amt_conversation_analyzer"
]

__version__ = "1.0.0-amt.1"
