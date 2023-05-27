import os
from authanticate_gmail import get_auth_credentials
from googleapiclient.discovery import build
import base64
import settings
import psycopg2
from datetime import datetime


# Connect to the PostgreSQL database
conn = psycopg2.connect(
    host=settings.DB_HOST,
    port=settings.DB_PORT,
    database=settings.DB_NAME,
    user=settings.DB_USER,
    password=settings.DB_PASSWORD
)

# Create a cursor object
cursor = conn.cursor()

# Create the emails table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS emails (
        id SERIAL PRIMARY KEY,
        subject TEXT,
        sender TEXT,
        body TEXT,
        email_date TIMESTAMP,
        receiver TEXT,
        msg_id TEXT
    )
''')

# Commit the table creation and close the cursor
conn.commit()
cursor.close()

creds = get_auth_credentials()

service = build('gmail', 'v1', credentials=creds)

# Fetch a list of emails from the Inbox
results = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
messages = results.get('messages', [])

# Iterate over the messages and fetch their details if needed
for message in messages:
    txt = service.users().messages().get(userId='me', id=message['id']).execute()
    try:
        # Get value of 'payload' from dictionary 'txt'
        payload = txt['payload']
        headers = payload['headers']

        # Look for Subject and Sender Email in the headers
        for d in headers:
            if d['name'] == 'Subject':
                subject = d['value']
            if d['name'] == 'From':
                sender = d['value']
            if d['name'] == 'Date':
                recieved_on = d['value']
                recieved_on = recieved_on.split("+")[0].split(",")[1].strip()
                if "GMT" in recieved_on:
                    recieved_on = recieved_on.replace("GMT", "").strip()
                recieved_on = datetime.strptime(recieved_on, settings.DATE_FORMAT)
            if d['name'] == 'To':
                receiver = d['value']

        # The Body of the message is in Encrypted format. So, we have to decode it.
        # Get the data and decode it with base 64 decoder.
        parts = payload.get('parts')[0]
        data = parts['body']['data']
        data = data.replace("-","+").replace("_","/")
        decoded_data = base64.b64decode(data)
        body = decoded_data.decode('utf-8')
        #Insert the email details into the table
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO emails (subject, sender, body, email_date, receiver, msg_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (subject, sender, body, recieved_on, receiver, message['id']))

        # Commit the changes and close the cursor
        conn.commit()
        cursor.close()
        
    except Exception as e:
        print("error", e)
        pass