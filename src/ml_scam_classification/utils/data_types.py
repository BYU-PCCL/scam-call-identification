from queue import Queue

def fn_applied_to_queue_els_ret_all_true(q: Queue, fn):
    size = q.qsize()
    for _ in range(size):
        item = q.get()
        if not fn(item):
            # put item back if you want to preserve queue
            q.put(item)
            # restore remaining items
            for _ in range(size - 1):
                q.put(q.get())
            return False
        q.put(item)  # requeue item if preserving
    return True