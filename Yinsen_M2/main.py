import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#print(os.getcwd())
#print(os.listdir('./core_engines'))

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
#print(os.path.dirname(os.path.abspath(__file__)))

from core_engines.streams.text.text_input import TextInput
from core_engines.streams.text.text_output import TextOutput
from core_engines.streams.audio.audio_input import AudioInput
from core_engines.streams.audio.audio_output import AudioOutput

from core_engines.multi_agent_model.MAS_system_1 import MAS_system_1

import logging
import yaml
from typing import Optional, Dict, Any
from pathlib import Path
import time
import re
import json

class JARVIS:
    """
    Main assistant agent class that orchestrates all components of Jarvis
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config(config_path)
        self.running = False

        #print(f"DEBUG: Config: {self.config}")
        
        # Initialize logging and components
        self._init_logging()
        self._init_components()
        
        # init data dir
        os.makedirs('./data', exist_ok=True)
        self.calender_logs_path, self.notification_logs_path = self.init_calender_and_notification_logs(self.config['calender_and_logs'])
        
        # Initialize MAS
        self.mas = MAS_system_1(self.config, self.logger, self.text_output)

        # Set current active agent to orchestrator initially
        self.current_agent = self.mas.get_current_agent()

        
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from yaml file"""
        if config_path is None:
            config_path = os.environ.get('CONFIG_PATH', os.path.join(os.getcwd(), 'config', 'config.yaml'))
            
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            raise
            
    def _init_logging(self):
        """Initialize logging configuration"""
        self._setup_logging()
        
    def _setup_logging(self):
        """Configure logging to write to both file and console"""
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.join(os.getcwd(), 'logs'), exist_ok=True)
        
        # Get root logger
        root_logger = logging.getLogger()
        
        # Remove any existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Create file handler
        log_path = os.path.join(os.getcwd(), self.config['logging']['file'])
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(logging.WARNING)  # Set to WARNING level
        file_handler.setFormatter(
            logging.Formatter(self.config['logging']['format'])
        )
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)  # Set to WARNING level
        console_handler.setFormatter(
            logging.Formatter('%(levelname)s: %(message)s')
        )
        
        # Add both handlers to root logger
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        root_logger.setLevel(logging.WARNING)  # Set root logger to WARNING level
        
    def _init_components(self):
        """Initialize all component subsystems"""
        try:
            # Initialize text I/O
            self.text_input = TextInput(self.config['sensors']['text'])
            self.text_output = TextOutput("JARVIS", self.config['sensors']['text'])
            
            # Initialize audio output
            try:
                if self.config['sensors']['audio']['output']['enabled']:
                    self.audio_output = AudioOutput(self.config['sensors']['audio']['output'])
                    self.logger.info("✓ Audio output initialized")
                else:
                    self.audio_output = None
            except Exception as e:
                self.logger.error(f"Failed to initialize audio output: {e}")
                self.audio_output = None
            
            # Initialize audio input without energy callback
            try:
                if self.config['sensors']['audio']['input']['enabled']:
                    # Use config directly, no energy callback
                    self.audio_input = AudioInput(
                        self.config['sensors']['audio']['input'],
                        on_wake_word=self._on_wake_word_detected
                    )
                    self.logger.info("✓ Audio input initialized")
                else:
                    self.audio_input = None
            except Exception as e:
                self.logger.error(f"Failed to initialize audio input: {e}")
                self.audio_input = None
            
            # Initialize other sensors (placeholder for future implementation)
            self.sensors = {}
            if self.config['sensors']['vision']['enabled']:
                self.logger.info("Vision sensor enabled but not yet implemented")
            if self.config['sensors']['environment']['enabled']:
                self.logger.info("Environment sensor enabled but not yet implemented")
                
        except Exception as e:
            self.logger.error(f"Error initializing components: {e}")
            raise

    def init_calender_and_notification_logs(self,
                               calender_logs_path
                               ):
        
        #print(f"DEBUG: Calender logs path: {calender_logs_path}")

        #save the calender_logs and notification_logs to a file
        if not os.path.exists(calender_logs_path['calender_logs_path']):
            self.calender_logs = { 'logs': [] }
            with open(calender_logs_path['calender_logs_path'], "w") as f:
                json.dump(self.calender_logs, f)

        if not os.path.exists(calender_logs_path['notification_logs_path']):
            self.notification_logs = { 'logs': [] }
            with open(calender_logs_path['notification_logs_path'], "w") as f:
                json.dump(self.notification_logs, f)

        return calender_logs_path['calender_logs_path'], calender_logs_path['notification_logs_path']

    def start(self):
        """Start Jarvis"""
        try:
            self.running = True
            self.logger.info(f"Starting JARVIS multi-agent system")
            
            # Display and speak welcome message
            welcome_msg = f"JARVIS multi-agent system initialized. Starting with {self.current_agent.agent_name} agent."
            self.text_output.display(welcome_msg)
            if self.audio_output:
                self.audio_output.speak(welcome_msg)
            
            # Start text input processing
            self.text_input.start()
            
            # Start audio input processing if enabled
            if self.audio_input:
                self.audio_input.start()
                self.logger.info("Voice commands enabled. Say the wake word to activate.")
            
            # Main loop
            self._main_loop()
            
        except Exception as e:
            self.logger.error(f"Error in assistant agent: {e}")
            self.stop()
            
    def stop(self):
        """Stop Jarvis"""
        self.running = False
        goodbye_msg = "Shutting down. Goodbye!"
        self.text_output.display(goodbye_msg)
        if self.audio_output:
            self.audio_output.speak(goodbye_msg)
        self.text_input.stop()
        if self.audio_input:
            self.audio_input.stop()
        self.logger.info(f"JARVIS multi-agent system stopped")

    def _main_loop(self):
        """Main processing loop"""
        while self.running:
            try:
                # Check both text and voice inputs
                text_input = self.text_input.get_input(timeout=0.1)
                voice_input = self.audio_input.get_input(timeout=0.1) if self.audio_input else None
                
                # Process text input if available
                if text_input:
                    _ = self._handle_user_input(text_input, response_format='HTML')
                
                # Process voice input if available
                if voice_input:
                    self.text_output.display(f"You said: {voice_input}")
                    _ = self._handle_user_input(voice_input, response_format='TEXT')
                    
            except KeyboardInterrupt:
                self.text_output.display("Received shutdown signal. Shutting down")
                self.stop()
                break
            
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                
    def _handle_user_input(self, 
                           user_input: str, 
                           response_format: str = 'TEXT' # 'TEXT' or 'HTML'
                           ):
        """Handle user input from any source"""
        # Process shutdown commands
        if any(keyword in user_input.lower() for keyword in ['exit', 'quit', 'shutdown']):
            self.text_output.display("Shutting down")
            self.stop()
            return
            
        # Get response from MAS system -------------------------------------------------------------
        response = self.get_response_from_MAS_system(user_input, response_format=response_format)
        
        #print(f"\nDEBUG: Raw raw response from main LLM agentaw_r: {raw_response}")

        # Display the response to the user in terminal and "local" audio output (if enabled) -------------------------------------------------------------
        if response['final_response_to_user']:
            display_msg = f"{self.current_agent.agent_name}: {response['final_response_to_user']}"
            #print(f"DEBUG: Display message: {display_msg}")
            self.text_output.display(display_msg)
            
            # Speak the response if audio output is enabled
            if self.audio_output:
                self.audio_output.speak(response['final_response_to_user'])
        
        # return reponse to frontend/api
        print(f"DEBUG: Response: {response}")
        return response

    def get_response_from_MAS_system(self, user_input: str, response_format: str) -> Dict[str, Any]:
        """Process user input and return response dictionary"""
        try:
            # Get reponse from MAS model 1
            response_dict, current_agent = self.mas.get_response_from_mas_system(user_input, self.current_agent, response_format=response_format)
            self.current_agent = current_agent
            return response_dict
            
        except Exception as e:
            self.logger.error(f"Error processing input: {e}")            
            return f"Error: {str(e)}"


def main():
    """Main entry point"""
    try:
        jarvis = JARVIS()
        jarvis.start()
    except Exception as e:
        logging.error(f"Error in main: {e}")
        
if __name__ == "__main__":
    main()
