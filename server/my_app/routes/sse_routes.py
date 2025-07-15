"""
Server-Sent Events routes for real-time updates and connection keep-alive
"""
import json
import time
import logging
import uuid
from flask import Blueprint, Response, request, session
from collections import defaultdict
from threading import Lock

logger = logging.getLogger(__name__)

# Create blueprint
sse_bp = Blueprint('sse', __name__)

# Active connections tracking
active_connections = defaultdict(set)
connections_lock = Lock()

# User activity tracking
user_activity = {}
activity_lock = Lock()


def track_user_activity(user_id: str):
    """Track user activity timestamp"""
    with activity_lock:
        user_activity[user_id] = time.time()


def get_active_users_count():
    """Get count of active users (active in last 5 minutes)"""
    with activity_lock:
        current_time = time.time()
        timeout = 300  # 5 minutes
        
        # Clean up old entries
        expired_users = [
            user_id for user_id, last_seen in user_activity.items()
            if current_time - last_seen > timeout
        ]
        for user_id in expired_users:
            del user_activity[user_id]
        
        return len(user_activity)


def generate_sse_event(event_type: str, data: dict):
    """Generate SSE formatted event"""
    event = f"event: {event_type}\n"
    event += f"data: {json.dumps(data)}\n\n"
    return event


@sse_bp.route('/sse/connect')
def sse_connect():
    """SSE endpoint for real-time updates"""
    
    # Get or create session ID
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    
    user_id = session['user_id']
    
    def generate():
        """Generator function for SSE stream"""
        connection_id = str(uuid.uuid4())
        
        # Track this connection
        with connections_lock:
            active_connections[user_id].add(connection_id)
        
        # Track user activity
        track_user_activity(user_id)
        
        try:
            # Send initial connection event
            yield generate_sse_event('connected', {
                'user_id': user_id,
                'active_users': get_active_users_count()
            })
            
            # Keep connection alive with periodic updates
            last_update = time.time()
            update_interval = 30  # Send update every 30 seconds
            
            while True:
                current_time = time.time()
                
                # Send periodic updates
                if current_time - last_update >= update_interval:
                    track_user_activity(user_id)
                    yield generate_sse_event('user_count', {
                        'active_users': get_active_users_count(),
                        'timestamp': current_time
                    })
                    last_update = current_time
                
                # Send heartbeat to keep connection alive
                yield generate_sse_event('heartbeat', {
                    'timestamp': current_time
                })
                
                time.sleep(15)  # Send heartbeat every 15 seconds
                
        except GeneratorExit:
            # Clean up when connection closes
            with connections_lock:
                active_connections[user_id].discard(connection_id)
                if not active_connections[user_id]:
                    del active_connections[user_id]
            logger.info(f"SSE connection closed for user {user_id}")
    
    response = Response(generate(), mimetype='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['X-Accel-Buffering'] = 'no'  # Disable Nginx buffering
    return response


@sse_bp.route('/sse/upload-progress', methods=['POST'])
def report_upload_progress():
    """Endpoint to report upload progress (keeps connection alive during uploads)"""
    
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    
    user_id = session['user_id']
    track_user_activity(user_id)
    
    data = request.json
    progress = data.get('progress', 0)
    status = data.get('status', 'uploading')
    
    return json.dumps({
        'success': True,
        'user_id': user_id,
        'active_users': get_active_users_count()
    })


@sse_bp.route('/api/active-users')
def get_active_users():
    """Simple endpoint to get active users count"""
    
    # Track this request as user activity
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    
    user_id = session['user_id']
    track_user_activity(user_id)
    
    return json.dumps({
        'active_users': get_active_users_count(),
        'timestamp': time.time()
    })
