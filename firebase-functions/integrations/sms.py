"""
SMS Integration for Agentic Persona using Twilio
Handles SMS messaging and automated responses
"""

import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from twilio.twiml.messaging_response import MessagingResponse

logger = logging.getLogger(__name__)

class SMSIntegration:
    def __init__(self):
        self.account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        self.auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        self.phone_number = os.environ.get('TWILIO_PHONE_NUMBER')
        self.webhook_url = os.environ.get('TWILIO_WEBHOOK_URL')
        self.client = None
        
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
    
    def verify_credentials(self) -> bool:
        """Verify Twilio credentials are valid"""
        if not self.client:
            return False
            
        try:
            # Try to fetch account details
            account = self.client.api.accounts(self.account_sid).fetch()
            return account.status == 'active'
        except TwilioRestException as e:
            logger.error(f"Failed to verify Twilio credentials: {e}")
            return False
    
    def send_sms(self, to_number: str, message: str, media_url: Optional[str] = None) -> Dict:
        """Send an SMS message"""
        if not self.client:
            raise ValueError("Twilio client not initialized")
        
        try:
            # Ensure number is in E.164 format
            if not to_number.startswith('+'):
                to_number = '+1' + to_number  # Default to US
            
            message_params = {
                'body': message,
                'from_': self.phone_number,
                'to': to_number
            }
            
            # Add media URL if provided (MMS)
            if media_url:
                message_params['media_url'] = [media_url]
            
            # Send message
            message = self.client.messages.create(**message_params)
            
            return {
                'success': True,
                'message_sid': message.sid,
                'to': message.to,
                'from': message.from_,
                'status': message.status,
                'date_sent': message.date_sent.isoformat() if message.date_sent else None,
                'price': message.price,
                'direction': message.direction
            }
            
        except TwilioRestException as e:
            logger.error(f"Failed to send SMS: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_code': e.code
            }
    
    def get_messages(self, limit: int = 20, date_sent_after: Optional[datetime] = None) -> List[Dict]:
        """Retrieve recent messages"""
        if not self.client:
            raise ValueError("Twilio client not initialized")
        
        try:
            # Default to last 24 hours if no date specified
            if not date_sent_after:
                date_sent_after = datetime.now() - timedelta(days=1)
            
            messages = self.client.messages.list(
                limit=limit,
                date_sent_after=date_sent_after
            )
            
            return [self._format_message(msg) for msg in messages]
            
        except TwilioRestException as e:
            logger.error(f"Failed to fetch messages: {e}")
            return []
    
    def _format_message(self, message) -> Dict:
        """Format Twilio message object to dict"""
        return {
            'sid': message.sid,
            'body': message.body,
            'from': message.from_,
            'to': message.to,
            'status': message.status,
            'direction': message.direction,
            'date_sent': message.date_sent.isoformat() if message.date_sent else None,
            'date_created': message.date_created.isoformat() if message.date_created else None,
            'price': message.price,
            'num_segments': message.num_segments,
            'num_media': message.num_media,
            'media_urls': [media.uri for media in message.media.list()] if message.num_media > '0' else []
        }
    
    def handle_incoming_sms(self, request_data: Dict) -> str:
        """Handle incoming SMS webhook from Twilio"""
        # Extract message data
        from_number = request_data.get('From')
        to_number = request_data.get('To')
        body = request_data.get('Body', '')
        message_sid = request_data.get('MessageSid')
        num_media = int(request_data.get('NumMedia', 0))
        
        # Extract media URLs if present
        media_urls = []
        for i in range(num_media):
            media_url = request_data.get(f'MediaUrl{i}')
            if media_url:
                media_urls.append(media_url)
        
        # Create message record
        message_data = {
            'platform': 'sms',
            'message_id': message_sid,
            'from': from_number,
            'to': to_number,
            'body': body,
            'media_urls': media_urls,
            'timestamp': datetime.now().isoformat(),
            'direction': 'inbound'
        }
        
        # Process message and generate response
        response_text = self._process_incoming_message(message_data)
        
        # Create TwiML response
        resp = MessagingResponse()
        resp.message(response_text)
        
        return str(resp)
    
    def _process_incoming_message(self, message_data: Dict) -> str:
        """Process incoming message and generate response"""
        # This would integrate with the AI system
        # For now, return a simple acknowledgment
        
        body = message_data.get('body', '').lower()
        
        # Handle common commands
        if 'help' in body:
            return (
                "ECHO SMS Commands:\n"
                "HELP - Show this message\n"
                "STATUS - Check automation status\n"
                "STOP - Stop notifications\n"
                "START - Resume notifications\n"
                "SUMMARY - Get daily summary"
            )
        elif 'status' in body:
            return "🤖 ECHO Active | 📧 Gmail: Connected | 💬 SMS: Active | Last sync: 2 min ago"
        elif 'summary' in body:
            return "📊 Today: 15 messages processed, 3 auto-responses sent, 2 tasks completed"
        else:
            return f"Message received: '{body[:50]}...'. Reply HELP for commands."
    
    def send_notification(self, to_number: str, notification_type: str, data: Dict) -> Dict:
        """Send notification via SMS"""
        emoji_map = {
            'new_email': '📧',
            'email_sent': '✉️',
            'task_reminder': '⏰',
            'daily_summary': '📊',
            'important_message': '🚨'
        }
        
        emoji = emoji_map.get(notification_type, '🔔')
        
        # Format message based on type
        if notification_type == 'new_email':
            message = f"{emoji} New email from {data.get('sender', 'Unknown')}\n"
            message += f"Subject: {data.get('subject', 'No subject')}\n"
            message += f"Preview: {data.get('preview', '')[:50]}..."
        elif notification_type == 'daily_summary':
            message = f"{emoji} Daily Summary\n"
            message += f"Emails: {data.get('email_count', 0)}\n"
            message += f"Tasks: {data.get('task_count', 0)}\n"
            message += f"Auto-responses: {data.get('auto_response_count', 0)}"
        else:
            message = f"{emoji} {notification_type}: {data.get('message', '')}"
        
        # SMS has 160 char limit, truncate if needed
        if len(message) > 160:
            message = message[:157] + "..."
        
        return self.send_sms(to_number, message)
    
    def verify_phone_number(self, phone_number: str) -> Dict:
        """Verify a phone number using Twilio Lookup"""
        if not self.client:
            raise ValueError("Twilio client not initialized")
        
        try:
            # Ensure number is in E.164 format
            if not phone_number.startswith('+'):
                phone_number = '+1' + phone_number  # Default to US
            
            phone_info = self.client.lookups.v1.phone_numbers(phone_number).fetch()
            
            return {
                'valid': True,
                'phone_number': phone_info.phone_number,
                'national_format': phone_info.national_format,
                'country_code': phone_info.country_code,
                'carrier': phone_info.carrier.get('name') if phone_info.carrier else None
            }
            
        except TwilioRestException as e:
            return {
                'valid': False,
                'error': str(e)
            }
    
    def create_messaging_service(self, friendly_name: str) -> Dict:
        """Create a messaging service for better deliverability"""
        if not self.client:
            raise ValueError("Twilio client not initialized")
        
        try:
            service = self.client.messaging.services.create(
                friendly_name=friendly_name,
                inbound_request_url=self.webhook_url,
                status_callback=f"{self.webhook_url}/status"
            )
            
            # Add phone number to service
            self.client.messaging.services(service.sid).phone_numbers.create(
                phone_number_sid=self._get_phone_number_sid()
            )
            
            return {
                'success': True,
                'service_sid': service.sid,
                'friendly_name': service.friendly_name
            }
            
        except TwilioRestException as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_phone_number_sid(self) -> str:
        """Get the SID of the configured phone number"""
        phone_numbers = self.client.incoming_phone_numbers.list(
            phone_number=self.phone_number
        )
        
        if phone_numbers:
            return phone_numbers[0].sid
        
        raise ValueError(f"Phone number {self.phone_number} not found in account")
    
    def get_usage_stats(self, start_date: datetime, end_date: datetime) -> Dict:
        """Get SMS usage statistics"""
        if not self.client:
            raise ValueError("Twilio client not initialized")
        
        try:
            usage_records = self.client.usage.records.list(
                category='sms',
                start_date=start_date,
                end_date=end_date
            )
            
            total_messages = 0
            total_cost = 0.0
            
            for record in usage_records:
                total_messages += int(record.count)
                total_cost += float(record.price)
            
            return {
                'total_messages': total_messages,
                'total_cost': total_cost,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            }
            
        except TwilioRestException as e:
            logger.error(f"Failed to fetch usage stats: {e}")
            return {
                'error': str(e)
            }