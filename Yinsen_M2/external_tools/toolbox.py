from aipolabs import ACI
from aipolabs.types.functions import FunctionDefinitionFormat
from openai import OpenAI
import os
import json
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.io as pio
from external_tools.utils import update_calender_logs, update_notification_logs
from core_engines.utils.utils import get_formatted_datetime

class Toolbox:
    def __init__(self, config):
        self.aci = ACI()
        self.openai = OpenAI()

        self.LINKED_ACCOUNT_OWNER_ID = os.getenv("LINKED_ACCOUNT_OWNER_ID", "")

        self.calender_logs_path = config['calender_and_logs']['calender_logs_path']
        self.notification_logs_path = config['calender_and_logs']['notification_logs_path']

    def execute_tool(self, tool_response_dict: dict) -> dict:
        
        if tool_response_dict["tool"] == "calendar":
            if tool_response_dict['instructions']["action"] == "create":
                # use calender api to create a new event
                function_definition = self.aci.functions.get_definition("GOOGLE_CALENDAR__EVENTS_INSERT")
                response = self.openai.chat.completions.create(model="o3-mini",
                                                               messages=[
                                                                    {
                                                                        "role": "system",
                                                                        "content": "You are a helpful assistant that can use the calender tool to create a new event. \
                                                                            You will be given a set of instructions on what to create, in the form of a JSON like this: \
                                                                                { \
                                                                            'action': 'create', \
                                                                            'start_time': '05/04/2025 15:00', \
                                                                            'end_time': '05/04/2025 16:00', \
                                                                            'description': 'OpenAI API payment' \
                                                                                }. \
                                                                            Use this information to create an event in your calendar. \
                                                                            Follow the function definition and the tool call format to create the event. \
                                                                            The provided date format is DD/MM/YYYY HH:MM. \
                                                                            The event should be created in the user's primary calendar. \
                                                                            The user's primary calendar is the one with the highest priority.\
                                                                            Also, infer the title of the event based on the description."
                                                                    },
                                                                    {
                                                                        "role": "user",
                                                                        "content": f"use the calender tool to schedule an event using the following information: {tool_response_dict['instructions']}",
                                                                    },
                                                                ],
                                                                tools=[function_definition],
                                                                tool_choice="required",  # force the model to generate a tool call for demo purposes
                                                                )
                #print(f"DEBUG: Response inside toolbox.py: {response}")
                tool_call = (
                    response.choices[0].message.tool_calls[0]
                    if response.choices[0].message.tool_calls
                    else None
                )
                print(f"DEBUG: Tool call inside toolbox.py: {tool_call}")
                result = self.aci.functions.execute(
                    "GOOGLE_CALENDAR__EVENTS_INSERT",
                    json.loads(tool_call.function.arguments),
                    linked_account_owner_id=self.LINKED_ACCOUNT_OWNER_ID,
                )
                #print(f"DEBUG: Tool execution result inside toolbox.py: {result}")
                #print(result.success, result.data['summary'], tool_response_dict['instructions']['start_time'])
                
                # Update calender logs if the event is created successfully for TODAY
                if result.success:
                    if get_formatted_datetime(date_only=True) == tool_response_dict['instructions']['start_time'].split(' ')[0]:
                        update_calender_logs(tool_response_dict['instructions']['start_time'].split(' ')[1], \
                                             result.data['summary'], \
                                             self.calender_logs_path
                                            )
                        #Update notification logs if the event is created successfully for TODAY
                        update_notification_logs('<b>+ Event created successfully!</b>', \
                                                 self.notification_logs_path
                                                )
                
                return result

            elif tool_response_dict['instructions']["action"] == "view":
                function_definition = self.aci.functions.get_definition("GOOGLE_CALENDAR__EVENTS_LIST")
                response = self.openai.chat.completions.create(model="o3-mini",
                                                               messages=[
                                                                    {
                                                                        "role": "system",
                                                                        "content": "You are a helpful assistant that can use the calender tool to fetch events from the user's calendar. \
                                                                            You will be given a date, for which you need to fetch the events, in the form of a JSON like this: \
                                                                                { \
                                                                                'action': 'view', \
                                                                                'date': '05/04/2025', \
                                                                                }. \
                                                                            Use this information to fetch events from the user's calendar. \
                                                                            Follow the function definition and the tool call format to fetch the events. \
                                                                            The provided date format is DD/MM/YYYY. \
                                                                            The event should be fetched from the user's primary calendar. \
                                                                            The user's primary calendar is the one with the highest priority."                                                                    
                                                                    },
                                                                    {
                                                                        "role": "user",
                                                                        "content": f"use the calender tool to fetch events from the user's calendar using the following information: {tool_response_dict['instructions']}",
                                                                    },
                                                                ],
                                                                tools=[function_definition],
                                                                tool_choice="required",  # force the model to generate a tool call for demo purposes
                                                                )
                #print(f"DEBUG: Response inside toolbox.py: {response}")
                tool_call = (
                    response.choices[0].message.tool_calls[0]
                    if response.choices[0].message.tool_calls
                    else None
                )
                print(f"DEBUG: Tool call inside toolbox.py: {tool_call}")
                result = self.aci.functions.execute(
                    "GOOGLE_CALENDAR__EVENTS_LIST",
                    json.loads(tool_call.function.arguments),
                    linked_account_owner_id=self.LINKED_ACCOUNT_OWNER_ID,
                )
                #print(f"DEBUG: Tool execution result inside toolbox.py: {result}")
                return result
        
        elif tool_response_dict["tool"] == "email":

            if tool_response_dict['instructions']["action"] == "send":

                # use email api to send an email
                function_definition = self.aci.functions.get_definition("GMAIL__SEND_EMAIL")
                response = self.openai.chat.completions.create(model="o3-mini",
                                                               messages=[
                                                                    {
                                                                        "role": "system",
                                                                        "content": "You are a helpful assistant that can use gmail send email function to send an email on behalf of the user. \
                                                                            You will be given a set of instructions on how to create the email, in the form of a JSON like this: \
                                                                                { \
                                                                            'action': 'send', \
                                                                            'to': 'yash@gmail.com', \
                                                                            'from': 'dipayan@gmail.com', \
                                                                            'subject': 'Event Confirmation', \
                                                                            'content': 'Dear Yash,\n\nI hope this message finds you well. I wanted to confirm that I will see you at the event today. Looking forward to it!\n\nBest regards,\nDas' \
                                                                                }. \
                                                                            Use this information to send an email on behalf of the user. \
                                                                            Follow the function definition and the tool call format to send the email. \
                                                                            Any provided date and time format is DD/MM/YYYY and HH:MM."
                                                                    },
                                                                    {
                                                                        "role": "user",
                                                                        "content": f"use the email tool to send an email using the following information: {tool_response_dict['instructions']}",
                                                                    },
                                                                ],
                                                                tools=[function_definition],
                                                                tool_choice="required",  # force the model to generate a tool call for demo purposes
                                                                )
                #print(f"DEBUG: Response inside toolbox.py: {response}")
                tool_call = (
                    response.choices[0].message.tool_calls[0]
                    if response.choices[0].message.tool_calls
                    else None
                )
                print(f"DEBUG: Tool call inside toolbox.py: {tool_call}")
                result = self.aci.functions.execute(
                    "GMAIL__SEND_EMAIL",
                    json.loads(tool_call.function.arguments),
                    linked_account_owner_id=self.LINKED_ACCOUNT_OWNER_ID,
                )
                print(f"DEBUG: Tool execution result inside toolbox.py: {result}")
                
                #Update notification logs if the email is sent successfully for TODAY
                if result.success:
                    update_notification_logs('<b>+ Email sent successfully!</b>', \
                                             self.notification_logs_path
                                            )
                
                return result
            '''
            elif tool_response_dict['instructions']["action"] == "read":
                # use email api to read emails
                # 1. retrieve list of emails - in the form of IDs
                function_definition = self.aci.functions.get_definition("GMAIL__MESSAGES_LIST")
                print(f"DEBUG: Email view i inside toolbox.py: {tool_response_dict['instructions']}")
                response = self.openai.chat.completions.create(model="o3-mini",
                                                               messages=[
                                                                    {
                                                                        "role": "system",
                                                                        "content": "You are a helpful assistant that can use gmail message list function to view emails on behalf of the user. \
                                                                            You will be given a set of instructions regarding how to view the emails, in the form of a JSON. \
                                                                            The JSON can either be like:\
                                                                                { \
                                                                            'action': 'read', \
                                                                            'until_date': '29/03/2025' \
                                                                                }. \
                                                                            or like:\
                                                                                { \
                                                                            'action': 'read', \
                                                                            'last_n_emails': 10 \
                                                                                }. \
                                                                            Use this information to view the emails. \
                                                                            Follow the function definition and the tool call format to view the emails. \
                                                                            Any provided date format is DD/MM/YYYY."
                                                                    },
                                                                    {
                                                                        "role": "user",
                                                                        "content": f"use the email tool to view emails using the following information: {tool_response_dict['instructions']}",
                                                                    },
                                                                ],
                                                                tools=[function_definition],
                                                                tool_choice="required",  # force the model to generate a tool call for demo purposes
                                                                )
                #print(f"DEBUG: Response inside toolbox.py: {response}")
                tool_call = (
                    response.choices[0].message.tool_calls[0]
                    if response.choices[0].message.tool_calls
                    else None
                )
                print(f"DEBUG: Tool call inside toolbox.py: {tool_call}")
                result = self.aci.functions.execute(
                    "GMAIL__MESSAGES_LIST",
                    json.loads(tool_call.function.arguments),
                    linked_account_owner_id=self.LINKED_ACCOUNT_OWNER_ID,
                )
                print(f"DEBUG: Tool execution result inside toolbox.py: {result}")

                # here we get a list of email IDs like the following:

                #DEBUG: Tool execution result inside toolbox.py: success=True data={'messages': [{'id': '1960dfae71df3aa5', 'threadId': '1960dfae71df3aa5'}, {'id': '1960ddb5bf95d60e', 'threadId': '1960ddb5bf95d60e'}, {'id': '1960dcb8b8996882', 'threadId': '1960dcb8b8996882'}, {'id': '1960da14f79ddfbf', 'threadId': '1960da14f79ddfbf'}, {'id': '1960cc30a2a03694', 'threadId': '1960cc238ce2fa68'}, {'id': '1960cc238ce2fa68', 'threadId': '1960cc238ce2fa68'}, {'id': '19603f4130e0009c', 'threadId': '19603f4130e0009c'}, {'id': '19601a8d15b3ec9b', 'threadId': '19601a8d15b3ec9b'}, {'id': '196006191c98762f', 'threadId': '196006191c98762f'}, {'id': '195fc314e169ae21', 'threadId': '195fc314e169ae21'}], 'nextPageToken': '12565313761980251534', 'resultSizeEstimate': 201} error=None
            
                # 2. retrieve the email content
                function_definition = self.aci.functions.get_definition("GMAIL__MESSAGES_GET")
                response = self.openai.chat.completions.create(model="o3-mini",
                                                               messages=[
                                                                    {
                                                                        "role": "system",
                                                                        "content": "You are a helpful assistant that can use gmail message get function to view emails' content on behalf of the user. \
                                                                            You will be given a set of id and threadId of the emails, in the form of a JSON like the following: \
                                                                                {'messages': [{'id': '1960dfae71df3aa5', 'threadId': '1960dfae71df3aa5'}, {'id': '1960ddb5bf95d60e', 'threadId': '1960ddb5bf95d60e'}, {'id': '1960dcb8b8996882', 'threadId': '1960dcb8b8996882'}, {'id': '1960da14f79ddfbf', 'threadId': '1960da14f79ddfbf'}, {'id': '1960cc30a2a03694', 'threadId': '1960cc238ce2fa68'}, {'id': '1960cc238ce2fa68', 'threadId': '1960cc238ce2fa68'}, {'id': '19603f4130e0009c', 'threadId': '19603f4130e0009c'}, {'id': '19601a8d15b3ec9b', 'threadId': '19601a8d15b3ec9b'}, {'id': '196006191c98762f', 'threadId': '196006191c98762f'}, {'id': '195fc314e169ae21', 'threadId': '195fc314e169ae21'}], 'nextPageToken': '12565313761980251534', 'resultSizeEstimate': 201}\
                                                                            Use this information to view the content of the all the emails in the list. \
                                                                            Follow the function definition and the tool call format to view the emails. \
                                                                            Any provided date format is DD/MM/YYYY."
                                                                    },
                                                                    {
                                                                        "role": "user",
                                                                        "content": f"use the email tool to view the content of the emails using the following information: {result.data}",
                                                                    },
                                                                ],
                                                                tools=[function_definition],
                                                                tool_choice="required",  # force the model to generate a tool call for demo purposes
                                                                )
                #print(f"DEBUG: Response inside toolbox.py: {response}")
                tool_call = (
                    response.choices[0].message.tool_calls[0]
                    if response.choices[0].message.tool_calls
                    else None
                )
                print(f"DEBUG: Tool call inside toolbox.py: {tool_call}")
                result = self.aci.functions.execute(
                    "GMAIL__MESSAGES_GET",
                    json.loads(tool_call.function.arguments),
                    linked_account_owner_id=self.LINKED_ACCOUNT_OWNER_ID,
                )
                print(f"DEBUG: Tool execution result inside toolbox.py: {result}")



                return result
            '''

        elif tool_response_dict["tool"] == "expense_manager":
            
            if tool_response_dict['instructions']["action"] == "log_expense":
                # use expense manager tool to log an expense
                
                # check if we expense_log.csv file exists
                if not os.path.exists('./data/finance/expense_log.csv'):
                    # create the file and directory if needed
                    os.makedirs('./data/finance', exist_ok=True)
                    with open('./data/finance/expense_log.csv', 'w') as f:
                        f.write('date,amount,category,currency\n')

                # read the expense_log.csv file using pandas
                df = pd.read_csv('./data/finance/expense_log.csv')
                #print(df)
                    
                # append the new expense to the expense_log.csv file
                # create a new row as a dictionary
                new_expense = {
                    'date': datetime.strptime(tool_response_dict['instructions']['date'], '%d/%m/%Y').strftime('%d/%m/%Y'),
                    'amount': tool_response_dict['instructions']['amount'],
                    'category': tool_response_dict['instructions']['category'],
                    'currency': tool_response_dict['instructions']['currency']
                }
                
                # use concat instead of append (which is deprecated)
                df = pd.concat([df, pd.DataFrame([new_expense])], ignore_index=True)
                
                # Convert date strings to datetime objects for proper sorting
                df['date_obj'] = pd.to_datetime(df['date'], format='%d/%m/%Y')
                # sort the dataframe by date
                df = df.sort_values(by='date_obj', ascending=True)
                # Remove the temporary column used for sorting
                df = df.drop('date_obj', axis=1)
                
                df.to_csv('./data/finance/expense_log.csv', index=False)
                #print(df)

                #Update notification logs if the expense is logged successfully for TODAY
                update_notification_logs('<b>+ Expense logged successfully!</b>', \
                                             self.notification_logs_path
                                            )
                return {'status': 'success', 'message': 'Expense logged successfully'}

            elif tool_response_dict['instructions']["action"] == "view_all_expenses":
                #print(f"DEBUG: Viewing all expenses inside toolbox.py")
                # Check if expense_log.csv exists
                if not os.path.exists('./data/finance/expense_log.csv'):
                    return {'status': 'error', 'message': 'No expense log found'}
                
                # Read the expense log
                df = pd.read_csv('./data/finance/expense_log.csv')
                #print(f"DEBUG: Expense log dataframe: {df}")
                # Check if there are any expenses
                if df.empty:
                    return {'status': 'info', 'message': 'No expenses logged yet'}
                #print(f"DEBUG: Returning all expenses inside toolbox.py")
                # Return all expenses
                return {'status': 'success', 'data': df.to_dict('records')}
                
            elif tool_response_dict['instructions']["action"] == "view_last_N_expenses":
                # Check if expense_log.csv exists
                if not os.path.exists('./data/finance/expense_log.csv'):
                    return {'status': 'error', 'message': 'No expense log found'}
                
                # Read the expense log
                df = pd.read_csv('./data/finance/expense_log.csv')
                
                # Check if there are any expenses
                if df.empty:
                    return {'status': 'info', 'message': 'No expenses logged yet'}
                
                # Get the number of expenses to return
                n = int(tool_response_dict['instructions'].get('n', 5))
                
                # Convert date strings to datetime objects for proper sorting
                df['date_obj'] = pd.to_datetime(df['date'], format='%d/%m/%Y')
                # Sort by date, most recent first
                df = df.sort_values(by='date_obj', ascending=False)
                # Remove the temporary column used for sorting
                df = df.drop('date_obj', axis=1)
                
                # Get the last N expenses
                last_n_expenses = df.head(n).to_dict('records')
                
                return {'status': 'success', 'data': last_n_expenses}
                
            elif tool_response_dict['instructions']["action"] == "view_expenses_by_category":
                # Check if expense_log.csv exists
                if not os.path.exists('./data/finance/expense_log.csv'):
                    return {'status': 'error', 'message': 'No expense log found'}
                
                # Read the expense log
                df = pd.read_csv('./data/finance/expense_log.csv')
                
                # Check if there are any expenses
                if df.empty:
                    return {'status': 'info', 'message': 'No expenses logged yet'}
                
                # Get the category to filter by
                category = tool_response_dict['instructions'].get('category', '')
                
                if not category:
                    return {'status': 'error', 'message': 'No category specified for view_expenses_by_category'}
                
                # Filter expenses by category
                filtered_df = df[df['category'].str.lower() == category.lower()]
                
                if filtered_df.empty:
                    return {'status': 'info', 'message': f'No expenses found for category: {category}'}
                
                return {'status': 'success', 'data': filtered_df.to_dict('records')}
                
            elif tool_response_dict['instructions']["action"] == "view_expenses_category_wise":
                # Check if expense_log.csv exists
                if not os.path.exists('./data/finance/expense_log.csv'):
                    return {'status': 'error', 'message': 'No expense log found'}
                
                # Read the expense log
                df = pd.read_csv('./data/finance/expense_log.csv')
                
                # Check if there are any expenses
                if df.empty:
                    return {'status': 'info', 'message': 'No expenses logged yet'}
                
                # Group by category and return summary
                category_summary = df.groupby('category').agg({
                    'amount': ['sum', 'count']
                }).reset_index()
                category_summary.columns = ['category', 'total_amount', 'count']
                
                # Sort by total amount in descending order
                category_summary = category_summary.sort_values(by='total_amount', ascending=False)

                # Create interactive bar chart with plotly
                fig = px.bar(
                    category_summary, 
                    x='category', 
                    y='total_amount',
                    title='Category-wise Expenses',
                    labels={'category': 'Category', 'total_amount': 'Total Amount'},
                    color='total_amount',
                    color_continuous_scale='Viridis'
                )
                
                # Improve layout with larger text sizes
                fig.update_layout(
                    xaxis_title='Category',
                    yaxis_title='Total Amount',
                    xaxis={'categoryorder': 'total descending'},
                    margin=dict(l=20, r=20, t=40, b=20),
                    font=dict(
                        family="Arial, sans-serif",
                        size=24,  # Base font size
                        color="black"
                    ),
                    title_font=dict(size=24),  # Title font size
                    legend_font=dict(size=24)  # Legend font size
                )
                
                # Update axis title font sizes
                fig.update_xaxes(title_font=dict(size=24))
                fig.update_yaxes(title_font=dict(size=24))
                
                # Ensure directory exists
                os.makedirs('./data/finance', exist_ok=True)
                
                # Save as static image with higher resolution and dimensions
                fig.write_image('./data/finance/category_wise_expenses.png', width=2000, height=800, scale=2)

                return {'status': 'success', 'data': category_summary.to_dict('records'), 'image_path': ['./data/finance/category_wise_expenses.png']}

            elif tool_response_dict['instructions']["action"] == "view_expenses_by_date":
                # Check if expense_log.csv exists
                if not os.path.exists('./data/finance/expense_log.csv'):
                    return {'status': 'error', 'message': 'No expense log found'}
                
                # Read the expense log
                df = pd.read_csv('./data/finance/expense_log.csv')
                
                # Check if there are any expenses
                if df.empty:
                    return {'status': 'info', 'message': 'No expenses logged yet'}
                
                # Get the date to filter by
                date_str = tool_response_dict['instructions'].get('date', '')
                
                if not date_str:
                    return {'status': 'error', 'message': 'No date specified for view_expenses_by_date'}
                
                # Parse the date
                try:
                    filter_date = datetime.strptime(date_str, '%d/%m/%Y').strftime('%d/%m/%Y')
                except ValueError:
                    return {'status': 'error', 'message': 'Invalid date format. Use DD/MM/YYYY'}
                
                # Filter expenses by date
                filtered_df = df[df['date'] == filter_date]
                
                if filtered_df.empty:
                    return {'status': 'info', 'message': f'No expenses found for date: {date_str}'}
                
                return {'status': 'success', 'data': filtered_df.to_dict('records')}
                
            elif tool_response_dict['instructions']["action"] == "view_daywise_expenses":
                # Check if expense_log.csv exists
                if not os.path.exists('./data/finance/expense_log.csv'):
                    return {'status': 'error', 'message': 'No expense log found'}
                
                # Read the expense log
                df = pd.read_csv('./data/finance/expense_log.csv')
                
                # Check if there are any expenses
                if df.empty:
                    return {'status': 'info', 'message': 'No expenses logged yet'}
                
                # Group by date and return summary
                date_summary = df.groupby('date').agg({
                    'amount': ['sum', 'count']
                }).reset_index()
                date_summary.columns = ['date', 'total_amount', 'count']
                
                # Convert date strings to datetime objects for proper sorting
                date_summary['date_obj'] = pd.to_datetime(date_summary['date'], format='%d/%m/%Y')
                # Sort by date
                date_summary = date_summary.sort_values(by='date_obj', ascending=True)
                # Remove the temporary column used for sorting
                date_summary = date_summary.drop('date_obj', axis=1)
                
                # Create interactive bar chart with plotly
                fig = px.bar(
                    date_summary, 
                    x='date', 
                    y='total_amount',
                    title='Day-wise Expenses',
                    labels={'date': 'Date', 'total_amount': 'Total Amount'},
                    color='total_amount',
                    color_continuous_scale='Viridis'
                )
                
                # Improve layout with larger text sizes
                fig.update_layout(
                    xaxis_title='Date',
                    yaxis_title='Total Amount',
                    margin=dict(l=20, r=20, t=40, b=20),
                    font=dict(
                        family="Arial, sans-serif",
                        size=24,  # Base font size
                        color="black"
                    ),
                    title_font=dict(size=24),  # Title font size
                    legend_font=dict(size=24)  # Legend font size
                )
                
                # Update axis title font sizes
                fig.update_xaxes(title_font=dict(size=24))
                fig.update_yaxes(title_font=dict(size=24))
                
                # Ensure directory exists
                os.makedirs('./data/finance', exist_ok=True)
                
                # Save as static image with higher resolution and dimensions
                fig.write_image('./data/finance/daywise_expenses.png', width=2000, height=800, scale=2)
                
                return {'status': 'success', 'data': 'shown in image plot. no data in text format', 'image_path': ['./data/finance/daywise_expenses.png']}
            
            # NA for now --------------------
            elif tool_response_dict['instructions']["action"] == "view_expenses_by_week":
                # Check if expense_log.csv exists
                if not os.path.exists('./data/finance/expense_log.csv'):
                    return {'status': 'error', 'message': 'No expense log found'}
                
                # Read the expense log
                df = pd.read_csv('./data/finance/expense_log.csv')
                
                # Check if there are any expenses
                if df.empty:
                    return {'status': 'info', 'message': 'No expenses logged yet'}
                
                # Get the week to filter by (format: YYYY-WW)
                week_str = tool_response_dict['instructions'].get('week', '')
                
                if not week_str:
                    return {'status': 'error', 'message': 'No week specified for view_expenses_by_week'}
                
                try:
                    # Parse the week string (format: YYYY-WW)
                    year, week = map(int, week_str.split('-'))
                    
                    # Convert date strings to datetime objects
                    df['date_obj'] = pd.to_datetime(df['date'], format='%d/%m/%Y')
                    
                    # Extract year and week from date
                    df['year'] = df['date_obj'].dt.isocalendar().year
                    df['week'] = df['date_obj'].dt.isocalendar().week
                    
                    # Filter expenses by year and week
                    filtered_df = df[(df['year'] == year) & (df['week'] == week)]
                    
                    # Drop temporary columns
                    filtered_df = filtered_df.drop(['date_obj', 'year', 'week'], axis=1)
                    
                except (ValueError, TypeError):
                    return {'status': 'error', 'message': 'Invalid week format. Use YYYY-WW (e.g., 2023-01)'}
                
                if filtered_df.empty:
                    return {'status': 'info', 'message': f'No expenses found for week: {week_str}'}
                
                return {'status': 'success', 'data': filtered_df.to_dict('records')}
            # NA for now
            elif tool_response_dict['instructions']["action"] == "view_weekwise_expenses":
                # Check if expense_log.csv exists
                if not os.path.exists('./data/finance/expense_log.csv'):
                    return {'status': 'error', 'message': 'No expense log found'}
                
                # Read the expense log
                df = pd.read_csv('./data/finance/expense_log.csv')
                
                # Check if there are any expenses
                if df.empty:
                    return {'status': 'info', 'message': 'No expenses logged yet'}
                
                # Convert date strings to datetime objects
                df['date_obj'] = pd.to_datetime(df['date'], format='%d/%m/%Y')
                
                # Extract year and week from date
                df['year'] = df['date_obj'].dt.isocalendar().year
                df['week'] = df['date_obj'].dt.isocalendar().week
                df['year_week'] = df['year'].astype(str) + '-W' + df['week'].astype(str).str.zfill(2)
                
                # Group by year-week and return summary
                weekly_summary = df.groupby(['year_week', 'week', 'year']).agg({
                    'amount': ['sum', 'count']
                }).reset_index()
                weekly_summary.columns = ['year_week', 'week', 'year', 'total_amount', 'count']
                
                # Sort by year and week
                weekly_summary = weekly_summary.sort_values(by=['year', 'week'], ascending=[False, False])
                
                # Create interactive bar chart with plotly
                fig = px.bar(
                    weekly_summary, 
                    x='week', 
                    y='total_amount',
                    title='Week-wise Expenses',
                    labels={'week': 'Week', 'total_amount': 'Total Amount'},
                    color='total_amount',
                    color_continuous_scale='Viridis',
                    hover_data=['year_week']  # Show the year-week string on hover
                )
                
                # Improve layout with larger text sizes
                fig.update_layout(
                    xaxis_title='Week',
                    yaxis_title='Total Amount',
                    xaxis={'dtick': 1},  # Force integer ticks
                    margin=dict(l=20, r=20, t=40, b=20),
                    font=dict(
                        family="Arial, sans-serif",
                        size=24,  # Base font size
                        color="black"
                    ),
                    title_font=dict(size=24),  # Title font size
                    legend_font=dict(size=24)  # Legend font size
                )
                
                # Update axis title font sizes
                fig.update_xaxes(title_font=dict(size=24))
                fig.update_yaxes(title_font=dict(size=24))
                
                # Ensure directory exists
                os.makedirs('./data/finance', exist_ok=True)
                
                # Save as static image with higher resolution and dimensions
                fig.write_image('./data/finance/weekwise_expenses.png', width=2000, height=800, scale=2)
                
                return {'status': 'success', 'data': weekly_summary.to_dict('records'), 'image_path': ['./data/finance/weekwise_expenses.png']}
            #--------------------------------

            elif tool_response_dict['instructions']["action"] == "view_expenses_by_month":
                # Check if expense_log.csv exists
                if not os.path.exists('./data/finance/expense_log.csv'):
                    return {'status': 'error', 'message': 'No expense log found'}
                
                # Read the expense log
                df = pd.read_csv('./data/finance/expense_log.csv')
                
                # Check if there are any expenses
                if df.empty:
                    return {'status': 'info', 'message': 'No expenses logged yet'}
                
                # Get the month and year to filter by
                month = tool_response_dict['instructions'].get('month', '')
                year = tool_response_dict['instructions'].get('year', '')
                
                if not month or not year:
                    return {'status': 'error', 'message': 'Both month and year must be specified for view_expenses_by_month'}
                
                try:
                    # Parse month and year as integers
                    month = int(month)
                    year = int(year)
                    
                    # Validate month range
                    if month < 1 or month > 12:
                        return {'status': 'error', 'message': 'Month must be between 1 and 12'}
                    
                    # Convert date strings to datetime objects
                    df['date_obj'] = pd.to_datetime(df['date'], format='%d/%m/%Y')
                    
                    # Filter expenses by year and month
                    filtered_df = df[(df['date_obj'].dt.year == year) & (df['date_obj'].dt.month == month)]
                    
                    # Drop temporary column
                    filtered_df = filtered_df.drop('date_obj', axis=1)
                    
                except (ValueError, TypeError):
                    return {'status': 'error', 'message': 'Invalid month or year format. Month and year must be numbers.'}
                
                if filtered_df.empty:
                    return {'status': 'info', 'message': f'No expenses found for month: {month}/{year}'}
                
                return {'status': 'success', 'data': filtered_df.to_dict('records')}
                
            elif tool_response_dict['instructions']["action"] == "view_monthwise_expenses":
                # Check if expense_log.csv exists
                if not os.path.exists('./data/finance/expense_log.csv'):
                    return {'status': 'error', 'message': 'No expense log found'}
                
                # Read the expense log
                df = pd.read_csv('./data/finance/expense_log.csv')
                
                # Check if there are any expenses
                if df.empty:
                    return {'status': 'info', 'message': 'No expenses logged yet'}
                
                # Convert date strings to datetime objects
                df['date_obj'] = pd.to_datetime(df['date'], format='%d/%m/%Y')
                
                # Extract year and month from date
                df['year_month'] = df['date_obj'].dt.strftime('%Y-%m')
                
                # Group by year-month and return summary
                monthly_summary = df.groupby('year_month').agg({
                    'amount': ['sum', 'count']
                }).reset_index()
                monthly_summary.columns = ['month', 'total_amount', 'count']
                
                # Sort by month
                monthly_summary = monthly_summary.sort_values(by='month', ascending=False)
                
                # Create interactive bar chart with plotly
                fig = px.bar(
                    monthly_summary, 
                    x='month', 
                    y='total_amount',
                    title='Month-wise Expenses',
                    labels={'month': 'Month', 'total_amount': 'Total Amount'},
                    color='total_amount',
                    color_continuous_scale='Viridis'
                )
                
                # Improve layout with larger text sizes
                fig.update_layout(
                    xaxis_title='Month',
                    yaxis_title='Total Amount',
                    margin=dict(l=20, r=20, t=40, b=20),
                    font=dict(
                        family="Arial, sans-serif",
                        size=24,  # Base font size
                        color="black"
                    ),
                    title_font=dict(size=24),  # Title font size
                    legend_font=dict(size=24)  # Legend font size
                )
                
                # Update axis title font sizes
                fig.update_xaxes(title_font=dict(size=24))
                fig.update_yaxes(title_font=dict(size=24))
                
                # Ensure directory exists
                os.makedirs('./data/finance', exist_ok=True)
                
                # Save as static image with higher resolution and dimensions
                fig.write_image('./data/finance/monthwise_expenses.png', width=2000, height=800, scale=2)
                
                return {'status': 'success', 'data': monthly_summary.to_dict('records'), 'image_path': ['./data/finance/monthwise_expenses.png']}
                
            elif tool_response_dict['instructions']["action"] == "view_yearwise_expenses":
                # Check if expense_log.csv exists
                if not os.path.exists('./data/finance/expense_log.csv'):
                    return {'status': 'error', 'message': 'No expense log found'}
                
                # Read the expense log
                df = pd.read_csv('./data/finance/expense_log.csv')
                
                # Check if there are any expenses
                if df.empty:
                    return {'status': 'info', 'message': 'No expenses logged yet'}
                
                # Convert date strings to datetime objects
                df['date_obj'] = pd.to_datetime(df['date'], format='%d/%m/%Y')
                
                # Extract year from date
                df['year'] = df['date_obj'].dt.year
                
                # Group by year and return summary
                yearly_summary = df.groupby('year').agg({
                    'amount': ['sum', 'count']
                }).reset_index()
                yearly_summary.columns = ['year', 'total_amount', 'count']
                
                # Sort by year
                yearly_summary = yearly_summary.sort_values(by='year', ascending=False)
                # Create interactive bar chart with plotly
                fig = px.bar(
                    yearly_summary, 
                    x='year', 
                    y='total_amount',
                    title='Year-wise Expenses',
                    labels={'year': 'Year', 'total_amount': 'Total Amount'},
                    color='total_amount',
                    color_continuous_scale='Viridis'
                )
                
                # Improve layout with larger text sizes
                fig.update_layout(
                    xaxis_title='Year',
                    yaxis_title='Total Amount',
                    margin=dict(l=20, r=20, t=40, b=20),
                    font=dict(
                        family="Arial, sans-serif",
                        size=24,  # Base font size
                        color="black"
                    ),
                    title_font=dict(size=24),  # Title font size
                    legend_font=dict(size=24)  # Legend font size
                )
                
                # Update axis title font sizes
                fig.update_xaxes(title_font=dict(size=24))
                fig.update_yaxes(title_font=dict(size=24))
                
                # Ensure directory exists
                os.makedirs('./data/finance', exist_ok=True)
                
                # Save as static image with higher resolution and dimensions
                fig.write_image('./data/finance/yearwise_expenses.png', width=2000, height=800, scale=2)
                
                return {'status': 'success', 'data': yearly_summary.to_dict('records'), 'image_path': ['./data/finance/yearwise_expenses.png']}

            elif tool_response_dict['instructions']["action"] == "view_expenses_by_year":
                # Check if expense_log.csv exists
                if not os.path.exists('./data/finance/expense_log.csv'):
                    return {'status': 'error', 'message': 'No expense log found'}
                
                # Read the expense log
                df = pd.read_csv('./data/finance/expense_log.csv')
                
                # Check if there are any expenses
                if df.empty:
                    return {'status': 'info', 'message': 'No expenses logged yet'}
                
                # Get the year to filter by
                year_str = tool_response_dict['instructions'].get('year', '')
                
                if not year_str:
                    return {'status': 'error', 'message': 'No year specified for view_expenses_by_year'}
                
                try:
                    # Parse the year
                    year = int(year_str)
                    
                    # Convert date strings to datetime objects
                    df['date_obj'] = pd.to_datetime(df['date'], format='%d/%m/%Y')
                    
                    # Filter expenses by year
                    filtered_df = df[df['date_obj'].dt.year == year]
                    
                    # Drop temporary column
                    filtered_df = filtered_df.drop('date_obj', axis=1)
                    
                except (ValueError, TypeError):
                    return {'status': 'error', 'message': 'Invalid year format. Use YYYY (e.g., 2023)'}
                
                if filtered_df.empty:
                    return {'status': 'info', 'message': f'No expenses found for year: {year_str}'}
                
                return {'status': 'success', 'data': filtered_df.to_dict('records')}
                
        elif tool_response_dict["tool"] == "diary":
            if tool_response_dict['instructions']["action"] == "create_entry":
                pass
            elif tool_response_dict['instructions']["action"] == "view_entry":
                pass
            elif tool_response_dict['instructions']["action"] == "edit_entry":
                pass
            elif tool_response_dict['instructions']["action"] == "delete_entry":
                pass

'''
Calender:

Create event:
Tool response: {
  "tool": "calendar",
  "instructions": {
    "action": "create",
    "start_time": "05/04/2025 15:00",
    "end_time": "05/04/2025 16:00",
    "description": "OpenAI API payment",
    "location": "London"
  }
}
View event: 


------------------------
Email:

Send email:

Tool response: {
  "tool": "email",
  "instructions": {
    "action": "send",
    "to": "yash@gmail.com",
    "from": "dipayan@gmail.com",
    "subject": "Event Confirmation",
    "content": "Dear Yash,\n\nI hope this message finds you well. I wanted to confirm that I will see you at the event today. Looking forward to it!\n\nBest regards,\nDipayan"
  }
}

View emails:

{
  "tool": "email",
  "instructions": {
    "action": "read",
    "until_date": "29/03/2025",
  }
}


'''