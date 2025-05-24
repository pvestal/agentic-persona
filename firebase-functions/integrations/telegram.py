"""
Telegram Integration for Agentic Persona
Handles Telegram bot messaging and automated responses
"""

import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

import requests
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler

logger = logging.getLogger(__name__)

class TelegramIntegration:
    def __init__(self):
        self.bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        self.webhook_url = os.environ.get('TELEGRAM_WEBHOOK_URL')
        self.bot = None
        self.application = None
        
    def initialize_bot(self):
        """Initialize Telegram bot"""
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not set")
            
        self.bot = Bot(token=self.bot_token)
        self.application = Application.builder().token(self.bot_token).build()
        
        # Add handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("autonomy", self.autonomy_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        return self.application
    
    async def start_command(self, update: Update, context):
        """Handle /start command"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        welcome_text = (
            f"👋 Welcome {user.first_name}!\n\n"
            "I'm ECHO, your AI assistant. I can help you with:\n"
            "• 📧 Managing emails\n"
            "• 💬 Automated responses\n"
            "• 🧠 Learning your communication style\n\n"
            "Use /help to see available commands."
        )
        
        await update.message.reply_text(welcome_text)
        
        # Store user info
        user_data = {
            'telegram_id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'chat_id': chat_id,
            'started_at': datetime.now().isoformat()
        }
        
        return user_data
    
    async def help_command(self, update: Update, context):
        """Handle /help command"""
        help_text = (
            "🤖 *ECHO Bot Commands*\n\n"
            "/start - Initialize the bot\n"
            "/help - Show this help message\n"
            "/status - Check your automation status\n"
            "/autonomy - Set autonomy levels\n"
            "/connect - Connect other services\n"
            "/summary - Get daily summary\n\n"
            "Just send me a message and I'll help you draft a response!"
        )
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def status_command(self, update: Update, context):
        """Handle /status command"""
        user_id = update.effective_user.id
        
        # This would fetch from Firestore
        status_text = (
            "📊 *Your Automation Status*\n\n"
            "✉️ Gmail: Connected ✅\n"
            "💬 Telegram: Active ✅\n"
            "📱 SMS: Not connected ❌\n\n"
            "📈 Messages processed today: 15\n"
            "🤖 Auto-responses sent: 3\n"
            "⏰ Last activity: 2 minutes ago"
        )
        
        await update.message.reply_text(status_text, parse_mode='Markdown')
    
    async def autonomy_command(self, update: Update, context):
        """Handle /autonomy command"""
        keyboard = [
            [
                InlineKeyboardButton("📧 Gmail", callback_data='autonomy_gmail'),
                InlineKeyboardButton("💬 Telegram", callback_data='autonomy_telegram'),
                InlineKeyboardButton("📱 SMS", callback_data='autonomy_sms')
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "Select a platform to configure autonomy:",
            reply_markup=reply_markup
        )
    
    async def handle_message(self, update: Update, context):
        """Handle regular text messages"""
        message = update.message
        user_id = update.effective_user.id
        text = message.text
        
        # Log message
        message_data = {
            'platform': 'telegram',
            'user_id': user_id,
            'message': text,
            'timestamp': datetime.now().isoformat(),
            'chat_id': message.chat_id,
            'message_id': message.message_id
        }
        
        # Process with AI (simplified)
        response = await self.process_with_ai(text, user_id)
        
        # Send response
        await message.reply_text(response['text'])
        
        return message_data
    
    async def button_callback(self, update: Update, context):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        if query.data.startswith('autonomy_'):
            platform = query.data.split('_')[1]
            
            keyboard = [
                [InlineKeyboardButton("0️⃣ Off", callback_data=f'set_{platform}_0')],
                [InlineKeyboardButton("1️⃣ Notify only", callback_data=f'set_{platform}_1')],
                [InlineKeyboardButton("2️⃣ Draft responses", callback_data=f'set_{platform}_2')],
                [InlineKeyboardButton("3️⃣ Auto-respond (important)", callback_data=f'set_{platform}_3')],
                [InlineKeyboardButton("4️⃣ Full automation", callback_data=f'set_{platform}_4')]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"Set autonomy level for {platform.upper()}:",
                reply_markup=reply_markup
            )
        
        elif query.data.startswith('set_'):
            _, platform, level = query.data.split('_')
            
            await query.edit_message_text(
                f"✅ {platform.upper()} autonomy set to level {level}"
            )
            
            # Store in database
            return {
                'platform': platform,
                'autonomy_level': int(level),
                'user_id': update.effective_user.id
            }
    
    async def process_with_ai(self, text: str, user_id: int) -> Dict:
        """Process message with AI (simplified)"""
        # This would call the actual AI service
        return {
            'text': f"I understand you said: '{text[:50]}...'. How can I help you with this?",
            'confidence': 0.8,
            'suggested_action': 'draft_response'
        }
    
    async def send_message(self, chat_id: int, text: str, reply_markup=None):
        """Send a message to a specific chat"""
        if not self.bot:
            self.initialize_bot()
            
        return await self.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def send_notification(self, chat_id: int, notification_type: str, data: Dict):
        """Send notification about email/SMS activity"""
        emoji_map = {
            'new_email': '📧',
            'email_sent': '✉️',
            'new_sms': '📱',
            'sms_sent': '💬',
            'summary': '📊'
        }
        
        emoji = emoji_map.get(notification_type, '🔔')
        
        text = f"{emoji} *{notification_type.replace('_', ' ').title()}*\n\n"
        
        if notification_type == 'new_email':
            text += f"From: {data.get('sender', 'Unknown')}\n"
            text += f"Subject: {data.get('subject', 'No subject')}\n\n"
            text += f"Preview: {data.get('preview', '')[:100]}..."
            
            keyboard = [
                [
                    InlineKeyboardButton("📖 Read", callback_data=f"read_email_{data.get('id')}"),
                    InlineKeyboardButton("✍️ Reply", callback_data=f"reply_email_{data.get('id')}")
                ],
                [
                    InlineKeyboardButton("🗑️ Archive", callback_data=f"archive_email_{data.get('id')}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
        else:
            reply_markup = None
        
        await self.send_message(chat_id, text, reply_markup)
    
    def set_webhook(self, url: str):
        """Set webhook for receiving updates"""
        webhook_url = f"https://api.telegram.org/bot{self.bot_token}/setWebhook"
        
        response = requests.post(webhook_url, json={'url': url})
        return response.json()
    
    def delete_webhook(self):
        """Delete webhook"""
        webhook_url = f"https://api.telegram.org/bot{self.bot_token}/deleteWebhook"
        
        response = requests.post(webhook_url)
        return response.json()
    
    async def get_updates(self, offset: int = 0) -> List[Dict]:
        """Get updates using long polling"""
        if not self.bot:
            self.initialize_bot()
            
        updates = await self.bot.get_updates(offset=offset, timeout=30)
        
        return [update.to_dict() for update in updates]
    
    async def get_chat_info(self, chat_id: int) -> Dict:
        """Get information about a chat"""
        if not self.bot:
            self.initialize_bot()
            
        chat = await self.bot.get_chat(chat_id)
        
        return {
            'id': chat.id,
            'type': chat.type,
            'title': chat.title,
            'username': chat.username,
            'first_name': chat.first_name,
            'last_name': chat.last_name
        }
    
    async def send_daily_summary(self, chat_id: int, summary_data: Dict):
        """Send daily summary to user"""
        text = "📊 *Your Daily Summary*\n\n"
        
        # Email summary
        text += f"📧 *Email Activity*\n"
        text += f"• Received: {summary_data.get('emails_received', 0)}\n"
        text += f"• Auto-responded: {summary_data.get('emails_auto_responded', 0)}\n"
        text += f"• Awaiting response: {summary_data.get('emails_pending', 0)}\n\n"
        
        # SMS summary
        text += f"📱 *SMS Activity*\n"
        text += f"• Received: {summary_data.get('sms_received', 0)}\n"
        text += f"• Auto-responded: {summary_data.get('sms_auto_responded', 0)}\n\n"
        
        # Learning insights
        if summary_data.get('insights'):
            text += f"🧠 *Learning Insights*\n"
            for insight in summary_data['insights'][:3]:
                text += f"• {insight}\n"
        
        await self.send_message(chat_id, text)