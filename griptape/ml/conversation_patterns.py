# analyzemeateam-griptape-core/griptape/ml/conversation_patterns.py
"""
AMT Conversation Pattern Analysis Engine
Foundation ML system for adaptive bot learning across 25-bot ecosystem
Enables organic expertise development without hardcoded Triangle Defense DNA
"""

import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import re
from collections import defaultdict, Counter
import hashlib
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class InteractionOutcome(Enum):
    """Standardized interaction outcome ratings"""
    EXCELLENT = 5    # User highly satisfied, task completed successfully
    GOOD = 4         # User satisfied, minor issues
    NEUTRAL = 3      # User neutral, task partially completed
    POOR = 2         # User unsatisfied, significant issues
    FAILED = 1       # User very unsatisfied, task failed

class DomainCategory(Enum):
    """AMT organizational domains for expertise development"""
    STRATEGIC_LEADERSHIP = "strategic_leadership"
    TRIANGLE_DEFENSE = "triangle_defense"
    LEGAL_COMPLIANCE = "legal_compliance"
    OPERATIONS_MANAGEMENT = "operations_management"
    FOOTBALL_ANALYTICS = "football_analytics"
    MEDICAL_SAFETY = "medical_safety"
    TECHNOLOGY_AI = "technology_ai"
    COMMUNICATIONS = "communications"
    INNOVATION_R_D = "innovation_r_d"
    SECURITY_RISK = "security_risk"
    HUMAN_CAPITAL = "human_capital"
    GENERAL_COORDINATION = "general_coordination"

@dataclass
class ConversationMetrics:
    """Metrics captured from each conversation"""
    conversation_id: str
    bot_id: str
    timestamp: datetime
    duration_seconds: int
    message_count: int
    user_satisfaction: InteractionOutcome
    domain_tags: Set[DomainCategory] = field(default_factory=set)
    complexity_score: float = 0.0
    success_indicators: List[str] = field(default_factory=list)
    failure_indicators: List[str] = field(default_factory=list)
    topic_keywords: Set[str] = field(default_factory=set)
    
class LearningPattern:
    """Represents a learned pattern from successful interactions"""
    
    def __init__(self, pattern_id: str, domain: DomainCategory, 
                 trigger_keywords: Set[str], response_strategy: str,
                 success_rate: float = 0.0, confidence: float = 0.0):
        self.pattern_id = pattern_id
        self.domain = domain
        self.trigger_keywords = trigger_keywords
        self.response_strategy = response_strategy
        self.success_rate = success_rate
        self.confidence = confidence
        self.usage_count = 0
        self.created_at = datetime.now()
        self.last_used = None
    
    def update_success(self, outcome: InteractionOutcome):
        """Update pattern success metrics"""
        self.usage_count += 1
        self.last_used = datetime.now()
        
        # Weighted success rate calculation
        outcome_weight = outcome.value / 5.0
        if self.usage_count == 1:
            self.success_rate = outcome_weight
        else:
            # Exponential moving average
            alpha = 0.1
            self.success_rate = alpha * outcome_weight + (1 - alpha) * self.success_rate
        
        # Update confidence based on usage frequency
        self.confidence = min(1.0, self.usage_count / 10.0)

