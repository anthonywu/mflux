"""Database management for mflux LoRA profiles."""

import logging
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

from sqlmodel import Session, SQLModel, create_engine, select

from mflux.database.exceptions import (
    EntryValidationError,
    ProfileExistsError,
    ProfileNotFoundError,
)
from mflux.database.lora_profiles import LoRAEntry, LoRAProfile

# Configure SQLAlchemy logging
sql_logger = logging.getLogger('sqlalchemy.engine')
sql_logger.setLevel(logging.INFO)

# Check if logging to file is enabled
ENABLE_SQL_LOGGING = os.environ.get("MFLUX_SQL_LOGGING", "0").lower() in ("1", "true", "yes")

if ENABLE_SQL_LOGGING:
    # Create logs directory if it doesn't exist
    logs_dir = Path.home() / ".mflux" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Set up file handler
    log_file = logs_dir / "sql.log"
    file_handler = logging.FileHandler(log_file, mode='a')
    file_handler.setLevel(logging.INFO)
    
    # Add formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    # Add handler to logger
    sql_logger.addHandler(file_handler)

# Get database path (user's home directory or configurable path)
DEFAULT_DB_PATH = Path.home() / ".mflux" / "lora_profiles.db"
DB_PATH = os.environ.get("MFLUX_LORA_DB_PATH", str(DEFAULT_DB_PATH))

# Ensure directory exists
Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)

# Create SQLite engine - echo setting is independent of file logging
engine = create_engine(
    f"sqlite:///{DB_PATH}", 
    echo=False,  # Set to True to output SQL to stdout as well
)


def init_db() -> None:
    """Initialize the database by creating all tables."""
    SQLModel.metadata.create_all(engine)


@contextmanager
def get_session() -> Iterator[Session]:
    """Get a database session as a context manager."""
    with Session(engine) as session:
        yield session


def register_lora_profile(
    name: str,
    lora_entries: List[Dict[str, Any]],
    description: Optional[str] = None,
) -> LoRAProfile:
    """Register a new LoRA profile with entries.

    Args:
        name: Name of the profile (must be unique)
        lora_entries: List of dictionaries with keys for location ('path' or 'hf_repo_id'), 
                     'scale', and 'trigger_phrase'
        description: Optional description of the profile

    Returns:
        The created LoRAProfile object

    Raises:
        ProfileExistsError: If a profile with the given name already exists
        EntryValidationError: If any entry doesn't have either path or hf_repo_id
    """
    with get_session() as session:
        # Check if profile already exists
        existing = session.exec(select(LoRAProfile).where(LoRAProfile.name == name)).first()
        if existing:
            raise ProfileExistsError(f"LoRA profile '{name}' already exists")

        # Create new profile
        profile = LoRAProfile(name=name, description=description)
        session.add(profile)
        session.commit()
        session.refresh(profile)

        # Add entries
        for i, entry in enumerate(lora_entries):
            # Get path or hf_repo_id (at least one must be provided)
            path = entry.get("path")
            hf_repo_id = entry.get("hf_repo_id")
            
            if not path and not hf_repo_id:
                raise EntryValidationError(f"Entry {i+1} must have either 'path' or 'hf_repo_id'")
            
            lora_entry = LoRAEntry(
                profile_id=profile.id,
                path=path,
                hf_repo_id=hf_repo_id,
                scale=entry.get("scale", 1.0),
                trigger_phrase=entry.get("trigger_phrase", entry.get("trigger_word", "")),  # Support both keys for backward compatibility
                order=i,
            )
            
            # Validate the entry
            if not lora_entry.validate():
                raise EntryValidationError(f"Entry {i+1} is invalid: must have either path or hf_repo_id")
                
            session.add(lora_entry)

        session.commit()
        return profile


def get_lora_profile(name: str) -> LoRAProfile:
    """Get a LoRA profile by name.

    Args:
        name: Name of the profile to retrieve

    Returns:
        The LoRAProfile object
        
    Raises:
        ProfileNotFoundError: If the profile is not found
    """
    with get_session() as session:
        statement = select(LoRAProfile).where(LoRAProfile.name == name)
        profile = session.exec(statement).first()
        if not profile:
            raise ProfileNotFoundError(f"LoRA profile '{name}' not found")
        return profile


def get_lora_entries(profile_id: int) -> List[LoRAEntry]:
    """Get all entries for a LoRA profile.

    Args:
        profile_id: ID of the profile to get entries for

    Returns:
        List of LoRAEntry objects sorted by order
        
    Raises:
        ProfileNotFoundError: If no profile with the given ID exists
    """
    with get_session() as session:
        # First check if the profile exists
        profile = session.exec(select(LoRAProfile).where(LoRAProfile.id == profile_id)).first()
        if not profile:
            raise ProfileNotFoundError(f"LoRA profile with ID {profile_id} not found")
            
        # Get entries
        statement = select(LoRAEntry).where(
            LoRAEntry.profile_id == profile_id
        ).order_by(LoRAEntry.order)
        return session.exec(statement).all()


def list_lora_profiles() -> List[LoRAProfile]:
    """List all LoRA profiles.

    Returns:
        List of all LoRAProfile objects sorted by name.
        Returns an empty list if no profiles exist.
    """
    with get_session() as session:
        return session.exec(select(LoRAProfile).order_by(LoRAProfile.name)).all()


def delete_lora_profile(name: str) -> None:
    """Delete a LoRA profile by name.

    Args:
        name: Name of the profile to delete

    Raises:
        ProfileNotFoundError: If the profile is not found
    """
    with get_session() as session:
        profile = session.exec(select(LoRAProfile).where(LoRAProfile.name == name)).first()
        if not profile:
            raise ProfileNotFoundError(f"LoRA profile '{name}' not found")

        # Delete all entries
        entries = session.exec(select(LoRAEntry).where(LoRAEntry.profile_id == profile.id)).all()
        for entry in entries:
            session.delete(entry)

        # Delete profile
        session.delete(profile)
        session.commit()
