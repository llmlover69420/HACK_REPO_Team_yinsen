# Jarvis

A local AI assistant powered by OpenAI's GPT models with text interface and task management capabilities.

## Prerequisites

1. Python 3.9 or higher
2. OpenAI API key (get it from https://platform.openai.com/api-keys)
3. Git (for cloning the repository)

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd jarvis
   ```

2. **Create Virtual Environment and Install Dependencies**
   ```bash
   ./scripts/create_venv.sh
   ```
   This will:
   - Create a Python virtual environment
   - Install required dependencies
   - Create a template .env file

3. **Configure OpenAI API Key**
   - Open the `.env` file in the root directory
   - Replace `your_api_key_here` with your actual OpenAI API key:
     ```
     OPENAI_API_KEY=sk-your-actual-api-key
     ```

## Usage

1. **Start Jarvis**
   ```bash
   ./scripts/run_in_venv.sh
   ```

2. **Interact with Jarvis**
   - Type your messages and press Enter
   - Use commands:
     - `exit`, `quit`, or `shutdown` to close Jarvis
     - More commands coming soon...

3. **Features**
   - Natural language conversation
   - Conversation history persistence
   - Clear error handling and logging

## Project Structure

## Features
- WakeUp Manager: An alarm clock that persuades you to wake up.
- Task Management: Uses LLM reasoning for job and task management.
- Proactive Reminders: Keeps track of tasks and deadlines.
- Note/Documentation Maintainer: Manages notes and documentation for tasks.
- Environmental Awareness: Tracks user activity and provides motivation.

## Roadmap
- Implement additional features like Google search and YouTube search.
- Enhance environmental awareness capabilities.

## Contributing
Feel free to contribute by submitting issues or pull requests.

A. Core Components:
1. core/agents/llm_agent.py (Base LLM functionality)
2. core/agents/assistant_agent.py (Main assistant logic)
3. core/utils/helper_functions.py (Shared utilities)

B. Sensors:
4. core/sensors/audio/audio_sensor.py
5. core/sensors/vision/vision_sensor.py
6. core/sensors/environment/environment_sensor.py

C. Custom Tools:
7. external_tools/custom/task_manager.py
8. external_tools/custom/alarm_clock.py

D. Standard Integrations:
9. external_tools/standard/google_search.py
10. external_tools/standard/youtube_search.py