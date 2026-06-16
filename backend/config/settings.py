import os
from dotenv import load_dotenv

load_dotenv() 
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

CLASSIFIER_MODEL = os.getenv("CLASSIFIER_MODEL", "llama3")

RESPONDER_MODEL = os.getenv("RESPONDER_MODEL", "llama3")

OLLAMA_GENERATE_URL = f"{OLLAMA_BASE_URL}/api/generate"

OLLAMA_CHAT_URL = f"{OLLAMA_BASE_URL}/api/chat"

SESSIONS_DIR = os.getenv("SESSIONS_DIR", "./sessions")

MAX_HISTORY_TURNS = int(os.getenv("MAX_HISTORY_TURNS", "10"))

SESSION_TIMEOUT_SECONDS = int(os.getenv("SESSION_TIMEOUT_SECONDS", "1800"))

DEFAULT_EMERGENCY_NUMBER = os.getenv("DEFAULT_EMERGENCY_NUMBER", None)

EMERGENCY_NUMBERS_BY_REGION = {
    "us": "911",
    "canada": "911",
    "uk": "999",
    "united kingdom": "999",
    "eu": "112",
    "europe": "112",
    "india": "112",
    "australia": "000",
    "new zealand": "111",
    "japan": "119",
    "china": "120",
}

MIN_CONFIDENCE_THRESHOLD = float(os.getenv("MIN_CONFIDENCE_THRESHOLD", "0.4"))

EMERGENCY_ALERT_LEVEL = int(os.getenv("EMERGENCY_ALERT_LEVEL", "3"))

MAX_SEARCH_RESULTS = int(os.getenv("MAX_SEARCH_RESULTS", "3"))

TRUSTED_MEDICAL_DOMAINS = [
    "mayoclinic.org",
    "webmd.com",
    "healthline.com",
    "nih.gov",
    "cdc.gov",
    "who.int",
    "medlineplus.gov",
    "clevelandclinic.org",
    "hopkinsmedicine.org",
    "medscape.com",
]

DANGEROUS_RESPONSE_PATTERNS = [
    "take this medication",
    "you should take",
    "prescribed dose",
    "i diagnose",
    "you have cancer",
    "you have diabetes",
    "you are pregnant",
    "stop your medication",
    "ignore your doctor",
]

VALID_INTENTS = [
    "greeting",         
    "symptom_check",      
    "medication_info",    
    "appointment",        
    "wellness_advice",    
    "mental_health",      
    "emergency",          
    "general_medical",    
    "farewell",           
    "out_of_scope",       
]

EMERGENCY_KEYWORDS_TIER1 = [
    "heart attack",
    "stroke",
    "unconscious",
    "not breathing",
    "can't breathe",
    "cannot breathe",
    "severe bleeding",
    "overdose",
    "suicide",
    "kill myself",
    "want to die",
    "poisoning",
    "seizure",
    "anaphylaxis",
    "severe allergic reaction",
]

EMERGENCY_KEYWORDS_TIER2 = [
    "chest pain",
    "chest pressure",
    "chest tightness",
    "allergic reaction",
    "difficulty breathing",
    "shortness of breath",
    "numbness",
    "confusion",
    "fainting",
    "coughing blood",
    "blood in stool",
    "blood in urine",
    "severe headache",
    "high fever",
]

EMERGENCY_KEYWORDS = EMERGENCY_KEYWORDS_TIER1 + EMERGENCY_KEYWORDS_TIER2

APP_TITLE = "Healthcare Chatbot"
APP_VERSION = "1.0.0"
DEBUG_MODE = os.getenv("DEBUG_MODE", "true").lower() == "true"

ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000"
).split(",")