"""
Migration script to add prompt_arg_names to existing agents.

This script:
1. Scans all agents in the database
2. Finds agents with uses_prompt_args=True that don't have prompt_arg_names set
3. Extracts prompt arg names from the prompt using regex (finds {arg_name} patterns)
4. Updates the agent with the extracted prompt_arg_names

Run this script once to migrate existing agents.
"""

import re
import json
import sys
sys.path.append("../")

from src.Models import Agent
from src.AWS.DynamoDB import get_all_items


def extract_prompt_arg_names(prompt: str) -> list[str]:
    """
    Extract prompt argument names from a prompt string.
    Finds all occurrences of {arg_name} pattern and returns them INCLUDING the brackets.
    
    For example, a prompt with "{user_name}" will return ["{user_name}"]
    This is for backwards compatibility - the full string including brackets is the arg name.
    
    Args:
        prompt: The prompt string to extract from
        
    Returns:
        List of unique argument patterns found in the prompt (including brackets)
    """
    # Pattern matches {word} - captures the FULL match including brackets
    # Only matches simple identifiers (not JSON-like patterns with colons, quotes, etc.)
    pattern = r'\{[a-zA-Z_][a-zA-Z0-9_]*\}'
    matches = re.findall(pattern, prompt)
    # Return unique names while preserving order
    seen = set()
    unique_names = []
    for name in matches:
        if name not in seen:
            seen.add(name)
            unique_names.append(name)
    return unique_names


def migrate_agents():
    """
    Migrate all existing agents that use prompt_args but don't have prompt_arg_names.
    """
    # Get all agents from the database
    table_name = Agent.AGENTS_TABLE_NAME
    all_items = get_all_items(table_name)
    
    print(f"Found {len(all_items)} total agents in the database")
    
    migrated_count = 0
    skipped_count = 0
    
    for item in all_items:
        try:
            agent = Agent.Agent(**item)
            
            # Check if agent uses prompt args but doesn't have prompt_arg_names
            if agent.uses_prompt_args:
                # Check if prompt_arg_names is empty or not set
                if not agent.prompt_arg_names or len(agent.prompt_arg_names) == 0:
                    # Extract prompt arg names from the prompt
                    extracted_names = extract_prompt_arg_names(agent.prompt)
                    
                    if extracted_names:
                        print(f"\nMigrating agent: {agent.agent_id}")
                        print(f"  Name: {agent.agent_name}")
                        print(f"  Extracted prompt_arg_names: {extracted_names}")
                        
                        # Update the agent with the extracted names
                        agent.prompt_arg_names = extracted_names
                        Agent.save_agent(agent)
                        
                        migrated_count += 1
                    else:
                        print(f"\nSkipping agent {agent.agent_id} - uses_prompt_args=True but no args found in prompt")
                        skipped_count += 1
                else:
                    print(f"\nSkipping agent {agent.agent_id} - already has prompt_arg_names: {agent.prompt_arg_names}")
                    skipped_count += 1
                    
        except Exception as e:
            print(f"\nError processing agent item: {e}")
            continue
    
    print(f"\n\nMigration complete!")
    print(f"  Migrated: {migrated_count} agents")
    print(f"  Skipped: {skipped_count} agents")


if __name__ == "__main__":
    print("Starting prompt_arg_names migration...")
    print("=" * 50)
    migrate_agents()
