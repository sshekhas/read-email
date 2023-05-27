Gmail API Email Fetcher and modifier
This project demonstrates how to authenticate to Google's Gmail API using OAuth and fetch a list of emails from the Inbox using Google's official Python client library.
Also do modification on emails based on some set of rules.
Prerequisites
Before running the code, make sure you have the following prerequisites:

Python (version 3.6 or higher) installed on your system.
Google Cloud Platform (GCP) project with the Gmail API enabled.
OAuth 2.0 credentials (client ID and client secret) generated from the GCP project.
Installation
Clone this repository to your local machine or download the code files.

Install the required dependencies by running the following command in your terminal:
pip install -r requirements.txt

Setup a database in postgress and modify settings.py in project root accoring to your database settings.

Save cretentials downloaded from GCP in root of the project and modify settings.py CREDENTIALS_FILE according to your credentials file name.

Run

python capture_mails.py 

This will populate all the mails from inbox inyour db

Run

python run_rules.py


this will run through set of rules mentiond in rules.json and run actions using gmail apis