class ConversationPatternAnalyzer:
    """Core ML engine for analyzing conversation patterns and extracting learning insights"""
    
    def __init__(self, bot_id: str, organizational_tier: str):
        self.bot_id = bot_id
        self.organizational_tier = organizational_tier
        self.conversation_history: List[ConversationMetrics] = []
        self.learned_patterns: Dict[str, LearningPattern] = {}
        self.domain_expertise: Dict[DomainCategory, float] = {
            domain: 0.0 for domain in DomainCategory
        }
        
        # AMT-specific pattern templates based on organizational roles
        self._initialize_role_patterns()
    
    def _initialize_role_patterns(self):
        """Initialize domain-specific pattern templates based on organizational tier"""
        tier_domain_mapping = {
            "founder": {DomainCategory.STRATEGIC_LEADERSHIP, DomainCategory.TRIANGLE_DEFENSE},
            "executive": {DomainCategory.LEGAL_COMPLIANCE, DomainCategory.OPERATIONS_MANAGEMENT},
            "strategic": {DomainCategory.FOOTBALL_ANALYTICS, DomainCategory.TECHNOLOGY_AI, DomainCategory.MEDICAL_SAFETY},
            "advisory": {DomainCategory.COMMUNICATIONS, DomainCategory.HUMAN_CAPITAL},
            "innovation": {DomainCategory.INNOVATION_R_D, DomainCategory.TECHNOLOGY_AI},
            "football": {DomainCategory.FOOTBALL_ANALYTICS, DomainCategory.TRIANGLE_DEFENSE}
        }
        
        # Initialize base expertise for bot's tier
        if self.organizational_tier.lower() in tier_domain_mapping:
            for domain in tier_domain_mapping[self.organizational_tier.lower()]:
                self.domain_expertise[domain] = 0.1  # Base competency
    
    def analyze_conversation(self, messages: List[Dict], user_feedback: Optional[InteractionOutcome] = None) -> ConversationMetrics:
        """Analyze a conversation and extract learning patterns"""
        
        conversation_id = self._generate_conversation_id(messages)
        
        # Extract conversation features
        topic_keywords = self._extract_keywords(messages)
        domain_tags = self._classify_domains(messages, topic_keywords)
        complexity_score = self._calculate_complexity(messages)
        
        # Determine outcome if not provided
        if user_feedback is None:
            user_feedback = self._infer_outcome(messages)
        
        metrics = ConversationMetrics(
            conversation_id=conversation_id,
            bot_id=self.bot_id,
            timestamp=datetime.now(),
            duration_seconds=self._estimate_duration(messages),
            message_count=len(messages),
            user_satisfaction=user_feedback,
            domain_tags=domain_tags,
            complexity_score=complexity_score,
            topic_keywords=topic_keywords
        )
        
        # Extract success/failure indicators
        if user_feedback.value >= 4:
            metrics.success_indicators = self._extract_success_patterns(messages, domain_tags)
        else:
            metrics.failure_indicators = self._extract_failure_patterns(messages, domain_tags)
        
        self.conversation_history.append(metrics)
        
        # Update learning patterns
        self._update_learning_patterns(metrics)
        
        # Update domain expertise
        self._update_domain_expertise(metrics)
        
        return metrics
    
    def _extract_keywords(self, messages: List[Dict]) -> Set[str]:
        """Extract relevant keywords from conversation"""
        text = " ".join([msg.get('content', '') for msg in messages])
        
        # AMT-specific keyword patterns
        amt_keywords = {
            'triangle defense', 'formation', 'defensive', 'larry', 'linda', 'leon', 'rita',
            'strategic', 'leadership', 'legal', 'compliance', 'operations', 'coordination',
            'analytics', 'medical', 'safety', 'security', 'innovation', 'technology',
            'coaching', 'player development', 'scouting', 'recruiting'
        }
        
        # Extract keywords using simple pattern matching
        found_keywords = set()
        text_lower = text.lower()
        
        for keyword in amt_keywords:
            if keyword in text_lower:
                found_keywords.add(keyword)
        
        # Add dynamic keyword extraction
        words = re.findall(r'\b\w{4,}\b', text_lower)
        word_freq = Counter(words)
        
        # Add frequently mentioned words
        for word, freq in word_freq.most_common(10):
            if freq > 1 and len(word) > 4:
                found_keywords.add(word)
        
        return found_keywords
    
    def _classify_domains(self, messages: List[Dict], keywords: Set[str]) -> Set[DomainCategory]:
        """Classify conversation into domain categories"""
        domain_keywords = {
            DomainCategory.STRATEGIC_LEADERSHIP: {'strategic', 'leadership', 'vision', 'planning', 'decision'},
            DomainCategory.TRIANGLE_DEFENSE: {'triangle', 'defense', 'formation', 'larry', 'linda', 'leon', 'rita'},
            DomainCategory.LEGAL_COMPLIANCE: {'legal', 'compliance', 'contract', 'ip', 'regulation'},
            DomainCategory.OPERATIONS_MANAGEMENT: {'operations', 'coordination', 'management', 'process'},
            DomainCategory.FOOTBALL_ANALYTICS: {'analytics', 'football', 'player', 'stats', 'performance'},
            DomainCategory.MEDICAL_SAFETY: {'medical', 'health', 'safety', 'injury', 'wellness'},
            DomainCategory.TECHNOLOGY_AI: {'technology', 'ai', 'data', 'system', 'algorithm'},
            DomainCategory.COMMUNICATIONS: {'communications', 'media', 'brand', 'message'},
            DomainCategory.INNOVATION_R_D: {'innovation', 'research', 'development', 'future'},
            DomainCategory.SECURITY_RISK: {'security', 'risk', 'threat', 'protection'},
            DomainCategory.HUMAN_CAPITAL: {'career', 'development', 'training', 'talent'},
            DomainCategory.GENERAL_COORDINATION: {'coordinate', 'organize', 'manage', 'plan'}
        }
        
        classified_domains = set()
        
        for domain, domain_keys in domain_keywords.items():
            if any(keyword in keywords for keyword in domain_keys):
                classified_domains.add(domain)
        
        # Default to general coordination if no specific domain identified
        if not classified_domains:
            classified_domains.add(DomainCategory.GENERAL_COORDINATION)
        
        return classified_domains
    
    def _calculate_complexity(self, messages: List[Dict]) -> float:
        """Calculate conversation complexity score"""
        if not messages:
            return 0.0
        
        total_length = sum(len(msg.get('content', '')) for msg in messages)
        avg_message_length = total_length / len(messages)
        
        # Complexity factors
        length_factor = min(1.0, avg_message_length / 200)  # Normalize to max 200 chars
        message_count_factor = min(1.0, len(messages) / 20)  # Normalize to max 20 messages
        
        return (length_factor + message_count_factor) / 2
    
    def _infer_outcome(self, messages: List[Dict]) -> InteractionOutcome:
        """Infer conversation outcome from message content"""
        if not messages:
            return InteractionOutcome.NEUTRAL
        
        last_messages = messages[-3:]  # Look at last few messages
        text = " ".join([msg.get('content', '') for msg in last_messages]).lower()
        
        # Positive indicators
        positive_words = {'thank', 'great', 'perfect', 'excellent', 'helpful', 'solved', 'clear'}
        negative_words = {'confused', 'wrong', 'error', 'problem', 'issue', 'unclear', 'frustrated'}
        
        positive_score = sum(1 for word in positive_words if word in text)
        negative_score = sum(1 for word in negative_words if word in text)
        
        if positive_score > negative_score + 1:
            return InteractionOutcome.EXCELLENT
        elif positive_score > negative_score:
            return InteractionOutcome.GOOD
        elif negative_score > positive_score + 1:
            return InteractionOutcome.POOR
        elif negative_score > positive_score:
            return InteractionOutcome.FAILED
        else:
            return InteractionOutcome.NEUTRAL
    
    def _estimate_duration(self, messages: List[Dict]) -> int:
        """Estimate conversation duration in seconds"""
        # Simple estimation based on message count and length
        if not messages:
            return 0
        
        total_chars = sum(len(msg.get('content', '')) for msg in messages)
        # Estimate ~2 seconds per 100 characters (reading + typing time)
        estimated_seconds = max(30, (total_chars // 50) * 30)  # Minimum 30 seconds
        
        return min(3600, estimated_seconds)  # Maximum 1 hour
    
    def _extract_success_patterns(self, messages: List[Dict], domains: Set[DomainCategory]) -> List[str]:
        """Extract patterns that led to successful interactions"""
        success_patterns = []
        
        # Look for patterns in successful conversations
        for msg in messages:
            content = msg.get('content', '').lower()
            
            # Pattern: Direct answers to specific questions
            if any(word in content for word in ['specifically', 'exactly', 'precisely']):
                success_patterns.append("direct_specific_response")
            
            # Pattern: Step-by-step explanations
            if any(word in content for word in ['first', 'then', 'next', 'finally']):
                success_patterns.append("step_by_step_explanation")
            
            # Pattern: Domain-specific expertise demonstration
            for domain in domains:
                if domain == DomainCategory.TRIANGLE_DEFENSE and 'formation' in content:
                    success_patterns.append("triangle_defense_expertise")
                elif domain == DomainCategory.STRATEGIC_LEADERSHIP and 'strategic' in content:
                    success_patterns.append("strategic_thinking_display")
        
        return success_patterns
    
    def _extract_failure_patterns(self, messages: List[Dict], domains: Set[DomainCategory]) -> List[str]:
        """Extract patterns that led to failed interactions"""
        failure_patterns = []
        
        for msg in messages:
            content = msg.get('content', '').lower()
            
            # Pattern: Vague or generic responses
            if any(word in content for word in ['maybe', 'possibly', 'might', 'could be']):
                failure_patterns.append("vague_response")
            
            # Pattern: Off-topic responses
            if 'not sure' in content or 'don\'t know' in content:
                failure_patterns.append("knowledge_gap")
        
        return failure_patterns
    
    def _update_learning_patterns(self, metrics: ConversationMetrics):
        """Update or create learning patterns based on conversation analysis"""
        
        if metrics.user_satisfaction.value < 3:
            return  # Don't learn from poor interactions
        
        for domain in metrics.domain_tags:
            for pattern_type in metrics.success_indicators:
                pattern_id = f"{domain.value}_{pattern_type}_{len(metrics.topic_keywords)}"
                
                if pattern_id in self.learned_patterns:
                    # Update existing pattern
                    self.learned_patterns[pattern_id].update_success(metrics.user_satisfaction)
                else:
                    # Create new pattern
                    self.learned_patterns[pattern_id] = LearningPattern(
                        pattern_id=pattern_id,
                        domain=domain,
                        trigger_keywords=metrics.topic_keywords.copy(),
                        response_strategy=pattern_type,
                        success_rate=metrics.user_satisfaction.value / 5.0,
                        confidence=0.1
                    )
    
    def _update_domain_expertise(self, metrics: ConversationMetrics):
        """Update domain expertise levels based on successful interactions"""
        
        learning_rate = 0.01  # Slow, organic learning
        
        for domain in metrics.domain_tags:
            if metrics.user_satisfaction.value >= 4:
                # Successful interaction - increase expertise
                current_expertise = self.domain_expertise[domain]
                improvement = learning_rate * (1 - current_expertise)  # Diminishing returns
                self.domain_expertise[domain] = min(1.0, current_expertise + improvement)
            elif metrics.user_satisfaction.value <= 2:
                # Failed interaction - slight decrease in confidence
                current_expertise = self.domain_expertise[domain]
                self.domain_expertise[domain] = max(0.0, current_expertise - learning_rate * 0.1)
    
    def _generate_conversation_id(self, messages: List[Dict]) -> str:
        """Generate unique conversation ID"""
        content_hash = hashlib.md5(
            json.dumps(messages, sort_keys=True).encode()
        ).hexdigest()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{self.bot_id}_{timestamp}_{content_hash[:8]}"
    
    def get_domain_expertise_summary(self) -> Dict[str, float]:
        """Get current domain expertise levels"""
        return {domain.value: expertise for domain, expertise in self.domain_expertise.items()}
    
    def get_learning_patterns_summary(self) -> Dict[str, Dict]:
        """Get summary of learned patterns"""
        return {
            pattern_id: {
                "domain": pattern.domain.value,
                "success_rate": pattern.success_rate,
                "confidence": pattern.confidence,
                "usage_count": pattern.usage_count,
                "trigger_keywords": list(pattern.trigger_keywords)
            }
            for pattern_id, pattern in self.learned_patterns.items()
        }
    
    def suggest_response_strategy(self, current_context: Dict[str, Any]) -> Optional[str]:
        """Suggest response strategy based on learned patterns"""
        keywords = set(current_context.get('keywords', []))
        domains = set(current_context.get('domains', []))
        
        best_pattern = None
        best_score = 0.0
        
        for pattern in self.learned_patterns.values():
            if pattern.domain in domains:
                # Calculate relevance score
                keyword_overlap = len(keywords.intersection(pattern.trigger_keywords))
                relevance_score = (
                    pattern.success_rate * 0.4 +
                    pattern.confidence * 0.3 +
                    (keyword_overlap / max(len(pattern.trigger_keywords), 1)) * 0.3
                )
                
                if relevance_score > best_score and relevance_score > 0.5:
                    best_score = relevance_score
                    best_pattern = pattern
        
        return best_pattern.response_strategy if best_pattern else None
    
    def save_learning_data(self, filepath: Path):
        """Save learning data to file"""
        data = {
            "bot_id": self.bot_id,
            "organizational_tier": self.organizational_tier,
            "domain_expertise": self.get_domain_expertise_summary(),
            "learned_patterns": self.get_learning_patterns_summary(),
            "conversation_count": len(self.conversation_history),
            "last_updated": datetime.now().isoformat()
        }
        
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Saved learning data for {self.bot_id} to {filepath}")
    
    def load_learning_data(self, filepath: Path):
        """Load learning data from file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Restore domain expertise
            for domain_name, expertise in data.get("domain_expertise", {}).items():
                try:
                    domain = DomainCategory(domain_name)
                    self.domain_expertise[domain] = expertise
                except ValueError:
                    logger.warning(f"Unknown domain category: {domain_name}")
            
            logger.info(f"Loaded learning data for {self.bot_id} from {filepath}")
            
        except FileNotFoundError:
            logger.info(f"No existing learning data found for {self.bot_id}")
        except Exception as e:
            logger.error(f"Error loading learning data: {e}")


class AMTLearningCoordinator:
    """Coordinates learning across multiple AMT bots to prevent homogenization"""
    
    def __init__(self):
        self.bot_analyzers: Dict[str, ConversationPatternAnalyzer] = {}
        self.cross_bot_patterns: Dict[str, Dict] = {}
    
    def register_bot(self, bot_id: str, analyzer: ConversationPatternAnalyzer):
        """Register a bot analyzer for coordination"""
        self.bot_analyzers[bot_id] = analyzer
    
    def share_successful_patterns(self, source_bot_id: str, target_bot_ids: List[str], 
                                 domain: DomainCategory, min_confidence: float = 0.7):
        """Share successful patterns between bots while preserving individuality"""
        
        if source_bot_id not in self.bot_analyzers:
            return
        
        source_analyzer = self.bot_analyzers[source_bot_id]
        
        # Find high-confidence patterns in the specified domain
        patterns_to_share = [
            pattern for pattern in source_analyzer.learned_patterns.values()
            if pattern.domain == domain and pattern.confidence >= min_confidence
        ]
        
        for target_bot_id in target_bot_ids:
            if target_bot_id in self.bot_analyzers:
                target_analyzer = self.bot_analyzers[target_bot_id]
                
                for pattern in patterns_to_share:
                    # Adapt pattern for target bot (reduced confidence to encourage organic learning)
                    adapted_pattern_id = f"shared_{source_bot_id}_{pattern.pattern_id}"
                    
                    if adapted_pattern_id not in target_analyzer.learned_patterns:
                        target_analyzer.learned_patterns[adapted_pattern_id] = LearningPattern(
                            pattern_id=adapted_pattern_id,
                            domain=pattern.domain,
                            trigger_keywords=pattern.trigger_keywords.copy(),
                            response_strategy=pattern.response_strategy,
                            success_rate=pattern.success_rate * 0.8,  # Reduce for adaptation
                            confidence=min(0.3, pattern.confidence * 0.5)  # Lower confidence
                        )
    
    def analyze_ecosystem_learning(self) -> Dict[str, Any]:
        """Analyze learning patterns across the entire 25-bot ecosystem"""
        
        ecosystem_summary = {
            "total_bots": len(self.bot_analyzers),
            "domain_distribution": defaultdict(list),
            "learning_velocity": {},
            "expertise_leaders": {},
            "coordination_opportunities": []
        }
        
        for bot_id, analyzer in self.bot_analyzers.items():
            # Track domain expertise distribution
            for domain, expertise in analyzer.domain_expertise.items():
                if expertise > 0.3:  # Significant expertise threshold
                    ecosystem_summary["domain_distribution"][domain.value].append({
                        "bot_id": bot_id,
                        "expertise": expertise
                    })
            
            # Calculate learning velocity (patterns learned per conversation)
            if len(analyzer.conversation_history) > 0:
                learning_velocity = len(analyzer.learned_patterns) / len(analyzer.conversation_history)
                ecosystem_summary["learning_velocity"][bot_id] = learning_velocity
        
        # Identify expertise leaders for each domain
        for domain_name, bot_list in ecosystem_summary["domain_distribution"].items():
            if bot_list:
                leader = max(bot_list, key=lambda x: x["expertise"])
                ecosystem_summary["expertise_leaders"][domain_name] = leader
        
        return ecosystem_summary


# Integration point with Griptape core
def create_amt_conversation_analyzer(bot_id: str, organizational_tier: str) -> ConversationPatternAnalyzer:
    """Factory function to create AMT-configured conversation analyzer"""
    return ConversationPatternAnalyzer(bot_id=bot_id, organizational_tier=organizational_tier)
