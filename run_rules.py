import json
import psycopg2
from psycopg2.extras import DictCursor
from authanticate_gmail import get_auth_credentials
from googleapiclient.discovery import build
import settings
from datetime import datetime

# Load rules from JSON file
with open('rules.json') as f:
    rules = json.load(f)

# Fetch emails from db


# Connect to the PostgreSQL database
conn = psycopg2.connect(
    host=settings.DB_HOST,
    port=settings.DB_PORT,
    database=settings.DB_NAME,
    user=settings.DB_USER,
    password=settings.DB_PASSWORD
)

# Create a cursor object with DictCursor
cursor = conn.cursor(cursor_factory=DictCursor)

# Execute a SELECT query to fetch data from the emails table
select_query = "SELECT * FROM emails"
cursor.execute(select_query)

# Fetch all rows as dictionaries
fetched_emails = cursor.fetchall()

# Close the cursor and connection
cursor.close()
conn.close()

creds = get_auth_credentials()

service = build('gmail', 'v1', credentials=creds)

labels = service.users().labels().list(userId='me').execute()


# Iterate through emails
for email in fetched_emails:
    # Initialize a variable to track rule matches
    

    for rule in rules:
        condition_matches = 0
        for condition in rule["conditions"]:
        # Evaluate conditions based on field, predicate, and value
            if condition['predicate'] == 'Contains' and condition['value'] in email.get(condition['field'], ""):
                condition_matches += 1
            elif condition['predicate'] == 'Equals' and condition['value'] == email.get(condition['field'], ""):
                condition_matches += 1

            elif condition['predicate'] == "Does not Contain" and condition['value'] not in email.get(condition['field'], ""):
                condition_matches += 1
            elif condition['predicate'] == "Does not equal" and condition['value'] != email.get(condition['field'], ""):
                condition_matches += 1
            elif condition['predicate'] == "Less than" and email.get(condition['field']) and datetime.strptime(condition['value'], settings.DATE_FORMAT) > email.get(rule['field']):
                condition_matches += 1

            elif condition['predicate'] == "Greater than" and email.get(condition['field']) and datetime.strptime(condition['value'], settings.DATE_FORMAT) < email.get(condition['field']):
                condition_matches += 1


        # Check rule matches based on the overall predicate
        if (condition_matches == len(rule["conditions"]) and rule['overall_predicate'] == 'All') or (condition_matches >= 1 and rule['overall_predicate'] == 'Any'):
             for action in rule["actions"]:
                if action["action"] == "Mark as read":
                    service.users().messages().modify(userId='me', id=email.get("msg_id"), body={'removeLabelIds': ['UNREAD']}).execute()
                elif action["action"] == "Mark as unread":
                    service.users().messages().modify(userId='me', id=email.get("msg_id"), body={'addLabelIds': ['UNREAD']}).execute()
                elif action["action"] == "Move Message":
                    folder_id = None
                    for label in labels['labels']:
                        if label['name'] == action['folder']:
                            folder_id = label['id']
                            break
                    if folder_id:
                        service.users().messages().modify(userId='me', id=email.get("msg_id"), body={'addLabelIds': [folder_id]}).execute()
                    else:
                        print("not able to move folder id not found ", action['folder'])
                    
                