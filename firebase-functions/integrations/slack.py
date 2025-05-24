"""
Slack Integration for Agentic Persona
Handles Slack message reading and automated responses
"""

import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.oauth import AuthorizeUrlGenerator
from slack_sdk.oauth.state_store import FileOAuthStateStore

class SlackIntegration:
    def __init__(self):
        self.client_id = os.environ.get('SLACK_CLIENT_ID')
        self.client_secret = os.environ.get('SLACK_CLIENT_SECRET')
        self.redirect_uri = os.environ.get('SLACK_REDIRECT_URI')
        self.scopes = [
            "channels:history",
            "channels:read",
            "chat:write",
            "groups:history",
            "groups:read",
            "im:history",
            "im:read",
            "mpim:history",
            "mpim:read",
            "users:read"
        ]
        self.state_store = FileOAuthStateStore(expiration_seconds=600)
    
    def get_auth_url(self, state: str) -> str:
        """Generate Slack OAuth authorization URL"""
        authorize_url_generator = AuthorizeUrlGenerator(
            client_id=self.client_id,
            scopes=self.scopes,
            redirect_uri=self.redirect_uri
        )
        
        return authorize_url_generator.generate(state=state)
    
    def exchange_code(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        token_response = requests.post(
            "https://slack.com/api/oauth.v2.access",
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": code,
                "redirect_uri": self.redirect_uri
            }
        )
        
        token_data = token_response.json()
        
        if not token_data.get("ok"):
            raise Exception(f"Failed to exchange code: {token_data.get('error')}")
        
        return {
            "access_token": token_data["access_token"],
            "team": token_data["team"],
            "user_id": token_data["authed_user"]["id"],
            "bot_user_id": token_data.get("bot_user_id")
        }
    
    def get_client(self, access_token: str) -> WebClient:
        """Create Slack WebClient instance"""
        return WebClient(token=access_token)
    
    def get_recent_messages(
        self, 
        client: WebClient, 
        channel_types: List[str] = ["public_channel", "private_channel", "im"],
        hours_back: int = 24
    ) -> List[Dict]:
        """Fetch recent messages from specified channel types"""
        messages = []
        
        try:
            # Get all conversations
            conversations = client.conversations_list(
                types=",".join(channel_types),
                exclude_archived=True
            )
            
            # Calculate time range
            oldest = (datetime.now() - timedelta(hours=hours_back)).timestamp()
            
            for channel in conversations["channels"]:
                channel_id = channel["id"]
                channel_name = channel.get("name", channel.get("user", "Direct Message"))
                
                try:
                    # Get messages from channel
                    result = client.conversations_history(
                        channel=channel_id,
                        oldest=str(oldest),
                        limit=100
                    )
                    
                    for msg in result["messages"]:
                        # Skip bot messages and thread replies
                        if msg.get("bot_id") or msg.get("thread_ts"):
                            continue
                        
                        # Get user info
                        user_info = self._get_user_info(client, msg.get("user"))
                        
                        messages.append({
                            "channel_id": channel_id,
                            "channel_name": channel_name,
                            "message_id": msg["ts"],
                            "user_id": msg.get("user"),
                            "user_name": user_info.get("name", "Unknown"),
                            "text": msg.get("text", ""),
                            "timestamp": msg["ts"],
                            "datetime": datetime.fromtimestamp(float(msg["ts"])).isoformat(),
                            "is_mention": self._check_mention(msg.get("text", ""))
                        })
                    
                except SlackApiError as e:
                    print(f"Error fetching messages from {channel_name}: {e}")
            
            # Sort by timestamp
            messages.sort(key=lambda x: x["timestamp"], reverse=True)
            
            return messages
            
        except SlackApiError as e:
            print(f"Error fetching conversations: {e}")
            return []
    
    def _get_user_info(self, client: WebClient, user_id: str) -> Dict:
        """Get user information"""
        if not user_id:
            return {}
        
        try:
            result = client.users_info(user=user_id)
            user = result["user"]
            return {
                "name": user.get("real_name", user.get("name", "Unknown")),
                "email": user.get("profile", {}).get("email"),
                "is_bot": user.get("is_bot", False)
            }
        except SlackApiError:
            return {"name": "Unknown"}
    
    def _check_mention(self, text: str) -> bool:
        """Check if message contains a mention"""
        return "<@" in text
    
    def send_message(
        self, 
        client: WebClient, 
        channel: str, 
        text: str,
        thread_ts: Optional[str] = None
    ) -> Dict:
        """Send a message to a Slack channel"""
        try:
            result = client.chat_postMessage(
                channel=channel,
                text=text,
                thread_ts=thread_ts
            )
            
            return {
                "success": True,
                "channel": result["channel"],
                "ts": result["ts"]
            }
            
        except SlackApiError as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_reply(
        self,
        client: WebClient,
        channel: str,
        thread_ts: str,
        text: str
    ) -> Dict:
        """Send a threaded reply"""
        return self.send_message(client, channel, text, thread_ts)
    
    def add_reaction(
        self,
        client: WebClient,
        channel: str,
        timestamp: str,
        emoji: str
    ) -> bool:
        """Add a reaction to a message"""
        try:
            client.reactions_add(
                channel=channel,
                timestamp=timestamp,
                name=emoji
            )
            return True
        except SlackApiError:
            return False
    
    def get_im_channels(self, client: WebClient) -> List[Dict]:
        """Get all direct message channels"""
        try:
            result = client.conversations_list(types="im")
            
            channels = []
            for channel in result["channels"]:
                user_info = self._get_user_info(client, channel.get("user"))
                channels.append({
                    "id": channel["id"],
                    "user_id": channel.get("user"),
                    "user_name": user_info.get("name", "Unknown"),
                    "is_open": channel.get("is_open", False)
                })
            
            return channels
            
        except SlackApiError as e:
            print(f"Error fetching IM channels: {e}")
            return []
    
    def set_presence(self, client: WebClient, presence: str = "auto") -> bool:
        """Set user presence (auto or away)"""
        try:
            client.users_setPresence(presence=presence)
            return True
        except SlackApiError:
            return False
    
    def get_workspace_info(self, client: WebClient) -> Dict:
        """Get workspace information"""
        try:
            result = client.team_info()
            team = result["team"]
            
            return {
                "id": team["id"],
                "name": team["name"],
                "domain": team["domain"],
                "icon": team.get("icon", {}).get("image_88")
            }
            
        except SlackApiError as e:
            print(f"Error fetching workspace info: {e}")
            return {}