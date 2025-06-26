"""SQLModel definitions for LoRA profile management."""

from datetime import datetime
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class LoRAProfile(SQLModel, table=True):
    """LoRA profile model for storing collections of LoRA configurations."""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship with LoRAEntry
    entries: List["LoRAEntry"] = Relationship(back_populates="profile")


class LoRAEntry(SQLModel, table=True):
    """LoRA entry model for storing LoRA file path or Hugging Face repo ID, scale, and trigger phrase."""

    id: Optional[int] = Field(default=None, primary_key=True)
    profile_id: int = Field(foreign_key="loraprofile.id")
    path: Optional[str] = None  # Local file path (use either path or hf_repo_id)
    hf_repo_id: Optional[str] = None  # Hugging Face repository ID
    scale: float = 1.0
    trigger_phrase: str
    order: int = 0  # For ordering entries within a profile

    # Relationship with LoRAProfile
    profile: LoRAProfile = Relationship(back_populates="entries")
    
    @property
    def location(self) -> str:
        """Get the location of the LoRA, either from path or hf_repo_id.
        
        Returns:
            The path or hf_repo_id, whichever is available
        """
        return self.path if self.path else self.hf_repo_id or ""
    
    def validate(self) -> bool:
        """Validate that the entry has at least one location specified.
        
        Returns:
            True if the entry is valid, False otherwise
        """
        return bool(self.path or self.hf_repo_id)
