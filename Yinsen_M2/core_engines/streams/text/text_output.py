import logging
from datetime import datetime

class TextOutput:
    def __init__(self, agent_name, config: dict):
        self.agent_name = agent_name
        self.config = config
        self.logger = logging.getLogger(agent_name)
        self.log_file = config.get('log_file', 'data/chat_history.log')
        
    def display(self, text: str):
        """Display text output with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_text = f"[{timestamp}] {self.agent_name}: {text}"
        print(formatted_text)
        self._log_output(formatted_text)
        
    def _log_output(self, text: str):
        """Log output to file"""
        try:
            with open(self.log_file, 'a') as f:
                f.write(f"{text}\n")
        except Exception as e:
            self.logger.error(f"Error logging output: {e}")
            
    def clear(self):
        """Clear the screen"""
        print("\033[H\033[J", end="") 