
broadcasts = []

def broadcast(message):
    global broadcasts
    for msg in broadcasts:
        if msg == message: return

    broadcasts.append(message)


def contains(message):
    global broadcasts
    for msg in broadcasts:
        if msg == message: return True
    
    return False

def remove(message):
    global broadcasts
    for msg in broadcasts:
        if msg == message: broadcasts.remove(msg)