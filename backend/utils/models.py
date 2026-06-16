from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class EmergencyLevel(int, Enum):
    NONE = 0
    MILD = 1
    MODERATE = 2
    URGENT = 3
    CRITICAL = 4


class IntentType(str, Enum):
    GREETING = "greeting"
    SYMPTOM_CHECK = "symptom_check"
    MEDICATION_INFO = "medication_info"
    APPOINTMENT = "appointment"
    WELLNESS_ADVICE = "wellness_advice"
    MENTAL_HEALTH = "mental_health"
    EMERGENCY = "emergency"
    GENERAL_MEDICAL = "general_medical"
    FAREWELL = "farewell"
    OUT_OF_SCOPE = "out_of_scope"


class Message(BaseModel):
    role: str                 
    content: str              
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class ChatRequest(BaseModel):
    session_id: Optional[str] = None  
    user_message: str                  
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "abc123",
                "user_message": "I have a headache and fever"
            }
        }



class PreprocessedInput(BaseModel):
    original: str              
    cleaned: str              
    tokens: List[str]          
    has_emergency_keyword: bool 
    detected_emergency_words: List[str] 
    possible_emergency_words: List[str] = [] 
    char_count: int
    word_count: int


class ClassificationResult(BaseModel):
    intent: IntentType                 
    emergency_level: EmergencyLevel    
    needs_web_search: bool             
    needs_memory: bool                 
    confidence: float                 
    keywords_detected: List[str]       
    raw_llm_output: str             


class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str
    is_trusted: bool          


class BuiltContext(BaseModel):
    system_prompt: str                    
    conversation_history: List[Message]    
    search_results: List[SearchResult]      
    memory_summary: str                    
    intent: IntentType
    emergency_level: EmergencyLevel

class ChatResponse(BaseModel):
    session_id: str
    response: str                         
    intent: str                           
    emergency_level: int                   
    emergency_message: Optional[str]      
    sources: List[SearchResult] = []       
    confidence: float                     
    is_safe: bool                         
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat()
    )


class SessionData(BaseModel):
    session_id: str
    created_at: str
    last_active: str
    messages: List[Message] = []
    metadata: Dict[str, Any] = {}         