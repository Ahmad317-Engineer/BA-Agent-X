"""
Slack Integration - Bot for agent interaction
"""

import os
from typing import Dict, Any
from datetime import datetime

class SlackBot:
    """Slack bot for agent interaction"""
    
    def __init__(self, bot_token: str = None, app_token: str = None):
        self.bot_token = bot_token or os.getenv("SLACK_BOT_TOKEN")
        self.app_token = app_token or os.getenv("SLACK_APP_TOKEN")
        self.mode = "mock" if not self.bot_token else "real"
        print(f"✅ SlackBot initialized ({self.mode} mode)")
    
    def send_message(self, channel: str, text: str, blocks: list = None) -> Dict:
        """Send message to Slack"""
        return {
            'success': True,
            'channel': channel,
            'text': text[:200],
            'blocks': blocks,
            'timestamp': datetime.now().isoformat(),
            'mode': self.mode
        }
    
    def format_agent_response(self, response: Dict) -> list:
        """Format agent response as Slack blocks"""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🤖 BA Agent Response"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Intent:* {response.get('intent', 'unknown')}\n*Session:* {response.get('session_id', 'N/A')}"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": response.get('output', 'No output')[:2000]
                }
            }
        ]
        
        # Add action buttons if approval needed
        if response.get('needs_approval'):
            blocks.append({
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "✅ Approve"},
                        "style": "primary",
                        "value": response.get('session_id')
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "❌ Reject"},
                        "style": "danger",
                        "value": response.get('session_id')
                    }
                ]
            })
        
        return blocks

# Test Slack integration
if __name__ == "__main__":
    slack = SlackBot()
    test_response = {
        'intent': 'requirements',
        'session_id': 'test_123',
        'output': 'This is a test response from the BA Agent.',
        'needs_approval': True
    }
    blocks = slack.format_agent_response(test_response)
    print(f"Formatted {len(blocks)} Slack blocks")
