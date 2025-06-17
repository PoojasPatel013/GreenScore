from flask_socketio import SocketIO, emit
from typing import Dict, Any
import json

class SocketService:
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.connected_clients = set()
        
    def emit_leaderboard_update(self, user_id: str, data: Dict[str, Any]):
        """Emit leaderboard update to all connected clients"""
        emit('leaderboard_update', data, broadcast=True)
        
    def emit_user_update(self, user_id: str, data: Dict[str, Any]):
        """Emit user-specific update to specific client"""
        emit('user_update', data, room=user_id)
        
    def emit_achievement(self, user_id: str, achievement: Dict[str, Any]):
        """Emit achievement notification to user"""
        emit('new_achievement', achievement, room=user_id)
        
    def on_connect(self, user_id: str):
        """Handle client connection"""
        self.connected_clients.add(user_id)
        
    def on_disconnect(self, user_id: str):
        """Handle client disconnection"""
        self.connected_clients.discard(user_id)
        
    def broadcast_message(self, message: str, data: Dict[str, Any]):
        """Broadcast a message to all connected clients"""
        emit(message, data, broadcast=True)
        
    def emit_event_notification(self, user_id: str, event: Dict[str, Any]):
        """Emit event notification to user"""
        emit('new_event', event, room=user_id)
        
    def emit_level_up(self, user_id: str, level: int):
        """Emit level up notification to user"""
        emit('level_up', {'level': level}, room=user_id)
        
    def emit_points_update(self, user_id: str, points: int):
        """Emit points update to user"""
        emit('points_update', {'points': points}, room=user_id)
