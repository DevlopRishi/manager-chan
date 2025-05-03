# Defines the data structure for a single note/task item.
import datetime
import uuid
from typing import List, Dict, Optional, Any
from .constants import STATUS_OPTIONS, PRIORITY_OPTIONS # Use constants

class NoteItem:
    def __init__(self, id: str = None, text: str = "", notes: str = "",
                 status: str = "Todo", priority: Optional[str] = None,
                 tags: Optional[List[str]] = None,
                 created_at: Optional[datetime.datetime] = None,
                 modified_at: Optional[datetime.datetime] = None,
                 due_date: Optional[datetime.date] = None):
        self.id = id or str(uuid.uuid4())
        self.text = text
        self.notes = notes # Markdown format
        self.status = status if status in STATUS_OPTIONS else STATUS_OPTIONS[0] # Default to first status
        self.priority = priority if priority in PRIORITY_OPTIONS else None
        self.tags = sorted(list(set(tag.strip().lower() for tag in tags if tag.strip()))) if tags else [] # Clean tags
        now = datetime.datetime.now().replace(microsecond=0) # Avoid microseconds for cleaner ISO strings
        self.created_at = created_at or now
        self.modified_at = modified_at or now
        self.due_date = due_date

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text,
            "notes": self.notes,
            "status": self.status,
            "priority": self.priority,
            "tags": self.tags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "modified_at": self.modified_at.isoformat() if self.modified_at else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NoteItem':
        try:
            created_at = datetime.datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None
            modified_at = datetime.datetime.fromisoformat(data["modified_at"]) if data.get("modified_at") else None
            due_date = datetime.date.fromisoformat(data["due_date"]) if data.get("due_date") else None
        except (ValueError, TypeError) as e:
            # Handle potential malformed dates gracefully during load
            print(f"Warning: Error parsing date for item '{data.get('id', 'Unknown')}': {e}. Setting to None.")
            if 'created_at' in data and data['created_at'] is not None: created_at = None # Ensure reset if parsing fails
            if 'modified_at' in data and data['modified_at'] is not None: modified_at = None
            if 'due_date' in data and data['due_date'] is not None: due_date = None


        return cls(
            id=data.get("id", str(uuid.uuid4())), # Ensure ID exists
            text=data.get("text", ""),
            notes=data.get("notes", ""),
            status=data.get("status", STATUS_OPTIONS[0]),
            priority=data.get("priority"),
            tags=data.get("tags", []),
            created_at=created_at,
            modified_at=modified_at,
            due_date=due_date
        )

    def __repr__(self):
        return f"<NoteItem(id={self.id[:8]}, text='{self.text[:20]}...')>"