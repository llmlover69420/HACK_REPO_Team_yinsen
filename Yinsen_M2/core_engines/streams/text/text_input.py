from typing import Optional
import logging
from queue import Queue
import threading

class TextInput:
    def __init__(self, config: dict):
        self.config = config
        self.input_queue = Queue()
        self.running = False
        self.logger = logging.getLogger(__name__)
        
        # Configure history
        self.history_size = config.get('history_size', 1000)
        self.history = []
        
    def start(self):
        """Start the text input listener"""
        self.running = True
        self.input_thread = threading.Thread(target=self._input_loop)
        self.input_thread.daemon = True
        self.input_thread.start()
        
    def stop(self):
        """Stop the text input listener"""
        self.running = False
        
    def _input_loop(self):
        """Main input loop"""
        while self.running:
            try:
                print("> ", end='', flush=True)  # Add explicit prompt with flush
                user_input = input().strip()  # Remove the prompt from input() itself
                if user_input:
                    self._add_to_history(user_input)
                    self.input_queue.put(user_input)
            except EOFError:
                self.running = False
            except Exception as e:
                self.logger.error(f"Error in input loop: {e}")
                
    def _add_to_history(self, text: str):
        """Add input to history, maintaining size limit"""
        self.history.append(text)
        if len(self.history) > self.history_size:
            self.history.pop(0)
            
    def get_input(self, timeout: Optional[float] = None) -> Optional[str]:
        """Get next input from queue"""
        try:
            return self.input_queue.get(timeout=timeout)
        except:
            return None
            
    def get_history(self) -> list:
        """Return input history"""
        return self.history.copy() 