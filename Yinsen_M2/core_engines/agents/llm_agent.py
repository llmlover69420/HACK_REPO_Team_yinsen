import logging
import openai
from openai import OpenAI
from typing import Optional, Dict, List, Any, Tuple
import os
from dotenv import load_dotenv
import json
import gzip
from pathlib import Path
import tempfile
import re
from core_engines.utils.utils import get_formatted_datetime
class LLMAgent:
    """
    LLM-powered agent that can generate responses to user queries
    """
    
    def __init__(self, agent_name: str, 
                 config: Dict[str, Any], 
                 agent_type: str = "orchestrator",
                 agent_category: str = "main", # main, helper
                 agent_type_to_name_map: Dict[str, str] = None):
        
        self.logger = logging.getLogger(__name__)
        self.agent_name = agent_name
        self.agent_type = agent_type
        self.agent_category = agent_category
        self.config = config
        self.model_type = config.get('type', 'openai')
        self.model_name = config.get('model', 'gpt-4o-mini')
        
        # Get agent-specific config
        agent_config = config.get(agent_type, {})
        #print(f"DEBUG: Agent config: {agent_config}")
        
        # Load agent-category-specific general instructions
        self._load_general_instructions()

        # Load agent-specific instructions or default to empty
        self._load_agent_instructions(agent_config)

        # Combine general instructions and agent-specific instructions
        # add agent name to the system instructions
        self.system_instructions = self.general_instructions + \
                                   '\n\nNow, Your name is ' + self.agent_name + '. You are the user\'s ' + self.agent_type + '. \n' + \
                                    self.system_instructions
        self.agent_type_to_name_map = agent_type_to_name_map
        #print('SYSTEM INSTRUCTIONS:', self.system_instructions)

        # Get agent-specific parameters or default to config values
        self.temperature = agent_config.get('temperature', config.get('temperature', 0.7))
        self.max_tokens = agent_config.get('max_tokens', config.get('max_tokens', 1000))
        self.top_p = agent_config.get('top_p', config.get('top_p', 0.9))
        self.frequency_penalty = agent_config.get('frequency_penalty', config.get('frequency_penalty', 0.0))
        self.presence_penalty = agent_config.get('presence_penalty', config.get('presence_penalty', 0.0))
        
        # Initialize clients
        self._init_clients()
        
        # Initialize conversation history
        self.conversation_history = []
        
        # Get agent-specific history file from config
        self.history_file = agent_config.get('history_file', 'data/random_conversation_history.json.gz')
        #print(f"DEBUG: History file: {self.history_file}")

        # Load conversation history
        self._load_conversation_history()
        
        self.logger.info(f"LLM Agent {agent_name} ({agent_type}) initialized with {self.model_type} model: {self.model_name}")
    
    def _load_general_instructions(self):
        """Load general instructions from file"""
        if self.agent_category == 'main':
            general_instructions_file = self.config.get('general_main_instructions', '')
        elif self.agent_category == 'helper':
            general_instructions_file = self.config.get('general_helper_instructions', '')
        else:
            general_instructions_file = ''
        if general_instructions_file:
            with open(general_instructions_file, 'r') as f:
                self.general_instructions = f.read()
        else:
            self.general_instructions = ''

    def _load_agent_instructions(self, agent_config):
        """Load agent instructions from file"""
        self.system_instructions = agent_config.get('instructions', '')
        
        # read system instruction txt
        with open(self.system_instructions, 'r') as f:
            self.system_instructions = f.read()
        #print(f"DEBUG: System instructions: {self.system_instructions[:20]}")

    def _init_clients(self):
        """Initialize API clients based on model type"""
        if self.model_type == 'openai':
            openai_api_key = os.environ.get('OPENAI_API_KEY')
            if not openai_api_key:
                self.logger.error("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
            self.client = openai.OpenAI(api_key=openai_api_key)
        else:
            self.logger.error(f"Unsupported model type: {self.model_type}")
            self.client = None

    def process_input_prompt(self, user_input: str) -> str:
        """Process the user input prompt"""
        
        # Construct messages including system instructions
        messages = []
        if self.system_instructions:
            messages.append({
                "role": "system",
                "content": self.system_instructions
            })
        
        # add system data
        current_datetime = get_formatted_datetime()
        messages.append({
            "role": "system",
            "content": f"Following is the current system data. Use this when needed: \
                         current_datetime: {current_datetime} | \
                         current_agent: {self.agent_name} | \
                         current_agent_type: {self.agent_type} | \
                         current_agent_category: {self.agent_category}"
            })
        
        # add agent type to name map
        messages.append({
            "role": "system",
            "content": f"Following is the agent type to name map. Use this when needed: \
                         {self.agent_type_to_name_map}"
        })

        # Add conversation history (limited to last 100 messages to save tokens)
        for msg in self.conversation_history[-10:]:
            messages.append(msg)
        #print(f"DEBUG: Conversation history: {self.conversation_history[-100:]}")
        # Add current user input first
        messages.append({
            "role": "user",
            "content": user_input
        })

        # final reminder to follow the format
        messages.append({
            "role": "system",
            "content": "Most importantly, follow the reponse format constraints strictly. Do not include any other text or comments. Always follow the response format constraints."
        })

        return messages
    
    def generate_response(self, user_input: str) -> Dict[str, Any]:
        """
        Generate a response to the user input and return a structured response
        
        Returns:
            Dict with the following keys:
            - response_to_user: The main response to display to the user
            - detailed_response: The full detailed response (if applicable)
        """
        try:
            
            # Add user message to history
            self.conversation_history.append({
            "role": "user",
            "content": user_input
            })

            # process input prompt and get messages ----------------------------------------------------
            messages = self.process_input_prompt(user_input)

            #print(f"\nAPI CALL INPUT: {messages}")

            # generate response ------------------------------------------------------------------------
            if self.model_type == 'openai':
                #print(f"API CALL INPUT: {messages}")
                response = self._generate_response_openai(messages)

            else:
                self.logger.error(f"Unsupported model type: {self.model_type}")
                return {
                    "response_to_user": "I'm sorry, but I encountered an error with my language model.",
                    "detailed_response": "Unsupported model type"
                }
                
            # Add assistant response to history (only the user-facing part) ---------------------------
            self.conversation_history.append({
                "role": "assistant",
                "content": response
            })
            
            # Save updated conversation history
            self._save_conversation_history()
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return {
                "response_to_user": "I apologize, but I encountered an error processing your request.",
                "detailed_response": f"Error: {str(e)}"
            }
    
    def _generate_response_openai(self, messages: List[Dict[str, str]]) -> str:
        """Generate response using OpenAI API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            raw_response = response.choices[0].message.content
            #print('\nRAW RESPONSE FROM OPENAI:', raw_response)
            return raw_response
            
        except Exception as e:
            self.logger.error(f"Error from OpenAI API: {e}")
            raise
    
    '''
    def _parse_response(self, raw_response: str) -> Dict:
        """Parse the raw response into structured format"""
        try:
            # Initialize default values
            parsed_response = {
                "response_to_user": "",
                "detailed_response": "",
                "invoke_another_agent_flag": False,
                "invoke_agent_name": ""
            }
            
            #print('\nRAW RESPONSE FROM PARSE:', raw_response)

            # Extract sections using regex
            response_match = re.search(r'\[response_to_user\]:\s*(.*?)(?=\[|$)', raw_response, re.DOTALL)
            detailed_match = re.search(r'\[detailed_response\]:\s*(.*?)(?=\[|$)', raw_response, re.DOTALL)
            flag_match = re.search(r'\[invoke_another_agent_flag\]:\s*(.*?)(?=\[|$)', raw_response, re.DOTALL)
            agent_match = re.search(r'\[invoke_agent_name\]:\s*(.*?)(?=\[|$)', raw_response, re.DOTALL)
            
            # Update parsed response with matches
            if response_match:
                parsed_response["response_to_user"] = response_match.group(1).strip()
            if detailed_match:
                parsed_response["detailed_response"] = detailed_match.group(1).strip()
            if flag_match:
                flag_value = flag_match.group(1).strip().lower()
                parsed_response["invoke_another_agent_flag"] = flag_value == "true"
            if agent_match:
                parsed_response["invoke_agent_name"] = agent_match.group(1).strip()
            
            print('\nPARSED RESPONSE:', parsed_response)
            
            return parsed_response
            
        except Exception as e:
            self.logger.error(f"Error parsing response: {e}")
            return {
                "response_to_user": "I apologize, but I encountered an error processing the response.",
                "detailed_response": str(e),
                "invoke_another_agent_flag": False,
                "invoke_agent_name": ""
            }
    '''

    def _load_conversation_history(self):
        """Load conversation history from gzipped JSON file"""
        self.conversation_history = []
        try:
            # Check if history file exists
            if os.path.exists(self.history_file):
                print(f"DEBUG: Loading conversation history from {self.history_file}")
                with gzip.open(self.history_file, 'rt', encoding='utf-8') as f:
                    self.conversation_history = json.load(f)
                self.logger.info(f"Loaded {len(self.conversation_history)} messages from conversation history")
        except Exception as e:
            self.logger.error(f"Error loading conversation history: {e}")
            # Initialize with empty history
            self.conversation_history = []
    
    def _save_conversation_history(self):
        """Save conversation history to gzipped JSON file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            
            # Write to a temporary file first (atomic operation)
            with tempfile.NamedTemporaryFile(delete=False, mode='wt', encoding='utf-8') as f:
                json.dump(self.conversation_history, f, indent=2, ensure_ascii=False)
                temp_filename = f.name
            
            # Compress the temporary file and move it to the target location
            with open(temp_filename, 'rt', encoding='utf-8') as f_in:
                with gzip.open(self.history_file, 'wt', encoding='utf-8') as f_out:
                    f_out.write(f_in.read())
            
            # Remove the temporary file
            os.unlink(temp_filename)
            
        except Exception as e:
            self.logger.error(f"Error saving conversation history: {e}")
