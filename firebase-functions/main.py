"""
Firebase Cloud Functions for Agentic Persona
Handles backend API endpoints in serverless environment
"""

import os
import json
import random
from typing import Dict, Any, Optional
from datetime import datetime

import firebase_admin
from firebase_admin import credentials, firestore, auth
from firebase_functions import https_fn, options
from firebase_functions.firestore_fn import on_document_created
from flask import Flask, jsonify, request
from flask_cors import CORS

# Initialize Firebase Admin
if not firebase_admin._apps:
    firebase_admin.initialize_app()

db = firestore.client()
app = Flask(__name__)
CORS(app)

# Import our services and integrations
from integrations.gmail import GmailIntegration
from integrations.slack import SlackIntegration
from integrations.telegram import TelegramIntegration
from integrations.sms import SMSIntegration

# For demo purposes, we'll create simplified versions of these services
# In production, you'd copy the actual services from echo-backend
class LLMService:
    def __init__(self):
        self.provider = os.environ.get('LLM_PROVIDER', 'openai')
    
    async def generate_response(self, prompt, context=None):
        # Simplified implementation
        return {
            'response': f"Automated response to: {prompt[:50]}...",
            'confidence': 0.85
        }

class AutonomousResponder:
    def __init__(self):
        self.llm_service = LLMService()
    
    def process_message(self, message_data):
        # Simplified implementation
        importance = message_data.get('importance', 'normal')
        should_auto_respond = importance in ['high', 'urgent']
        
        return {
            'response': f"Re: {message_data.get('content', '')[:50]}...",
            'should_auto_respond': should_auto_respond,
            'confidence': 0.9 if should_auto_respond else 0.5
        }

class SimpleLearningSystem:
    def __init__(self):
        self.feedback_store = []
    
    def record_feedback(self, **kwargs):
        self.feedback_store.append(kwargs)
        return {'success': True, 'feedback_id': len(self.feedback_store)}

# Initialize services
llm_service = LLMService()
responder = AutonomousResponder()
learning_system = SimpleLearningSystem()
gmail_integration = GmailIntegration()
slack_integration = SlackIntegration()
telegram_integration = TelegramIntegration()
sms_integration = SMSIntegration()

# === Authentication Middleware ===
def verify_auth_token(req):
    """Verify Firebase Auth token from request"""
    auth_header = req.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.split('Bearer ')[1]
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        print(f"Auth error: {e}")
        return None

# === Agent Endpoints ===
@app.route('/api/agents', methods=['GET'])
def get_agents():
    """Get user's agents"""
    user = verify_auth_token(request)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Get user's agents from Firestore
    agents_ref = db.collection('agents').where('userId', '==', user['uid'])
    agents = []
    
    for doc in agents_ref.stream():
        agent_data = doc.to_dict()
        agent_data['id'] = doc.id
        agents.append(agent_data)
    
    return jsonify(agents)

@app.route('/api/agents/<agent_id>/config', methods=['PUT'])
def update_agent_config(agent_id):
    """Update agent configuration"""
    user = verify_auth_token(request)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    config = request.get_json()
    
    # Update in Firestore
    agent_ref = db.collection('agents').document(agent_id)
    agent_doc = agent_ref.get()
    
    if not agent_doc.exists or agent_doc.to_dict().get('userId') != user['uid']:
        return jsonify({'error': 'Agent not found'}), 404
    
    agent_ref.update({
        'config': config,
        'updatedAt': firestore.SERVER_TIMESTAMP
    })
    
    return jsonify({'success': True, 'config': config})

