
import uuid
import time

class key():

    key_id: str
    timestamp: time

    def __init__(self):
        """
        Creates a new key with a own UUID and timestamp
        """

        self.key_id = str(uuid.uuid4())
        self.timestamp = time.time()

    def refresh(self):
        """
        Refreshes the timestamp of this key
        """

        self.timestamp = time.time()

    def has_expired(self, cur_time: time, lifetime: int):
        """
        Checks if this key has expired
        """

        return (cur_time - self.timestamp) > lifetime
