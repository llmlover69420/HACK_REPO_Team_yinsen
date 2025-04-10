import json
import os

from aipolabs import ACI
from aipolabs.types.functions import FunctionDefinitionFormat
from dotenv import load_dotenv
from openai import OpenAI
from rich import print as rprint
from rich.panel import Panel

load_dotenv()
LINKED_ACCOUNT_OWNER_ID = os.getenv("LINKED_ACCOUNT_OWNER_ID", "")
if not LINKED_ACCOUNT_OWNER_ID:
    raise ValueError("LINKED_ACCOUNT_OWNER_ID is not set")

# gets OPENAI_API_KEY from your environment variables
openai = OpenAI()
# gets AIPOLABS_ACI_API_KEY from your environment variables
aci = ACI()


def main() -> None:
    # For a list of all supported apps and functions, please go to the platform.aci.dev
    function_definition = aci.functions.get_definition(
        "GOOGLE_CALENDAR__EVENTS_LIST"
    )

    #rprint(Panel("Google calendar function definition", style="bold blue"))
    #rprint(function_definition)

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant with access to a variety of tools.",
            },
            {
                "role": "user",
                "content": "get my events for 04/04/2025",
            },
        ],
        tools=[function_definition],
        tool_choice="required",  # force the model to generate a tool call for demo purposes
    )
    tool_call = (
        response.choices[0].message.tool_calls[0]
        if response.choices[0].message.tool_calls
        else None
    )

    result = aci.functions.execute(
        "GOOGLE_CALENDAR__EVENTS_LIST",
        json.loads(tool_call.function.arguments),
        linked_account_owner_id=LINKED_ACCOUNT_OWNER_ID,
        )

    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from core_engines.utils.parsers import parse_google_calendar_event

    for x in result:
        if x[0] == 'data':
            data = x[1]
            for key in data.keys():
                #print(f"{key}: {data[key]}")
                if key == 'items':
                    for x in data[key]:
                        event = parse_google_calendar_event(x)
                        event_summary = {
                            'summary': event['summary'],
                            'start_time': event['start_time'],
                            'end_time': event['end_time'],
                            'creator': event['creator']
                        }
                        print(event_summary)
                        print("---")
            break
        
if __name__ == "__main__":
    main()