# === Message Processing ===
@app.route('/api/messages/process', methods=['POST'])
def process_message():
    """Process a message through the agent system"""
    user = verify_auth_token(request)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    message = data.get('message', '')
    platform = data.get('platform', 'web')
    context = data.get('context', {})
    
    # Store message in Firestore
    message_doc = {
        'userId': user['uid'],
        'message': message,
        'platform': platform,
        'context': context,
        'timestamp': firestore.SERVER_TIMESTAMP,
        'status': 'processing'
    }
    
    doc_ref = db.collection('messages').add(message_doc)[1]
    
    try:
        # Process with responder
        response = responder.process_message({
            'content': message,
            'sender': user.get('email', 'user'),
            'platform': platform,
            'importance': context.get('importance', 'normal'),
            'timestamp': datetime.now().isoformat()
        })
        
        # Update message with response
        doc_ref.update({
            'response': response,
            'status': 'completed',
            'completedAt': firestore.SERVER_TIMESTAMP
        })
        
        return jsonify({
            'messageId': doc_ref.id,
            'response': response['response'],
            'shouldAutoRespond': response.get('should_auto_respond', False),
            'confidence': response.get('confidence', 0.0)
        })
        
    except Exception as e:
        doc_ref.update({
            'status': 'error',
            'error': str(e)
        })
        return jsonify({'error': str(e)}), 500

# === Learning System ===
@app.route('/api/learning/feedback', methods=['POST'])
def submit_feedback():
    """Submit feedback for learning"""
    user = verify_auth_token(request)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    feedback = request.get_json()
    
    # Store in Firestore
    feedback_doc = {
        **feedback,
        'userId': user['uid'],
        'timestamp': firestore.SERVER_TIMESTAMP
    }
    
    db.collection('learning').document(user['uid']).collection('feedback').add(feedback_doc)
    
    # Process with learning system
    result = learning_system.record_feedback(
        message_id=feedback.get('message_id'),
        feedback_type=feedback.get('feedback_type'),
        original_response=feedback.get('original_response'),
        edited_response=feedback.get('edited_response'),
        rating=feedback.get('rating')
    )
    
    return jsonify(result)

# === Evolution System ===
@app.route('/api/evolution/metrics', methods=['GET'])
def get_evolution_metrics():
    """Get user's evolution metrics"""
    user = verify_auth_token(request)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Get metrics from Firestore
    evolution_ref = db.collection('evolution').document(user['uid'])
    evolution_doc = evolution_ref.get()
    
    if evolution_doc.exists:
        return jsonify(evolution_doc.to_dict().get('metrics', {}))
    
    return jsonify({
        'total_evolutions': 0,
        'agents_evolved': {},
        'capability_additions': 0,
        'performance_improvements': 0
    })

# === Platform Integrations ===
@app.route('/api/integrations/gmail/auth', methods=['POST'])
def gmail_auth():
    """Initialize Gmail OAuth flow"""
    user = verify_auth_token(request)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Return OAuth URL for Gmail
    # This would be implemented with Google OAuth2 flow
    return jsonify({
        'authUrl': f"https://accounts.google.com/oauth2/v2/auth?client_id={os.environ.get('GOOGLE_CLIENT_ID')}&redirect_uri={os.environ.get('GOOGLE_REDIRECT_URI')}&scope=https://www.googleapis.com/auth/gmail.modify&response_type=code&access_type=offline&state={user['uid']}"
    })

@app.route('/api/integrations/gmail/callback', methods=['POST'])
def gmail_callback():
    """Handle Gmail OAuth callback"""
    user = verify_auth_token(request)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    code = request.get_json().get('code')
    state = request.get_json().get('state')
    
    # Exchange code for tokens
    tokens = gmail_integration.exchange_code(code, state)
    
    # Store tokens securely in Firestore
    user_ref = db.collection('users').document(user['uid'])
    user_ref.update({
        'integrations.gmail': {
            'connected': True,
            'tokens': tokens,  # In production, encrypt these
            'connectedAt': firestore.SERVER_TIMESTAMP
        }
    })
    
    return jsonify({'success': True})

# === Telegram Integration ===
@app.route('/api/integrations/telegram/connect', methods=['POST'])
def telegram_connect():
    """Connect Telegram account"""
    user = verify_auth_token(request)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Generate unique connection token
    connection_token = f"echo_{user['uid'][:8]}"
    
    # Store pending connection
    db.collection('telegram_connections').document(connection_token).set({
        'userId': user['uid'],
        'status': 'pending',
        'createdAt': firestore.SERVER_TIMESTAMP
    })
    
    return jsonify({
        'bot_username': os.environ.get('TELEGRAM_BOT_USERNAME', 'echo_bot'),
        'connection_token': connection_token,
        'instructions': f"Open Telegram and send /start {connection_token} to the bot"
    })

