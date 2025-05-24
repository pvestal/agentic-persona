"""
Gmail Integration for Agentic Persona
Handles email reading and automated responses
"""

import os
import base64
from typing import List, Dict, Any
from datetime import datetime, timedelta

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class GmailIntegration:
    def __init__(self):
        self.scopes = ['https://www.googleapis.com/auth/gmail.modify']
        self.client_config = {
            "web": {
                "client_id": os.environ.get('GOOGLE_CLIENT_ID'),
                "client_secret": os.environ.get('GOOGLE_CLIENT_SECRET'),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [os.environ.get('GOOGLE_REDIRECT_URI')]
            }
        }
    
    def get_auth_url(self, state: str) -> str:
        """Generate OAuth authorization URL"""
        flow = Flow.from_client_config(
            self.client_config,
            scopes=self.scopes,
            state=state
        )
        flow.redirect_uri = self.client_config['web']['redirect_uris'][0]
        
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        return auth_url
    
    def exchange_code(self, code: str, state: str) -> Dict[str, Any]:
        """Exchange authorization code for tokens"""
        flow = Flow.from_client_config(
            self.client_config,
            scopes=self.scopes,
            state=state
        )
        flow.redirect_uri = self.client_config['web']['redirect_uris'][0]
        
        flow.fetch_token(code=code)
        
        credentials = flow.credentials
        return {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
    
    def get_service(self, credentials_dict: Dict[str, Any]):
        """Create Gmail service instance"""
        credentials = Credentials(
            token=credentials_dict['token'],
            refresh_token=credentials_dict['refresh_token'],
            token_uri=credentials_dict['token_uri'],
            client_id=credentials_dict['client_id'],
            client_secret=credentials_dict['client_secret'],
            scopes=credentials_dict['scopes']
        )
        
        return build('gmail', 'v1', credentials=credentials)
    
    def get_recent_messages(self, service, query: str = '', max_results: int = 10) -> List[Dict]:
        """Fetch recent messages"""
        try:
            # Default query for unread important messages
            if not query:
                query = 'is:unread is:important'
            
            results = service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            detailed_messages = []
            for msg in messages:
                msg_data = service.users().messages().get(
                    userId='me',
                    id=msg['id']
                ).execute()
                
                # Parse message
                parsed = self._parse_message(msg_data)
                detailed_messages.append(parsed)
            
            return detailed_messages
            
        except HttpError as error:
            print(f'An error occurred: {error}')
            return []
    
    def _parse_message(self, message_data: Dict) -> Dict:
        """Parse Gmail message into structured format"""
        headers = message_data['payload'].get('headers', [])
        
        # Extract header information
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
        
        # Extract body
        body = self._get_message_body(message_data['payload'])
        
        # Check importance
        labels = message_data.get('labelIds', [])
        is_important = 'IMPORTANT' in labels
        is_unread = 'UNREAD' in labels
        
        return {
            'id': message_data['id'],
            'threadId': message_data['threadId'],
            'subject': subject,
            'sender': sender,
            'date': date,
            'body': body,
            'snippet': message_data.get('snippet', ''),
            'isImportant': is_important,
            'isUnread': is_unread,
            'labels': labels
        }
    
    def _get_message_body(self, payload: Dict) -> str:
        """Extract message body from payload"""
        body = ''
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body']['data']
                    body += base64.urlsafe_b64decode(data).decode('utf-8')
        elif payload['body'].get('data'):
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        
        return body
    
    def send_reply(self, service, message_id: str, reply_text: str) -> Dict:
        """Send a reply to a message"""
        try:
            # Get original message
            original = service.users().messages().get(
                userId='me',
                id=message_id
            ).execute()
            
            # Get thread ID
            thread_id = original['threadId']
            
            # Parse headers
            headers = original['payload'].get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
            to = next((h['value'] for h in headers if h['name'] == 'From'), '')
            
            # Create reply
            message = self._create_message(
                to=to,
                subject=f"Re: {subject}",
                body=reply_text,
                thread_id=thread_id
            )
            
            # Send reply
            result = service.users().messages().send(
                userId='me',
                body=message
            ).execute()
            
            return result
            
        except HttpError as error:
            print(f'An error occurred: {error}')
            return None
    
    def _create_message(self, to: str, subject: str, body: str, thread_id: str = None) -> Dict:
        """Create a message for sending"""
        message_text = f"To: {to}\n"
        message_text += f"Subject: {subject}\n\n"
        message_text += body
        
        message = {
            'raw': base64.urlsafe_b64encode(message_text.encode()).decode()
        }
        
        if thread_id:
            message['threadId'] = thread_id
        
        return message
    
    def mark_as_read(self, service, message_id: str):
        """Mark a message as read"""
        try:
            service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
        except HttpError as error:
            print(f'An error occurred: {error}')
    
    def watch_inbox(self, service, topic_name: str) -> Dict:
        """Set up push notifications for new emails"""
        try:
            request = {
                'labelIds': ['INBOX'],
                'topicName': topic_name
            }
            
            result = service.users().watch(
                userId='me',
                body=request
            ).execute()
            
            return result
            
        except HttpError as error:
            print(f'An error occurred: {error}')
            return None