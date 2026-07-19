"""ORM models.

Import every model here so Alembic autogenerate can discover it.
"""

from app.database.base import Base
from app.models.conversation import Conversation, ConversationChannel, Message, MessageSender
from app.models.department import Department
from app.models.doctor import Doctor
from app.models.document import Document, DocumentStatus, DocumentType
from app.models.hospital import Hospital
from app.models.user import User, UserRole

__all__ = [
    "Base",
    "Conversation",
    "ConversationChannel",
    "Department",
    "Doctor",
    "Document",
    "DocumentStatus",
    "DocumentType",
    "Hospital",
    "Message",
    "MessageSender",
    "User",
    "UserRole",
]
