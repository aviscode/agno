"""
Control Memory Database Tools - Add, Update, Delete, and Clear Operations

This cookbook demonstrates how to control which memory database operations
are available to the AI model using the four DB tools parameters:
- add_memories: Controls whether the AI can add new memories
- update_memories: Controls whether the AI can update existing memories  
- delete_memories: Controls whether the AI can delete individual memories
- clear_memories: Controls whether the AI can clear all memories

These parameters provide fine-grained control over memory operations for security
and functionality purposes.
"""

from agno.agent.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.memory.manager import MemoryManager
from agno.models.openai import OpenAIChat
from rich.pretty import pprint

# Setup database and user
memory_db = SqliteDb(db_file="tmp/memory_control_demo.db")
john_doe_id = "john_doe@example.com"

print("=" * 80)
print("MEMORY DB TOOLS CONTROL DEMONSTRATION")
print("=" * 80)

# Example 1: Full Memory Control (Default - All Operations Enabled)
print("\n1. DEFAULT SETUP - All memory operations enabled")
print("-" * 50)

memory_manager_full = MemoryManager(
    model=OpenAIChat(id="gpt-4o"),
    db=memory_db,
    # These are the default values (all True)
    add_memories=True,
    update_memories=True, 
    delete_memories=True,
    clear_memories=True,
)

agent_full = Agent(
    model=OpenAIChat(id="gpt-4o"),
    memory_manager=memory_manager_full,
    enable_user_memories=True,
    db=memory_db,
)

# Add initial memory
agent_full.print_response(
    "My name is John Doe and I like to hike in the mountains on weekends. I also enjoy photography.",
    stream=True,
    user_id=john_doe_id,
)

# Test memory recall
agent_full.print_response("What are my hobbies?", stream=True, user_id=john_doe_id)

# Test memory update
agent_full.print_response(
    "I no longer enjoy photography. Instead, I've taken up rock climbing.",
    stream=True,
    user_id=john_doe_id,
)

print("\nMemories after update:")
memories = memory_manager_full.get_user_memories(user_id=john_doe_id)
pprint([m.memory for m in memories] if memories else [])

print("\n" + "=" * 80)

# Example 2: Read-Only Memory (No modifications allowed)
print("\n2. READ-ONLY SETUP - No memory modifications allowed")
print("-" * 50)

memory_manager_readonly = MemoryManager(
    model=OpenAIChat(id="gpt-4o"),
    db=memory_db,
    add_memories=False,      # Cannot add new memories
    update_memories=False,   # Cannot update existing memories
    delete_memories=False,   # Cannot delete memories
    clear_memories=False,    # Cannot clear all memories
)

agent_readonly = Agent(
    model=OpenAIChat(id="gpt-4o"),
    memory_manager=memory_manager_readonly,
    enable_user_memories=True,
    db=memory_db,
)

# Try to add new information (should not create memory)
agent_readonly.print_response(
    "I also like to cook Italian food and play chess on Sundays.",
    stream=True,
    user_id=john_doe_id,
)

# Try to update existing memory (should not work)
agent_readonly.print_response(
    "Actually, I prefer mountain biking over hiking now.",
    stream=True,
    user_id=john_doe_id,
)

print("\nMemories after read-only operations (should be unchanged):")
memories = memory_manager_readonly.get_user_memories(user_id=john_doe_id)
pprint([m.memory for m in memories] if memories else [])

print("\n" + "=" * 80)

# Example 3: Add-Only Memory (Can add but not modify existing)
print("\n3. ADD-ONLY SETUP - Can add memories but not modify existing ones")
print("-" * 50)

memory_manager_addonly = MemoryManager(
    model=OpenAIChat(id="gpt-4o"),
    db=memory_db,
    add_memories=True,       # Can add new memories
    update_memories=False,   # Cannot update existing memories
    delete_memories=False,   # Cannot delete memories
    clear_memories=False,    # Cannot clear all memories
)

agent_addonly = Agent(
    model=OpenAIChat(id="gpt-4o"),
    memory_manager=memory_manager_addonly,
    enable_user_memories=True,
    db=memory_db,
)

# Add new information (should work)
agent_addonly.print_response(
    "I've started learning Spanish and I volunteer at the local animal shelter.",
    stream=True,
    user_id=john_doe_id,
)

# Try to modify existing memory (should not work)
agent_addonly.print_response(
    "I want to completely forget about rock climbing.",
    stream=True,
    user_id=john_doe_id,
)

print("\nMemories after add-only operations:")
memories = memory_manager_addonly.get_user_memories(user_id=john_doe_id)
pprint([m.memory for m in memories] if memories else [])

print("\n" + "=" * 80)