from datetime import datetime
import json

def update_calender_logs(time_str, event_str, calender_logs_path):
    entry = convert_time_format(time_str) + ' | ' + event_str
    #print(f"DEBUG: Entry: {entry}")
    # read the calender_logs_path
    with open(calender_logs_path, "r") as f:
        calender_logs = json.load(f)
    #print(f"DEBUG: Calender logs: {calender_logs}")
    # append the new entry to the calender_logs
    calender_logs['logs'].append(entry)
    #print(f"DEBUG: Calender logs after appending: {calender_logs}")
    # sort the calender_logs by time
    calender_logs['logs'] = sort_time_entries(calender_logs['logs'])
    #print(f"DEBUG: Calender logs after sorting: {calender_logs}")
    # write the calender_logs to the calender_logs_path
    with open(calender_logs_path, "w") as f:
        json.dump(calender_logs, f)

    #print(f"DEBUG: Calender logs updated: {calender_logs}")

def update_notification_logs(message, notification_logs_path):
    # read the notification_logs_path
    with open(notification_logs_path, "r") as f:
        notification_logs = json.load(f)
    # append the new entry to the notification_logs
    notification_logs['logs'].append(message)
    # reverse the notification_logs
    notification_logs['logs'].reverse()
    # write the notification_logs to the notification_logs_path
    with open(notification_logs_path, "w") as f:
        json.dump(notification_logs, f)

def convert_time_format(time_str):
    """
    Convert a time string from 24-hour format (HH:MM) to 12-hour format with am/pm.
    
    Args:
        time_str (str): Time string in 24-hour format (e.g., '21:00')
        
    Returns:
        str: Time string in 12-hour format with am/pm (e.g., '09:00 pm')
    """
    try:
        # Parse the time string
        hours, minutes = map(int, time_str.split(':'))
        
        # Determine am/pm
        period = 'AM' if hours < 12 else 'PM'
        
        # Convert to 12-hour format
        hours = hours % 12
        if hours == 0:
            hours = 12
            
        # Format the result with leading zeros and always show minutes
        return f"{hours:02d}:{minutes:02d} {period}"
    except:
        # Return the original string if there's any error
        return time_str
    
def sort_time_entries(entries):
    """
    Sort a list of time entries in 12-hour format.
    
    Args:
        entries (list): List of strings in format "HH:MM AM/PM | Description"
        
    Returns:
        list: Sorted list of entries by time of day
    """
    def extract_time(entry):
        # Extract the time part from the entry
        time_str = entry.split('|')[0].strip()
        
        # Parse the time and AM/PM
        time_parts = time_str.split()
        time_digits = time_parts[0]
        am_pm = time_parts[1].upper()
        
        # Split hours and minutes
        hours, minutes = map(int, time_digits.split(':'))
        
        # Convert to 24-hour format for sorting
        if am_pm == 'PM' and hours < 12:
            hours += 12
        elif am_pm == 'AM' and hours == 12:
            hours = 0
            
        # Return a value that can be used for sorting
        return hours * 60 + minutes
    
    # Sort the entries using the extract_time function
    return sorted(entries, key=extract_time)