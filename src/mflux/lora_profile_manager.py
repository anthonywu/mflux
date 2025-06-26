#!/usr/bin/env python3
"""Command-line tool for managing LoRA profiles in the database."""

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlmodel import Session, select

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


def parse_lora_entries(
    scales: List[float],
    trigger_phrases: List[str],
    paths: Optional[List[str]] = None,
    hf_repo_ids: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """Parse LoRA entries from command-line arguments.

    Args:
        scales: List of scaling factors for each LoRA
        trigger_phrases: List of trigger phrases for each LoRA
        paths: Optional list of LoRA file paths (local files)
        hf_repo_ids: Optional list of Hugging Face repository IDs

    Returns:
        List of dictionaries with keys for location ('path' or 'hf_repo_id'), 
        'scale', and 'trigger_phrase'

    Raises:
        EntryValidationError: If neither paths nor hf_repo_ids is provided
        EntryValidationError: If the number of locations, scales, and trigger phrases don't match
    """
    # Check that at least one location type is provided
    if not paths and not hf_repo_ids:
        raise EntryValidationError(
            "At least one of 'paths' or 'hf_repo_ids' must be provided"
        )
    
    # Determine which location type to use
    locations = paths if paths else hf_repo_ids
    location_key = "path" if paths else "hf_repo_id"
    
    # Check lengths match
    if len(locations) != len(scales) or len(locations) != len(trigger_phrases):
        raise EntryValidationError(
            f"Number of {location_key}s, scales, and trigger phrases must match"
        )

    entries = []
    for i in range(len(locations)):
        entry = {
            location_key: locations[i],
            "scale": scales[i],
            "trigger_phrase": trigger_phrases[i],
        }
        entries.append(entry)

    return entries


def display_profile(profile: LoRAProfile, show_entries: bool = False) -> None:
    """Display information about a LoRA profile.

    Args:
        profile: The LoRAProfile to display
        show_entries: Whether to show detailed information about each entry
    """
    print(f"- {profile.name}")
    print(f"  Description: {profile.description or 'N/A'}")
    print(f"  Created: {profile.created_at}")

    if show_entries:
        # Fetch entries
        entries = get_lora_entries(profile.id)
        
        if entries:
            print(f"  Entries: {len(entries)}")
            for i, entry in enumerate(entries):
                if entry.path:
                    print(f"    [{i+1}] Path: {entry.path}")
                elif entry.hf_repo_id:
                    print(f"    [{i+1}] Hugging Face: {entry.hf_repo_id}")
                print(f"        Scale: {entry.scale}")
                print(f"        Trigger phrase: {entry.trigger_phrase}")
        else:
            print("  Entries: None")


def handle_add(args) -> int:
    """Handle the 'add' subcommand.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        # Parse entries
        entries = parse_lora_entries(
            scales=args.lora_scales,
            trigger_phrases=args.trigger_phrases,
            paths=args.lora_paths,
            hf_repo_ids=args.hf_repo_ids,
        )
        
        # Register profile
        profile = register_lora_profile(
            name=args.name,
            lora_entries=entries,
            description=args.description,
        )
        
        print(f"LoRA profile '{profile.name}' registered successfully")
        print(f"- Description: {profile.description or 'N/A'}")
        print(f"- Entries: {len(entries)}")
        for i, entry in enumerate(entries):
            # Display location (path or hf_repo_id)
            if "path" in entry and entry["path"]:
                print(f"  [{i+1}] Path: {entry['path']}")
            elif "hf_repo_id" in entry and entry["hf_repo_id"]:
                print(f"  [{i+1}] Hugging Face: {entry['hf_repo_id']}")
            
            print(f"      Scale: {entry['scale']}")
            print(f"      Trigger phrase: {entry['trigger_phrase']}")
        
    except (ProfileExistsError, EntryValidationError, LoRAProfileError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1
    
    return 0


def handle_list(args) -> int:
    """Handle the 'list' subcommand.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    # List profiles
    profiles = list_lora_profiles()
    
    if profiles:
        print(f"Found {len(profiles)} LoRA profiles:")
        for profile in profiles:
            display_profile(profile, args.show_entries)
    else:
        print("No LoRA profiles found")

    return 0


def handle_delete(args) -> int:
    """Handle the 'delete' subcommand.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    # Check if profile exists
    profile = get_lora_profile(args.name)
    if not profile:
        print(f"Error: LoRA profile '{args.name}' not found", file=sys.stderr)
        return 1

    # Confirm deletion
    if not args.force:
        print(f"You are about to delete LoRA profile '{args.name}'.")
        print(f"Description: {profile.description or 'N/A'}")
        confirmation = input("Are you sure you want to proceed? [y/N] ")
        if confirmation.lower() not in ["y", "yes"]:
            print("Operation cancelled")
            return 0

    # Delete profile
    if delete_lora_profile(args.name):
        print(f"LoRA profile '{args.name}' deleted successfully")
    else:
        print(f"Error: Failed to delete LoRA profile '{args.name}'", file=sys.stderr)
        return 1

    return 0


def handle_update(args) -> int:
    """Handle the 'update' subcommand.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    # Get the profile
    profile = get_lora_profile(args.name)
    if not profile:
        print(f"Error: LoRA profile '{args.name}' not found", file=sys.stderr)
        return 1
    
    try:
        with Session(engine) as session:
            # Get the profile with entries for updating
            db_profile = session.exec(
                select(LoRAProfile).where(LoRAProfile.name == args.name)
            ).one()
            
            # Update profile name if provided
            if args.new_name:
                # Check if the new name already exists
                if args.new_name != args.name:
                    try:
                        get_lora_profile(args.new_name)
                        print(f"Error: LoRA profile '{args.new_name}' already exists", file=sys.stderr)
                        return 1
                    except ProfileNotFoundError:
                        # This is what we want - the name should not exist
                        pass
                db_profile.name = args.new_name
                
            # Update description if provided
            if args.description is not None:  # Allow empty description
                db_profile.description = args.description
            
            # Get entries
            entries = get_lora_entries(profile.id)
            
            # Handle entry operations
            if args.add_entry:
                # Validate required fields for a new entry
                has_location = bool(args.path or args.hf_repo_id)
                if not has_location or args.scale is None or not args.trigger_phrase:
                    print("Error: Location (--path or --hf-repo-id), --scale, and --trigger-phrase are required when adding an entry", file=sys.stderr)
                    return 1
                
                # Create a new entry
                new_entry = LoRAEntry(
                    profile_id=profile.id,
                    path=args.path,
                    hf_repo_id=args.hf_repo_id,
                    scale=args.scale,
                    trigger_phrase=args.trigger_phrase,
                    order=len(entries)  # Add to the end
                )
                
                # Validate the entry
                if not new_entry.validate():
                    raise EntryValidationError("Entry must have either path or hf_repo_id")
                
                session.add(new_entry)
                
                # Display message with the appropriate location type
                location_msg = f"Path={args.path}" if args.path else f"Hugging Face={args.hf_repo_id}"
                print(f"Added new entry: {location_msg}, Scale={args.scale}, Trigger phrase={args.trigger_phrase}")
                
            elif args.remove_entry:
                # Validate entry index
                if args.remove_entry < 1 or args.remove_entry > len(entries):
                    raise EntryIndexError(f"Entry index {args.remove_entry} is out of range (1-{len(entries)})")
                
                # Get the entry to remove (adjust for 0-based index)
                entry_to_remove = entries[args.remove_entry - 1]
                session.delete(entry_to_remove)
                
                # Update order of remaining entries
                for i, entry in enumerate([e for e in entries if e.id != entry_to_remove.id]):
                    entry.order = i
                    session.add(entry)
                
                print(f"Removed entry #{args.remove_entry}: {entry_to_remove.path}")
                
            elif args.update_entry:
                # Validate entry index
                if args.update_entry < 1 or args.update_entry > len(entries):
                    raise EntryIndexError(f"Entry index {args.update_entry} is out of range (1-{len(entries)})")
                
                # Get the entry to update (adjust for 0-based index)
                entry_to_update = entries[args.update_entry - 1]
                
                # Update fields if provided
                if args.path:
                    entry_to_update.path = args.path
                    entry_to_update.hf_repo_id = None  # Clear hf_repo_id if path is set
                elif args.hf_repo_id:
                    entry_to_update.hf_repo_id = args.hf_repo_id
                    entry_to_update.path = None  # Clear path if hf_repo_id is set
                
                if args.scale is not None:
                    entry_to_update.scale = args.scale
                if args.trigger_phrase:
                    entry_to_update.trigger_phrase = args.trigger_phrase
                
                # Validate the updated entry
                if not entry_to_update.validate():
                    raise EntryValidationError("Entry must have either path or hf_repo_id")
                    
                session.add(entry_to_update)
                print(f"Updated entry #{args.update_entry}")
            
            # Commit changes
            session.commit()
            
            # Show the updated profile
            profile_name = args.new_name if args.new_name else args.name
            print(f"LoRA profile '{profile_name}' updated successfully")
            
            # Re-fetch to get updated entries
            updated_profile = get_lora_profile(profile_name)
            updated_entries = get_lora_entries(updated_profile.id)
            
            print(f"- Description: {updated_profile.description or 'N/A'}")
            print(f"- Entries: {len(updated_entries)}")
            for i, entry in enumerate(updated_entries):
                if entry.path:
                    print(f"  [{i+1}] Path: {entry.path}")
                elif entry.hf_repo_id:
                    print(f"  [{i+1}] Hugging Face: {entry.hf_repo_id}")
                print(f"      Scale: {entry.scale}")
                print(f"      Trigger phrase: {entry.trigger_phrase}")
            
    except (ProfileNotFoundError, EntryValidationError, EntryIndexError, LoRAProfileError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1
    
    return 0


def main() -> int:
    """Main entry point for the command-line tool.
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    # Initialize database
    init_db()
    
    # Create main parser
    parser = argparse.ArgumentParser(
        description="Manage LoRA profiles for mflux."
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Add subcommand
    add_parser = subparsers.add_parser("add", help="Add a new LoRA profile")
    add_parser.add_argument("--name", type=str, required=True, help="Name of the LoRA profile")
    add_parser.add_argument("--description", type=str, help="Description of the LoRA profile")
    
    # Location group (either paths or hf-repo-ids must be provided)
    location_group = add_parser.add_mutually_exclusive_group(required=True)
    location_group.add_argument("--lora-paths", type=str, nargs="+", help="Local paths to LoRA files")
    location_group.add_argument("--hf-repo-ids", type=str, nargs="+", help="Hugging Face repository IDs for LoRA files")
    
    add_parser.add_argument("--lora-scales", type=float, nargs="+", required=True, help="Scales for LoRA files")
    add_parser.add_argument("--trigger-phrases", type=str, nargs="+", required=True, help="Trigger phrases for LoRA files")
    
    # List subcommand
    list_parser = subparsers.add_parser("list", help="List all LoRA profiles")
    list_parser.add_argument("--show-entries", action="store_true", help="Show detailed information about each entry")
    
    # Delete subcommand
    delete_parser = subparsers.add_parser("delete", help="Delete a LoRA profile")
    delete_parser.add_argument("--name", type=str, required=True, help="Name of the LoRA profile to delete")
    delete_parser.add_argument("--force", action="store_true", help="Delete without confirmation")
    
    # Update subcommand
    update_parser = subparsers.add_parser("update", help="Update an existing LoRA profile")
    update_parser.add_argument("--name", type=str, required=True, help="Name of the LoRA profile to update")
    update_parser.add_argument("--new-name", type=str, help="New name for the profile")
    update_parser.add_argument("--description", type=str, help="New description for the profile")
    
    # For entry modification in update
    update_parser.add_argument("--add-entry", action="store_true", help="Add a new entry to the profile")
    update_parser.add_argument("--remove-entry", type=int, help="Remove an entry by its index (starting with 1)")
    update_parser.add_argument("--update-entry", type=int, help="Update an entry by its index (starting with 1)")
    
    # Entry details for update
    location_group_update = update_parser.add_mutually_exclusive_group()
    location_group_update.add_argument("--path", type=str, help="Path to LoRA file (local file)")
    location_group_update.add_argument("--hf-repo-id", type=str, help="Hugging Face repository ID for LoRA")
    update_parser.add_argument("--scale", type=float, help="Scaling factor for LoRA")
    update_parser.add_argument("--trigger-phrase", type=str, help="Trigger phrase for LoRA")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Handle commands
    if args.command == "add":
        return handle_add(args)
    elif args.command == "list":
        return handle_list(args)
    elif args.command == "delete":
        return handle_delete(args)
    elif args.command == "update":
        return handle_update(args)
    else:
        parser.print_help()
        return 1


# For development/testing purposes
if __name__ == "__main__":
    sys.exit(main())
