# -*- coding: utf-8 -*-
"""
Created on Sat Jun 27 19:09:28 2020

@author: jokebill
"""

import base64
import os.path
import pickle
import twilio.rest
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

class GMail(object):
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    TOKEN_PATH = 'resource/token.pickle'
    CRED_PATH = 'resource/credentials.json'
    
    
    def __init__(self):
        self.service = self.Login()
        self.user = 'jokebill@gmail.com'
        self.receiver = 'zzwang.prim@gmail.com'
    
    
    def Login(self):
        """Login to gmail account."""
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(GMail.TOKEN_PATH):
            with open(GMail.TOKEN_PATH, 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    GMail.CRED_PATH, GMail.SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(GMail.TOKEN_PATH, 'wb') as token:
                pickle.dump(creds, token)
    
        service = build('gmail', 'v1', credentials=creds)
        return service
    
    def CreateMessage(self, subject, text):
        message = MIMEText(text)
        message['from'] = self.user
        message['to'] = self.receiver
        message['subject'] = subject
        return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}        
    
    def Send(self, subject, text):
        body = self.CreateMessage(subject, text)
        message = self.service.users().messages().send(
            userId=self.user, body=body).execute()
        print('Sent message Id: {}'.format(message['id']))
        
class SMS(object):
    ACCOUNT = ''
    TOKEN = ''
    RECEIVER = ''
    SENDER = ''
    def __init__(self, receiver=''):
        self.client = twilio.rest.Client(
            self.ACCOUNT,
            self.TOKEN)

    def Send(self, subject, text):
        message = subject+'\n\n'+text
        self.client.messages.create(
            body=message, from_=self.SENDER, to=self.RECEIVER)
        
    