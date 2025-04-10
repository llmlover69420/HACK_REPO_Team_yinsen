'''
This file contains the parsers for the response from different LLM agents.

'''

from typing import Dict, Any

# parser for main LLM agent response
def parse_main_llm_response(response: str) -> Dict[str, Any]:
    '''
    Parse the response from the main LLM agent.
    '''

    # parse the response from the manager agent
    return
    return parsed_response

# String to Dictionary Conversion Function
def convert_to_boolean(value: str):
    print(f"DEBUG: Converting to boolean: {value}")
    print(value.lower())
    value = value.strip()
    if value.lower() == 'true':
        return True
    elif value.lower() == 'false':
        return False
    else:
        return None
def convert_string_to_dict(response_string: str) -> dict:
    """
    Convert a structured response string to a dictionary.
    
    Example input:
    [detailed_response]: Hello, Boss! How can I assist you today?  
    [summarized_response]: Hello, Boss! How can I assist you today?  
    [ask_for_agent_switch_confirmation_flag]: False  
    [invoke_another_agent_flag]: False  
    [invoke_agent_name]:  
    
    Returns:
        dict: A dictionary with keys extracted from brackets and corresponding values
    """
    if not response_string:
        return {}
    
    result = {}
    
    # Find all [key]: value patterns in the string using regex
    import re
    pattern = r'\[(.*?)\]:\s*(.*?)(?=\[\w+\]:|$)'
    matches = re.findall(pattern, response_string, re.DOTALL)
    
    for key, value in matches:
        # Clean up the value (remove extra whitespace)
        value = value.strip()
        
        # Convert boolean strings to actual boolean values
        if value.lower() == 'true':
            value = True
        elif value.lower() == 'false':
            value = False
        elif value == '':
            value = None
            
        # Add to the result dictionary
        result[key] = value
    
    return result

def convert_tool_response_json_string_to_dict(json_string: str) -> dict:
    """
    Convert a JSON-formatted string to a Python dictionary.
    
    Args:
        json_string (str): A string containing valid JSON
        
    Returns:
        dict: The parsed dictionary from the JSON string
        
    Raises:
        ValueError: If the input string is not valid JSON
    """
    if not json_string:
        return {}
    
    try:
        import json
        dict_result = json.loads(json_string)
        print(f"DEBUG: Dict result: {dict_result}")
        #for key in dict_result['instructions'].keys():
        #    if dict_result['instructions'][key].lower() == 'true':
        #        dict_result['instructions'][key] = True
        #    elif dict_result['instructions'][key].lower() == 'false':
        #        dict_result['instructions'][key] = False
        return dict_result
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON string: {e}")

# Google Calendar Event Parser Function
def parse_google_calendar_event(event_dict: dict) -> dict:
    """
    Parse a single Google Calendar event dictionary into a more structured format.
    
    Args:
        event_dict (dict): Dictionary containing a Google Calendar event
        
    Returns:
        dict: A dictionary with extracted and formatted event information
    """
    if not event_dict:
        return {}
    
    # Extract datetime helpers
    def _extract_datetime(time_data: dict) -> str:
        """Extract datetime from event time data"""
        if 'dateTime' in time_data:
            return time_data['dateTime']
        elif 'date' in time_data:  # For all-day events
            return time_data['date']
        return ''
    
    def _extract_timezone(time_data: dict) -> str:
        """Extract timezone from event time data"""
        return time_data.get('timeZone', '')

    def format_iso_datetime(iso_datetime_str: str, output_format: str = "d/m/Y h:M A") -> str:
        """
        Parse an ISO 8601 datetime string into a custom format.
        
        Args:
            iso_datetime_str (str): Datetime string in ISO 8601 format (e.g., "2025-04-04T19:00:00+01:00")
            output_format (str): Output format (default: "d/m/Y h:M A" for dd/mm/yyyy hh:mm AM/PM)
            
        Returns:
            str: The formatted datetime string
            
        Examples:
            >>> format_iso_datetime("2025-04-04T19:00:00+01:00")
            "4/4/2025 7:00 PM"
            
            >>> format_iso_datetime("2025-04-04T09:30:00+01:00")
            "4/4/2025 9:30 AM"
        """
        from datetime import datetime
        
        # Parse the ISO datetime string
        try:
            # Use fromisoformat for Python 3.7+
            dt = datetime.fromisoformat(iso_datetime_str.replace('Z', '+00:00'))
        except ValueError:
            # Fallback for older Python versions or unusual formats
            import dateutil.parser
            dt = dateutil.parser.parse(iso_datetime_str)
        
        # Define the format mappings
        format_mapping = {
            'd': '%-d',    # Day of the month without leading zeros
            'm': '%-m',    # Month without leading zeros
            'Y': '%Y',     # 4-digit year
            'h': '%-I',    # Hour (12-hour clock) without leading zeros
            'H': '%-H',    # Hour (24-hour clock) without leading zeros
            'M': '%M',     # Minute with leading zeros
            'S': '%S',     # Second with leading zeros
            'A': '%p',     # AM/PM
        }
        
        # Apply format mappings
        python_format = output_format
        for key, val in format_mapping.items():
            python_format = python_format.replace(key, val)
        
        # Format the datetime
        return dt.strftime(python_format)
    
    # Parse the event data
    try:
        event = {
            'event_id': event_dict.get('id', ''),
            'summary': event_dict.get('summary', ''),
            'description': event_dict.get('description', ''),
            'status': event_dict.get('status', ''),
            'created': event_dict.get('created', ''),
            'updated': event_dict.get('updated', ''),
            'creator': event_dict.get('creator', {}).get('email', ''),
            'organizer': event_dict.get('organizer', {}).get('email', ''),
            'start_time': format_iso_datetime(_extract_datetime(event_dict.get('start', {}))),
            'end_time': format_iso_datetime(_extract_datetime(event_dict.get('end', {}))),
            'timezone': _extract_timezone(event_dict.get('start', {})),
            'html_link': event_dict.get('htmlLink', ''),
            'ical_uid': event_dict.get('iCalUID', ''),
            'sequence': event_dict.get('sequence', 0),
            'is_all_day': 'date' in event_dict.get('start', {}) and 'date' in event_dict.get('end', {}),
            'reminders': event_dict.get('reminders', {}).get('useDefault', False)
        }
        
        # Add attendees information if available
        if 'attendees' in event_dict:
            event['attendees'] = [
                {
                    'email': attendee.get('email', ''),
                    'name': attendee.get('displayName', ''),
                    'response_status': attendee.get('responseStatus', ''),
                    'is_organizer': attendee.get('organizer', False),
                    'is_self': attendee.get('self', False)
                }
                for attendee in event_dict['attendees']
            ]
        else:
            event['attendees'] = []
            
        return event
        
    except Exception as e:
        raise ValueError(f"Error parsing calendar event: {e}")