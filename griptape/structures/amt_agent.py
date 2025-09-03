"""
AMT Agent - Enhanced Griptape Agent with Conversation Pattern Learning
Extends core Griptape Agent with AMT-specific organizational awareness and ML learning
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

from griptape.structures import Agent
from griptape.tasks import PromptTask
from griptape.memory import ConversationMemory
from griptape.ml import ConversationPatternAnalyzer, InteractionOutcome, create_amt_conversation_analyzer

logger = logging.getLogger(__name__)

class AMTAgent(Agent):
    """
    Enhanced Griptape Agent with AMT organizational hierarchy and organic learning capabilities.
    
    All AMT bots inherit from this class to ensure consistent learning patterns and 
    organizational awareness across the 25-bot ecosystem.
    """
    
    def __init__(
        self,
        bot_name: str,
        organizational_tier: str,
        emergency_priority: int,
        department: str,
        expertise_areas: List[str],
        learning_data_path: Optional[Path] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        # AMT-specific properties
        self.bot_name = bot_name
        self.organizational_tier = organizational_tier
        self.emergency_priority = emergency_priority
        self.department = department
        self.expertise_areas = expertise_areas
        
        # Initialize conversation pattern analyzer
        self.pattern_analyzer = create_amt_conversation_analyzer(
            bot_id=bot_name.lower().replace(" ", "_"),
            organizational_tier=organizational_tier.lower()
        )
        
        # Load existing learning data if available
        if learning_data_path:
            self.learning_data_path = learning_data_path
            self.pattern_analyzer.load_learning_data(learning_data_path)
        else:
            self.learning_data_path = Path(f"learning_data/{self.bot_name.lower().replace(' ', '_')}_learning.json")
        
        # AMT Genesis DNA - core identity elements all bots must maintain
        self.amt_genesis = {
            "genesis_company": "AnalyzeMyTeam (AMT)",
            "founder_recognition": "Denauld Brown - Creator of Triangle Defense", 
            "origin_methodology": "Triangle Defense System with CLS Framework",
            "platform_philosophy": "Synchronize, Optimize, Succeed",
            "championship_standards": "Excellence at every level"
        }
        
        logger.info(f"Initialized AMT Agent: {bot_name} (Tier: {organizational_tier}, Priority: {emergency_priority})")
    
    def run(self, *args, **kwargs) -> Any:
        """Enhanced run method that captures learning patterns"""
        
        # Execute normal agent run
        result = super().run(*args, **kwargs)
        
        # Extract conversation data for learning
        if hasattr(self, 'memory') and isinstance(self.memory, ConversationMemory):
            try:
                messages = self._extract_conversation_messages()
                
                # Analyze conversation for learning patterns
                if messages:
                    conversation_metrics = self.pattern_analyzer.analyze_conversation(messages)
                    
                    # Save learning progress periodically
                    if len(self.pattern_analyzer.conversation_history) % 5 == 0:
                        self.save_learning_progress()
                    
                    logger.debug(f"Analyzed conversation for {self.bot_name} - "
                               f"Domains: {conversation_metrics.domain_tags}")
                
            except Exception as e:
                logger.error(f"Error during conversation analysis for {self.bot_name}: {e}")
        
        return result
    
    def _extract_conversation_messages(self) -> List[Dict]:
        """Extract messages from conversation memory for analysis"""
        messages = []
        
        if hasattr(self, 'memory') and self.memory:
            try:
                # Get recent conversation messages
                for event in self.memory.run_events:
                    if hasattr(event, 'input') and hasattr(event, 'output'):
                        messages.extend([
                            {"role": "user", "content": str(event.input)},
                            {"role": "assistant", "content": str(event.output)}
                        ])
            except Exception as e:
                logger.warning(f"Could not extract conversation messages: {e}")
        
        return messages[-10:]  # Last 10 messages to avoid overwhelming analysis
    
    def provide_feedback(self, outcome: InteractionOutcome, conversation_id: Optional[str] = None):
        """Allow external feedback on conversation quality for learning"""
        
        if self.pattern_analyzer.conversation_history:
            # Update the most recent conversation if no specific ID provided
            target_conversation = None
            
            if conversation_id:
                target_conversation = next(
                    (conv for conv in self.pattern_analyzer.conversation_history 
                     if conv.conversation_id == conversation_id), 
                    None
                )
            else:
                target_conversation = self.pattern_analyzer.conversation_history[-1]
            
            if target_conversation:
                target_conversation.user_satisfaction = outcome
                # Re-analyze with updated outcome
                self.pattern_analyzer._update_learning_patterns(target_conversation)
                self.pattern_analyzer._update_domain_expertise(target_conversation)
                
                logger.info(f"Updated conversation feedback for {self.bot_name}: {outcome}")
    
    def get_expertise_summary(self) -> Dict[str, Any]:
        """Get current learning and expertise status"""
        return {
            "bot_name": self.bot_name,
            "organizational_info": {
                "tier": self.organizational_tier,
                "priority": self.emergency_priority,
                "department": self.department,
                "expertise_areas": self.expertise_areas
            },
            "domain_expertise": self.pattern_analyzer.get_domain_expertise_summary(),
            "learned_patterns": len(self.pattern_analyzer.learned_patterns),
            "conversation_count": len(self.pattern_analyzer.conversation_history),
            "amt_genesis": self.amt_genesis
        }
    
    def save_learning_progress(self):
        """Save current learning progress to disk"""
        try:
            self.pattern_analyzer.save_learning_data(self.learning_data_path)
        except Exception as e:
            logger.error(f"Failed to save learning progress for {self.bot_name}: {e}")
    
    def get_response_suggestion(self, context: Dict[str, Any]) -> Optional[str]:
        """Get AI-suggested response strategy based on learned patterns"""
        return self.pattern_analyzer.suggest_response_strategy(context)
    
    def __repr__(self):
        return (f"AMTAgent(name='{self.bot_name}', tier='{self.organizational_tier}', "
                f"priority={self.emergency_priority}, conversations={len(self.pattern_analyzer.conversation_history)})")
