# Copilot Instructions for A2A Task Management Project

<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

This is an Agent-to-Agent (A2A) protocol project for distributed task management. The project consists of multiple specialized agents that communicate through the A2A protocol.

## Project Architecture

- **Supervisor Agent**: Receives missions/tasks and divides work among other agents
- **Milestone Agent**: Creates timeline planning and milestone breakdowns
- **Task Agent**: Breaks down milestones into detailed tasks with time estimates
- **Resource Agent**: Handles team allocation and resource management

## Key Guidelines

1. All inter-agent communication must use the A2A protocol
2. Each agent should have its own agent card (/.well-known/agent.json)
3. Use async/await for all agent communications
4. Implement proper error handling for network communications
5. Follow the A2A message format for all agent interactions
6. Each agent should be independently runnable as a service
7. Use dependency injection for agent client configurations

## Code Style

- Use Python asyncio for concurrent operations
- Follow PEP 8 styling guidelines
- Use type hints for all function parameters and return values
- Implement proper logging for debugging and monitoring
- Use environment variables for configuration