@app.route('/api/integrations/telegram/webhook', methods=['POST'])
def telegram_webhook():
    """Handle Telegram webhook updates"""
    update = request.get_json()
    
    # Process with Telegram integration
    # This would handle incoming messages and commands
    
    return jsonify({'ok': True})

# === SMS Integration ===
@app.route('/api/integrations/sms/connect', methods=['POST'])
def sms_connect():
    """Connect SMS via phone number verification"""
    user = verify_auth_token(request)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    phone_number = request.get_json().get('phone_number')
    
    # Verify phone number
    verification = sms_integration.verify_phone_number(phone_number)
    
    if verification['valid']:
        # Generate verification code
        verification_code = str(random.randint(100000, 999999))
        
        # Store pending verification
        db.collection('sms_verifications').document(user['uid']).set({
            'phone_number': verification['phone_number'],
            'code': verification_code,
            'createdAt': firestore.SERVER_TIMESTAMP,
            'verified': False
        })
        
        # Send verification SMS
        sms_integration.send_sms(
            verification['phone_number'],
            f"Your ECHO verification code is: {verification_code}"
        )
        
        return jsonify({
            'success': True,
            'phone_number': verification['national_format']
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Invalid phone number'
        }), 400

@app.route('/api/integrations/sms/verify', methods=['POST'])
def sms_verify():
    """Verify SMS code"""
    user = verify_auth_token(request)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    code = request.get_json().get('code')
    
    # Check verification code
    verification_doc = db.collection('sms_verifications').document(user['uid']).get()
    
    if verification_doc.exists:
        verification = verification_doc.to_dict()
        
        if verification['code'] == code and not verification['verified']:
            # Update user with verified phone
            user_ref = db.collection('users').document(user['uid'])
            user_ref.update({
                'integrations.sms': {
                    'connected': True,
                    'phone_number': verification['phone_number'],
                    'connectedAt': firestore.SERVER_TIMESTAMP
                }
            })
            
            # Mark as verified
            db.collection('sms_verifications').document(user['uid']).update({
                'verified': True
            })
            
            return jsonify({'success': True})
    
    return jsonify({'error': 'Invalid code'}), 400

@app.route('/api/integrations/sms/webhook', methods=['POST'])
def sms_webhook():
    """Handle incoming SMS from Twilio"""
    # Verify webhook signature
    # Process incoming SMS
    response = sms_integration.handle_incoming_sms(request.form.to_dict())
    
    return response, 200, {'Content-Type': 'text/xml'}

# === Export Cloud Functions ===
@https_fn.on_request(
    cors=options.CorsOptions(
        cors_origins="*",
        cors_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )
)
def api(req: https_fn.Request) -> https_fn.Response:
    """Main API endpoint for Cloud Functions"""
    with app.request_context(req.environ):
        return app.full_dispatch_request()

@on_document_created(document="messages/{messageId}")
def on_message_created(event: Event[DocumentSnapshot]) -> None:
    """Trigger when a new message is created"""
    message_data = event.data.to_dict()
    
    # Check if auto-response is enabled
    user_id = message_data.get('userId')
    platform = message_data.get('platform')
    
    # Get user's autonomy settings
    user_ref = db.collection('users').document(user_id)
    user_doc = user_ref.get()
    
    if user_doc.exists:
        autonomy_settings = user_doc.to_dict().get('autonomySettings', {})
        autonomy_level = autonomy_settings.get(platform, 0)
        
        if autonomy_level >= 3:  # Auto-respond threshold
            # Process message asynchronously
            responder.process_message({
                'content': message_data['message'],
                'sender': user_id,
                'platform': platform,
                'importance': message_data.get('context', {}).get('importance', 'normal'),
                'timestamp': datetime.now().isoformat()
            })