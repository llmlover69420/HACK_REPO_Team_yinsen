from aipolabs import ACI
from dotenv import load_dotenv
import os
import openai
import json
# Initialize the ACI client
load_dotenv()
aci = ACI()

LINKED_ACCOUNT_OWNER_ID = os.getenv("LINKED_ACCOUNT_OWNER_ID", "")
if not LINKED_ACCOUNT_OWNER_ID:
    raise ValueError("LINKED_ACCOUNT_OWNER_ID is not set")

    
# Get the function definition
function_definition = aci.functions.get_definition("GOOGLE_CALENDAR__CALENDARLIST_GET")

# Print the function definition
print(function_definition)

response = openai.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant with access to a variety of tools."},
        {"role": "user", "content": "What is aipolabs ACI?"}
    ],
    tools=[function_definition],
    tool_choice="required"
)

print(response)

tool_call = (
    response.choices[0].message.tool_calls[0]
    if response.choices[0].message.tool_calls
    else None
)

result = aci.functions.execute(
    tool_call.function.name,
    json.loads(tool_call.function.arguments),
    linked_account_owner_id=LINKED_ACCOUNT_OWNER_ID
)
print(f"function call result: {result}")