# Standard Library
from queue import Full, Queue
from typing import Dict, List


class PubSub:
    def __init__(self) -> None:
        self.listeners: Dict[str, List[Queue]] = {}

    def listen(self, event: str = ""):
        q: Queue = Queue(maxsize=5)
        if not event in self.listeners:
            self.listeners[event] = []
        self.listeners[event].append(q)

        while True:  # q in self.listeners[event]:
            msg = q.get()  # blocks until a new message arrives
            yield msg

    def publish(self, msg, event: str = ""):
        if not event in self.listeners:
            return
        for i in reversed(range(len(self.listeners[event]))):
            try:
                self.listeners[event][i].put_nowait(msg)
            except Full:
                del self.listeners[event][i]
