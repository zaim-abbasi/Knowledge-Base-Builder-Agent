"""
Demonstration script for KnowledgeBaseBuilderAgent usage.
"""

from agents.workers.knowledge_base_builder_agent import KnowledgeBaseBuilderAgent


def main():
    # Create an instance of the KnowledgeBaseBuilderAgent
    agent = KnowledgeBaseBuilderAgent(
        agent_id="kb_builder_001",
        supervisor_id="supervisor_001"
    )
    
    print("=" * 60)
    print("KnowledgeBaseBuilderAgent Demo")
    print("=" * 60)
    print()
    
    # Example 1: Overwrite mode (default)
    print("Example 1: Overwriting wiki content")
    print("-" * 60)
    task_data_1 = {
        "wiki_update_content": "# Team Wiki\n\n## Project Overview\nThis is the main project documentation.",
        "update_mode": "overwrite"
    }
    result_1 = agent.process_task(task_data_1)
    print(f"Result: {result_1}")
    print()
    
    # Example 2: Append mode
    print("Example 2: Appending to wiki content")
    print("-" * 60)
    task_data_2 = {
        "wiki_update_content": "## Daily Updates\n- Completed task A\n- Started task B",
        "update_mode": "append"
    }
    result_2 = agent.process_task(task_data_2)
    print(f"Result: {result_2}")
    print()
    
    # Example 3: Read from LTM
    print("Example 3: Reading wiki content from LTM")
    print("-" * 60)
    wiki_content = agent.get_wiki_content()
    print(f"Current wiki content:\n{wiki_content}")
    print()
    
    # Example 4: Send a message
    print("Example 4: Sending a completion message")
    print("-" * 60)
    completion_message = {
        "type": "completion_report",
        "task_id": "task_123",
        "status": "completed",
        "summary": "Wiki updated successfully"
    }
    agent.send_message("supervisor_001", completion_message)
    print()
    
    # Example 5: Error handling - missing parameter
    print("Example 5: Error handling - missing parameter")
    print("-" * 60)
    invalid_task = {
        "update_mode": "overwrite"
        # Missing wiki_update_content
    }
    result_error = agent.process_task(invalid_task)
    print(f"Result: {result_error}")
    print()
    
    print("=" * 60)
    print("Demo completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()

