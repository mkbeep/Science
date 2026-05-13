"""
Alerting Module - Send notifications about crawler status
Supports webhook notifications (Slack, Discord, custom endpoints)
"""

import os
import requests
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Configuration from environment
ALERT_WEBHOOK_URL = os.getenv('ALERT_WEBHOOK_URL', '')
ALERT_WEBHOOK_TOKEN = os.getenv('ALERT_WEBHOOK_TOKEN', '')

def send_webhook_alert(
    status: str,
    message: str,
    details: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Send alert via webhook
    
    Args:
        status: 'success', 'warning', or 'error'
        message: Alert message
        details: Additional details
        
    Returns:
        True if sent successfully, False otherwise
    """
    
    if not ALERT_WEBHOOK_URL:
        logger.debug("No webhook URL configured, skipping alert")
        return False
    
    # Prepare payload
    payload = {
        'timestamp': datetime.now().isoformat(),
        'status': status,
        'message': message,
        'service': 'IT Jobs Crawler',
        'details': details or {}
    }
    
    # Add emoji based on status
    emoji_map = {
        'success': '✅',
        'warning': '⚠️',
        'error': '❌'
    }
    emoji = emoji_map.get(status, '📊')
    
    # Format for Slack/Discord
    slack_payload = {
        'text': f"{emoji} **{payload['service']}**",
        'attachments': [{
            'color': 'good' if status == 'success' else ('warning' if status == 'warning' else 'danger'),
            'fields': [
                {'title': 'Status', 'value': status.upper(), 'short': True},
                {'title': 'Time', 'value': payload['timestamp'], 'short': True},
                {'title': 'Message', 'value': message, 'short': False}
            ]
        }]
    }
    
    # Add details if present
    if details:
        for key, value in details.items():
            slack_payload['attachments'][0]['fields'].append({
                'title': key.replace('_', ' ').title(),
                'value': str(value),
                'short': True
            })
    
    try:
        headers = {'Content-Type': 'application/json'}
        
        # Add auth token if configured
        if ALERT_WEBHOOK_TOKEN:
            headers['Authorization'] = f'Bearer {ALERT_WEBHOOK_TOKEN}'
        
        response = requests.post(
            ALERT_WEBHOOK_URL,
            json=slack_payload,
            headers=headers,
            timeout=10
        )
        
        response.raise_for_status()
        logger.info(f"✅ Alert sent successfully: {status}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to send alert: {e}")
        return False

def notify_crawl_success(new_jobs: int, updated_jobs: int, total_jobs: int):
    """Notify successful crawl completion"""
    send_webhook_alert(
        status='success',
        message=f'Crawl completed successfully',
        details={
            'new_jobs': new_jobs,
            'updated_jobs': updated_jobs,
            'total_jobs': total_jobs
        }
    )

def notify_crawl_warning(message: str, details: Optional[Dict[str, Any]] = None):
    """Notify crawl warning"""
    send_webhook_alert(
        status='warning',
        message=message,
        details=details
    )

def notify_crawl_error(error: str, details: Optional[Dict[str, Any]] = None):
    """Notify crawl error"""
    send_webhook_alert(
        status='error',
        message=f'Crawl failed: {error}',
        details=details
    )


def notify_webhook(
    message: str,
    severity: str = 'info',
    extra: Optional[Dict[str, Any]] = None
):
    """
    Simplified webhook notification
    
    Args:
        message: Notification message
        severity: 'info', 'warning', or 'error'
        extra: Additional data
    """
    status_map = {
        'info': 'success',
        'warning': 'warning',
        'error': 'error'
    }
    
    status = status_map.get(severity, 'success')
    details = extra or {}
    
    send_webhook_alert(status, message, details)
