"""Tests for the LoRA profile database functionality."""

import os
import tempfile
from pathlib import Path

import pytest
from sqlmodel import Session, SQLModel, create_engine, select

from mflux.database.database import (
    delete_lora_profile,
    engine,
    get_lora_entries,
    get_lora_profile,
    init_db,
    list_lora_profiles,
    register_lora_profile,
)
from mflux.database.lora_profiles import LoRAEntry, LoRAProfile


@pytest.fixture
def temp_db(monkeypatch):
    """Create a temporary database for testing."""
    # Create a temporary file for the database
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        db_path = Path(tmp.name)
    
    # Create a test engine with the temporary path
    test_engine = create_engine(f"sqlite:///{db_path}", echo=False)
    
    # Create the tables
    SQLModel.metadata.create_all(test_engine)
    
    # Monkey patch the database module
    from mflux.database import database
    monkeypatch.setattr(database, "DB_PATH", str(db_path))
    monkeypatch.setattr(database, "engine", test_engine)
    
    # We need to call init_db since the database functions use it
    init_db()
    
    yield str(db_path)
    
    # Clean up
    if db_path.exists():
        db_path.unlink()


@pytest.fixture
def sample_entries():
    """Create a list of sample LoRA entries for testing."""
    return [
        {"path": "test_lora1.safetensors", "scale": 0.8, "trigger_word": "test style"},
        {"path": "test_lora2.safetensors", "scale": 1.0, "trigger_word": "another style"},
    ]


def test_register_and_get_profile(temp_db, sample_entries):
    """Test registering and retrieving a LoRA profile."""
    # Register a profile
    profile = register_lora_profile(
        name="test_profile",
        lora_entries=sample_entries,
        description="Test profile description",
    )
    
    # Get a fresh instance from the database to avoid detached instance issues
    with Session(engine) as session:
        # Verify the profile was created in database
        db_profile = session.exec(select(LoRAProfile).where(LoRAProfile.name == "test_profile")).first()
        assert db_profile is not None
        assert db_profile.name == "test_profile"
        assert db_profile.description == "Test profile description"
    
    # Retrieve the profile using the function
    retrieved = get_lora_profile("test_profile")
    assert retrieved is not None
    assert retrieved.name == "test_profile"
    assert retrieved.description == "Test profile description"
    
    # Check entries
    retrieved_entries = get_lora_entries(retrieved.id)
    assert len(retrieved_entries) == 2
    
    # Check first entry
    assert retrieved_entries[0].path == "test_lora1.safetensors"
    assert retrieved_entries[0].scale == pytest.approx(0.8)
    assert retrieved_entries[0].trigger_word == "test style"
    
    # Check second entry
    assert retrieved_entries[1].path == "test_lora2.safetensors"
    assert retrieved_entries[1].scale == pytest.approx(1.0)
    assert retrieved_entries[1].trigger_word == "another style"


def test_list_profiles(temp_db):
    """Test listing LoRA profiles."""
    # Register multiple profiles
    register_lora_profile(
        name="profile1",
        lora_entries=[{"path": "lora1.safetensors", "scale": 1.0, "trigger_word": "style1"}],
        description="First profile",
    )
    
    register_lora_profile(
        name="profile2",
        lora_entries=[{"path": "lora2.safetensors", "scale": 0.5, "trigger_word": "style2"}],
        description="Second profile",
    )
    
    # List profiles
    profiles = list_lora_profiles()
    
    # Verify we have two profiles
    assert len(profiles) == 2
    
    # Check they're sorted by name
    assert profiles[0].name == "profile1"
    assert profiles[1].name == "profile2"


def test_delete_profile(temp_db):
    """Test deleting a LoRA profile."""
    # Register a profile
    register_lora_profile(
        name="delete_me",
        lora_entries=[{"path": "lora.safetensors", "scale": 1.0, "trigger_word": "style"}],
        description="Profile to delete",
    )
    
    # Verify it exists
    profile = get_lora_profile("delete_me")
    assert profile is not None
    
    # Delete it
    result = delete_lora_profile("delete_me")
    assert result is True
    
    # Verify it's gone
    profile = get_lora_profile("delete_me")
    assert profile is None
    
    # Try to delete a non-existent profile
    result = delete_lora_profile("nonexistent")
    assert result is False


def test_duplicate_profile_name(temp_db):
    """Test that we can't create two profiles with the same name."""
    # Register a profile
    register_lora_profile(
        name="unique_name",
        lora_entries=[{"path": "lora.safetensors", "scale": 1.0, "trigger_word": "style"}],
    )
    
    # Try to register another with the same name
    with pytest.raises(ValueError):
        register_lora_profile(
            name="unique_name",
            lora_entries=[{"path": "other.safetensors", "scale": 0.8, "trigger_word": "other"}],
        )