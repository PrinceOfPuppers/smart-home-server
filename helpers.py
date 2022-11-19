from queue import Queue

def clearQueue(q: Queue):
    with q.mutex:
        q.queue.clear()
