import time

_last_action = {}

def can_proceed(user_id, cooldown):
    now = time.time()
    last = _last_action.get(user_id, 0)

    if now - last < cooldown:
        return False

    _last_action[user_id] = now
    return True
	

