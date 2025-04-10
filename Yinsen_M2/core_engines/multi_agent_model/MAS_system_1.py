from core_engines.agents.llm_agent import LLMAgent
from core_engines.utils.parsers import convert_string_to_dict, convert_tool_response_json_string_to_dict

#from core_engines.utils.parsers import convert_to_boolean
from core_engines.utils.utils import _dict_to_string
from external_tools.toolbox import Toolbox

from typing import Dict, Any
import base64
import os

class MAS_system_1(object):
    def __init__(self,
                 config,
                 logger,
                 text_output) -> None:
        '''
        Initialize the MAS system 1.
        '''

        # init logger
        self.logger = logger

        # init config
        self.config = config    

        # init text output
        self.text_output = text_output

        # get agent type to name mapping
        self.agent_type_to_name_map = _dict_to_string(self._get_agent_type_to_name_map())
        #print(f"DEBUG: Agent type to name mapping: {_dict_to_string(self.agent_type_to_name_map)}")
    
        # init agents
        self._init_agents()

        # init toolbox
        self.toolbox = Toolbox(config=self.config)

        # set current agent
        self.current_agent = self.orchestrator_agent

    def _init_agents(self):
        """Initialize all LLM agents"""
        # Main agents ----------------------------------------------------------------------------------------
        # Create orchestrator agent
        self.orchestrator_agent = LLMAgent(
            agent_name=self.config['agent']['orchestrator']['name'],
            config=self.config['agent'],
            agent_type="orchestrator",
            agent_category="main",
            agent_type_to_name_map=self.agent_type_to_name_map
        )
        self.logger.info(f"Orchestrator agent '{self.orchestrator_agent.agent_name}' initialized")
        #print(f"Orchestrator agent '{self.orchestrator_agent.agent_name}' initialized")

        # Create finance manager agent
        self.finance_manager_agent = LLMAgent(
            agent_name=self.config['agent']['finance_manager']['name'],
            config=self.config['agent'],
            agent_type="finance_manager",
            agent_category="main",
            agent_type_to_name_map=self.agent_type_to_name_map
        )
        self.logger.info(f"Finance manager agent '{self.finance_manager_agent.agent_name}' initialized")
        #print(f"Finance manager agent '{self.finance_manager_agent.agent_name}' initialized")

        # Create study manager agent
        self.study_manager_agent = LLMAgent(
            agent_name=self.config['agent']['study_manager']['name'],
            config=self.config['agent'],
            agent_type="study_manager",
            agent_category="main",
            agent_type_to_name_map=self.agent_type_to_name_map
        )
        self.logger.info(f"Study manager agent '{self.study_manager_agent.agent_name}' initialized")
        #print(f"Study manager agent '{self.study_manager_agent.agent_name}' initialized")

        # Create health manager agent
        self.health_manager_agent = LLMAgent(
            agent_name=self.config['agent']['health_manager']['name'],
            config=self.config['agent'],
            agent_type="health_manager",
            agent_category="main",
            agent_type_to_name_map=self.agent_type_to_name_map
        )
        self.logger.info(f"Health manager agent '{self.health_manager_agent.agent_name}' initialized")
        #print(f"Health manager agent '{self.health_manager_agent.agent_name}' initialized")

        # Helper agents -------------------------------------------------------------------------------------
        self.visualizer_agent = LLMAgent(
            agent_name=self.config['agent']['helper_agents']['visualizer_agent']['name'],
            config=self.config['agent']['helper_agents'],
            agent_type="visualizer_agent",
            agent_category="helper",
            agent_type_to_name_map=self.agent_type_to_name_map
        )
        self.logger.info(f"Visualizer agent '{self.visualizer_agent.agent_name}' initialized")
        #print(f"Visualizer agent '{self.visualizer_agent.agent_name}' initialized")

        self.tool_handler_agent = LLMAgent(
            agent_name=self.config['agent']['helper_agents']['tool_handler_agent']['name'],
            config=self.config['agent']['helper_agents'],
            agent_type="tool_handler_agent",
            agent_category="helper",
            agent_type_to_name_map=self.agent_type_to_name_map
        )
        self.logger.info(f"Tool handler agent '{self.tool_handler_agent.agent_name}' initialized")
        #print(f"Tool handler agent '{self.tool_handler_agent.agent_name}' initialized")

        self.visualizer_agent = LLMAgent(
            agent_name=self.config['agent']['helper_agents']['visualizer_agent']['name'],
            config=self.config['agent']['helper_agents'],
            agent_type="visualizer_agent",
            agent_category="helper",
            agent_type_to_name_map=self.agent_type_to_name_map
        )
        self.logger.info(f"Visualizer agent '{self.visualizer_agent.agent_name}' initialized")
        #print(f"Visualizer agent '{self.visualizer_agent.agent_name}' initialized")

    def _get_agent_type_to_name_map(self):
        """Get the agent type to name mapping"""
        agent_type_to_name_map = {}
        for agent_type, agent_data in self.config['agent'].items():
            if isinstance(agent_data, dict) and 'name' in agent_data:
                agent_type_to_name_map[agent_type] = agent_data['name']
        return agent_type_to_name_map

    def get_current_agent(self) -> LLMAgent:
        '''
        Get the current agent.
        '''
        return self.current_agent    
    
    def _switch_agent(self, agent_name: str):
        """Switch to a different agent"""
        # Remove quotes from the beginning and end of the string if they exist
        if isinstance(agent_name, str):
            agent_name = agent_name.strip()
            if (agent_name.startswith('"') and agent_name.endswith('"')) or \
               (agent_name.startswith("'") and agent_name.endswith("'")):
                agent_name = agent_name[1:-1]

        if ((agent_name.lower() == "orchestrator") or (agent_name.lower() == self.orchestrator_agent.agent_name.lower()) and self.current_agent != self.orchestrator_agent):
            self.current_agent = self.orchestrator_agent
            print(f"\n===== SWITCHING TO ORCHESTRATOR AGENT: {self.orchestrator_agent.agent_name} =====\n")
            #self.text_output.display(f"Switching to {self.orchestrator_agent.agent_name}")
            return True
        
        elif ((agent_name.lower() == "finance_manager") or \
              (agent_name.lower() == "finance manager") or \
              (agent_name.lower() == "finance agent") or \
              (agent_name.lower() == "finance") or \
              ((agent_name.lower() == self.finance_manager_agent.agent_name.lower()) and (self.current_agent != self.finance_manager_agent))):
            self.current_agent = self.finance_manager_agent
            print(f"\n===== SWITCHING TO FINANCE MANAGER AGENT: {self.finance_manager_agent.agent_name} =====\n")
            #self.text_output.display(f"Switching to {self.finance_manager_agent.agent_name}")
            return True

        elif ((agent_name.lower() == "study_manager") or \
              (agent_name.lower() == "study manager") or \
              (agent_name.lower() == "study agent") or \
              (agent_name.lower() == "study") or \
              ((agent_name.lower() == self.study_manager_agent.agent_name.lower()) and self.current_agent != self.study_manager_agent)):
            self.current_agent = self.study_manager_agent
            print(f"\n===== SWITCHING TO STUDY MANAGER AGENT: {self.study_manager_agent.agent_name} =====\n")
            #self.text_output.display(f"Switching to {self.study_manager_agent.agent_name}")
            return True

        elif ((agent_name.lower() == "health_manager") or \
              (agent_name.lower() == "health manager") or \
              (agent_name.lower() == "health agent") or \
              (agent_name.lower() == "health") or \
              ((agent_name.lower() == self.health_manager_agent.agent_name.lower()) and self.current_agent != self.health_manager_agent)):
            self.current_agent = self.health_manager_agent
            print(f"\n===== SWITCHING TO HEALTH MANAGER AGENT: {self.health_manager_agent.agent_name} =====\n")
            #self.text_output.display(f"Switching to {self.health_manager_agent.agent_name}")
            return True

        else:
            self.logger.warning(f"Unknown agent name: {agent_name}, staying with current agent")
            return False
    
    def get_response_from_mas_system(self,
                                    user_input: str,
                                    main_llm_agent: LLMAgent,
                                    response_format: str
                                    ) -> Dict[str, Any]:
        '''
        Get the response from the MAS model 1.
        Here we define the flow of the MAS system.
        '''
        return_response = {
            "final_response_to_user": "",
            "summarized_response": "",
            "current_agent_name": "",
            "current_agent_type": "",
            "logs_updated": False,
            "calendar_updated": False,
            "youtube_urls": [],
            "display_images": []
        }

        # 1. get response from main LLM agent : simple+detailed response -----------------------------------
        main_agent_response_dict = main_llm_agent.generate_response(user_input)
        #print(f"DEBUG: Raw response: {main_agent_response_dict}")
        # convert string to dict
        main_agent_response_dict = convert_string_to_dict(main_agent_response_dict)
        print(f"\nResponse dict: {main_agent_response_dict}")
        
        # now we have a dictionary with the following keys:
        # a. simple response
        # b. detailed response
        # c. tool use response
        # d. invoke another agent flag
        # e. invoke agent name

        # Check if we need to switch agents -------------------------------------------------------------
        if main_agent_response_dict.get("invoke_another_agent_flag", False) and main_agent_response_dict.get("invoke_agent_name", False):
            switch_status = self._switch_agent(main_agent_response_dict["invoke_agent_name"])

        # 2. if using tool, use tool and get response from tool handler agent ----------------------------------------
        else:
            if main_agent_response_dict.get("tool_usage_flag"):
                
                tool_usage_instructions = main_agent_response_dict["tool_usage_response"]
                
                #current_datetime = get_formatted_datetime()
                tool_usage_instructions = f"main_agent_response: {tool_usage_instructions}"#. current_datetime: {current_datetime}"
                print(f"\nTool usage instructions: {tool_usage_instructions}")
                
                tool_response_dict = self.tool_handler_agent.generate_response(tool_usage_instructions)
                print(f"DEBUG: Tool response: {tool_response_dict}")
                tool_response_dict = convert_tool_response_json_string_to_dict(tool_response_dict)
                #print(f"Tool response dict: {tool_response_dict}")

                if "error" in tool_response_dict.keys():
                    # TODO: handle error
                    print(f"Tool error: {tool_response_dict['error']}")
                    print(f"Tool details: {tool_response_dict['details']}")
                    tool_execution_result = {'status': 'error', 'error': tool_response_dict['error'], 'details': tool_response_dict['details']}
                    # TODO: update the response dict with the tool error
                    #response_dict["detailed_response"] = tool_response_dict["details"]
                    #response_dict["summarized_response"] = tool_response_dict["error"]
                else:
                    # TODO: execute the tool with the tool response dict
                    #print(f"Tool response: {tool_response_dict}")
                    
                    # Execute the tool
                    #tool_execution_response_dict = {'status': 'success'}                
                    tool_execution_result = self.toolbox.execute_tool(tool_response_dict)
                    print(f"DEBUG: Tool execution result: {tool_execution_result}")
        # 3. get response from visualizer agent ---------------------------------------------------------
        # if no tool is used, return the detailed response
        if not main_agent_response_dict["tool_usage_flag"]:
            # if not switching agent, just return the detailed response
            if not main_agent_response_dict.get("invoke_another_agent_flag"):
                overall_response_dict = f'[main_agent_response]: {main_agent_response_dict["detailed_response"]}'
            # if switching agent, return the detailed response, switch flag, and switch name
            else:
                overall_response_dict = f'[main_agent_response]: {main_agent_response_dict["detailed_response"]}\n \
                                          [switch_agent_flag]: {main_agent_response_dict["invoke_another_agent_flag"]}\n \
                                          [switch_agent_name]: {main_agent_response_dict["invoke_agent_name"]}\n \
                                          [switch_status]: {switch_status}'
        
        # if tool is used, return the detailed response, tool usage flag, tool usage response, tool instruction from tool agent, and tool execution result
        elif main_agent_response_dict["tool_usage_flag"]:
            # handle tool error case - later
            
            if type(tool_execution_result) == dict:
                #extract image path
                if 'image_path' in tool_execution_result.keys():
                    for img_path in tool_execution_result['image_path']:
                        if os.path.exists(img_path):
                            print(f'DEBUG: Image path: {img_path}')
                            with open(img_path, 'rb') as image_file:
                                image = base64.b64encode(image_file.read()).decode('utf-8')
                                return_response['display_images'].append(image)

                # remove image_path from dict
                tool_execution_result.pop('image_path', None)

                tool_execution_result_str = _dict_to_string(tool_execution_result)
            else:
                tool_execution_result_str = tool_execution_result

            overall_response_dict = f'[main_agent_response]: {main_agent_response_dict["detailed_response"]}\n \
                                      [tool_usage]: {main_agent_response_dict["tool_usage_flag"]}\n \
                                      [tool_input_from_main_agent]: {main_agent_response_dict["tool_usage_response"]}\n \
                                      [tool_instruction_from_tool_agent]: {str(tool_response_dict)}\n \
                                      [tool_execution_result]: {tool_execution_result_str}'
        

        # 4. add response format to the overall response dict
        overall_response_dict = overall_response_dict + f"\n [response_format]: {response_format}"

        #print(f"DEBUG: Overall response dict: {overall_response_dict}")

        visualizer_response = self.visualizer_agent.generate_response(overall_response_dict)

        #print(f"DEBUG: Visualizer response: {visualizer_response}")

        visualizer_response_dict = convert_string_to_dict(visualizer_response)
        
        #print(f"DEBUG: Visualizer response: {visualizer_response_dict}")

        # Format the visualizer response

        return_response['final_response_to_user'] = visualizer_response_dict["final_response_to_user"]
        return_response['summarized_response'] = visualizer_response_dict["summarized_response"]
        return_response['current_agent_name'] = self.current_agent.agent_name
        return_response['current_agent_type'] = self.current_agent.agent_type

        #print(f"DEBUG: Return response: {return_response}")

        return return_response, self.current_agent
    
