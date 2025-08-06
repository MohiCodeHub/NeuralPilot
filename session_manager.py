import uuid
from collections import defaultdict

#Stores session id, and corresponding list of (user_msg,bot_msg) tuple pairs

SESSION_MEMORY = defaultdict(list)

def create_session():
    return str(uuid.uuid4())

def get_context(session_id):
    return SESSION_MEMORY[session_id]

def update_context(session_id, user_msg, bot_msg):
    SESSION_MEMORY[session_id].append((user_msg,bot_msg))

def clear_context(session_id):
    if session_id in SESSION_MEMORY:
        del SESSION_MEMORY[session_id]

