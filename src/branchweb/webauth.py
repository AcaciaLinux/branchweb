import time
import uuid

from branchweb import webserver
from branchweb import usermanager

class web_auth():

    # key - timestamp of last access
    authorized_keys = [ ]

    # user, hash pair
    user_hash = { }

    # usermanager
    usermgr = None

    @staticmethod
    def setup_user_manager():
        web_auth.usermgr = usermanager.usermanager()
    
    #
    # clear out dead keys
    #
    @staticmethod
    def clear_dead_keys():
        webserver.debug("Clearing dead keys..")
        curr_time = time.time()

        revoked_keys = 0
        for k in web_auth.authorized_keys:
            # key has expired
            if((curr_time - k.timestamp) > webserver.WEB_CONFIG["key_timeout"]):
                web_auth.authorized_keys.remove(k)
                revoked_keys += 1
        
        webserver.debug("Cleared {} dead keys.".format(revoked_keys))

    #
    # check if a user / phash pair match
    #
    @staticmethod
    def validate_pw(user, phash):
        bhash = phash.encode("utf-8")
        user_obj = web_auth.usermgr.get_user(user)
        
        if(user_obj is None):
            webserver.debug("No such user.")
            return False

        return user_obj.validate_phash(phash) 


    #
    # returns a new key id, and authorizes the key object
    #
    @staticmethod
    def new_authorized_key():
        key_obj = key()

        webserver.debug("Authorizing key '{}', timestamp: {}".format(key_obj.key_id, key_obj.timestamp))
        web_auth.authorized_keys.append(key_obj)
        return key_obj
   
    #
    # check if a given key is valid
    #
    @staticmethod
    def validate_key(key_id):
        webserver.debug("Key validation requested.")
        web_auth.clear_dead_keys()
        
        key_obj = None

        # does key exist
        for k in web_auth.authorized_keys:
            if(str(k.key_id) == key_id):
                key_obj = k
                break
        
        if(key_obj is None):
            webserver.debug("Key validation failed. No such key found.")
            return False

        curr_time = time.time()

        # key has expired
        if((curr_time - key_obj.timestamp) > webserver.WEB_CONFIG["key_timeout"]):
            webserver.debug("Key validation failed. Key has expired.")
            web_auth.invalidate_key(key_obj.key_id)
            return False
        
        # key is valid
        key_obj.timestamp = time.time()
        webserver.debug("Key validation succeeded. Updating key timestamp: {}".format(key_obj.timestamp))
        return True

    #
    # method to invalidate a key
    #
    @staticmethod
    def invalidate_key(key_id):
        webserver.debug("Invalidating requested key")
        key_obj = None
        
        # does key exist
        for k in web_auth.authorized_keys:
            if(str(k.key_id) == key_id):
                key_obj = k
                break
        
        if(key_obj is None):
            webserver.debug("Key validation failed. No such key found.")
            return False

        web_auth.authorized_keys.remove(key_obj)
        webserver.debug("Key invalidated.")

class key():
    def __init__(self):
        self.key_id = uuid.uuid4();
        self.timestamp = time.time()

