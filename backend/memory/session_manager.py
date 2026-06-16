import os
import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional
from utils.models import SessionData, Message
from utils.logger import logger
from config.settings import (
    SESSIONS_DIR,
    MAX_HISTORY_TURNS,
    SESSION_TIMEOUT_SECONDS,
)


class SessionManager:

    def __init__(self):
        self.sessions_dir = Path(SESSIONS_DIR)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 SessionManager initialized. Storage: {self.sessions_dir.resolve()}")

    def _session_path(self, session_id: str) -> Path:
        return self.sessions_dir / f"{session_id}.json"

    def _load_session(self, session_id: str) -> Optional[SessionData]:
        path = self._session_path(session_id)
        if not path.exists():
            logger.debug(f"Session not found on disk: {session_id}")
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return SessionData(**data)
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Corrupt session file {path}: {e}")
            return None

    def _save_session(self, session: SessionData) -> None:
        path = self._session_path(session.session_id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(session.model_dump(), f, indent=2, ensure_ascii=False)
        logger.debug(f"💾 Saved session {session.session_id} ({len(session.messages)} messages)")

    def _is_expired(self, session: SessionData) -> bool:
        last_active = datetime.fromisoformat(session.last_active)
        timeout = timedelta(seconds=SESSION_TIMEOUT_SECONDS)
        expired = datetime.now() - last_active > timeout
        if expired:
            logger.info(f"⏰ Session {session.session_id} expired (idle > {SESSION_TIMEOUT_SECONDS}s)")
        return expired


    def create_session(self) -> str:
        session_id = str(uuid.uuid4())[:8] 
        now = datetime.now().isoformat()

        session = SessionData(
            session_id=session_id,
            created_at=now,
            last_active=now,
            messages=[],
            metadata={}
        )
        self._save_session(session)
        logger.info(f"🆕 Created new session: {session_id}")
        return session_id

    def session_exists(self, session_id: str) -> bool:
        session = self._load_session(session_id)
        if session is None:
            return False
        if self._is_expired(session):
            return False
        return True

    def add_message(self, session_id: str, role: str, content: str) -> None:
        session = self._load_session(session_id)
        if session is None:
            logger.warning(f"Session {session_id} not found, creating new one")
            self.create_session()
            session = self._load_session(session_id)

        msg = Message(
            role=role,
            content=content,
            timestamp=datetime.now().isoformat()
        )
        session.messages.append(msg)

        max_messages = MAX_HISTORY_TURNS * 2
        if len(session.messages) > max_messages:
            session.messages = session.messages[-max_messages:]
            logger.debug(f"Trimmed session history to {max_messages} messages")

        session.last_active = datetime.now().isoformat()

        self._save_session(session)

    def get_history(self, session_id: str, last_n: Optional[int] = None) -> List[Message]:
        session = self._load_session(session_id)
        if session is None:
            logger.warning(f"get_history: session {session_id} not found")
            return []

        messages = session.messages
        if last_n is not None:
            messages = messages[-last_n:]

        logger.debug(f"📜 get_history({session_id}): returning {len(messages)} messages")
        return messages

    def get_history_as_dicts(self, session_id: str) -> List[dict]:
        messages = self.get_history(session_id, last_n=MAX_HISTORY_TURNS * 2)
        return [{"role": m.role, "content": m.content} for m in messages]

    def get_session_summary(self, session_id: str) -> str:
        session = self._load_session(session_id)
        if session is None or len(session.messages) == 0:
            return "No previous conversation history."

        user_messages = [
            m.content for m in session.messages if m.role == "user"
        ][-6:]

        if not user_messages:
            return "No previous conversation history."

        summary = f"Previous topics discussed ({len(user_messages)} user messages): "
        summary += " | ".join(
            msg[:60] + "..." if len(msg) > 60 else msg
            for msg in user_messages
        )
        return summary

    def clear_session(self, session_id: str) -> bool:
        path = self._session_path(session_id)
        if path.exists():
            path.unlink()
            logger.info(f"🗑️  Deleted session: {session_id}")
            return True
        return False

    def get_session_metadata(self, session_id: str) -> dict:
        session = self._load_session(session_id)
        if session is None:
            return {}
        return session.metadata

    def update_session_metadata(self, session_id: str, key: str, value) -> None:
        session = self._load_session(session_id)
        if session is None:
            return
        session.metadata[key] = value
        session.last_active = datetime.now().isoformat()
        self._save_session(session)

session_manager = SessionManager()