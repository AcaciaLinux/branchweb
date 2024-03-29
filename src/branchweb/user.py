
import bcrypt
import time

from .key import key

#
# user class
#
class user():

    def __init__(self, name: str, passwd :str = None):
        """
        Creates a new user

        Args
        ----
            name (str): The username for the user
            passwd (str, optional): The password in plaintext
        """

        self.name: str = name
        self.phash: str = ""
        self.authkeys: dict[str, key] = {}

        if (passwd is not None):
            byte_array = passwd.encode("utf-8")
            salt = bcrypt.gensalt()
            passwdhash = bcrypt.hashpw(byte_array, salt)

            self.phash = passwdhash.decode("utf-8")

    @staticmethod
    def from_pw_hash(name: str, phash: str) -> super:
        """
        Constructs a new user with the supplied hash instead of the password

        Args
        ----
            name (str): The username
            phash (str): The password hash

        Returns:
        A user instance
        """

        u = user(name)
        u.phash = phash

        return u

    def set_password(self, passwd: str):
        """
        Sets a new password for this user

        Args
        ----
            passwd (str): The new password to set
        """

        byte_array = passwd.encode("utf-8")
        salt = bcrypt.gensalt()
        passwdhash = bcrypt.hashpw(byte_array, salt)

        self.phash = passwdhash.decode("utf-8")

    def authenticate(self, passwd: str) -> key:
        """
        Checks if the supplied password is valid for the user and returns an authkey

        Args
        ----
            passwd: (str): The password to validate

        Returns
        -------
        The new authkey or None on failure
        """

        if (bcrypt.checkpw(passwd.encode("utf-8"), self.phash.encode("utf-8"))):
            newkey = key()
            self.authkeys[newkey.key_id] = newkey
            print("User {} authenticated for key {}".format(self.name, newkey.key_id))
            return newkey
        else:
            return None

    def has_authkey(self, authkey: str) -> bool:
        """
        Checks if the supplied authkey is valid for this user

        Args
        ----
            authke (str): The authkey to check

        Returns
        -------
        true or false
        """

        return authkey in self.authkeys.keys()

    def revoke_authkey(self, authkey: str) -> bool:
        """
        Revokes a previously handed out authkey

        Args
        ----
            authkey (str): The key to revoke

        Returns
        -------
        True, False if the key was never handed out
        """

        if (not self.has_authkey(authkey)):
            return False

        del self.authkeys[authkey]

        return True

    def clean_dangling_keys(self, cur_time: time, lifetime: int) -> int:
        """
        Checks for dangling keys in this user and revokes them

        Args
        ----
            cur_time (time): The time to check against (the current time)
            lifetime (int): The lifetime of keys in seconds

        Returns
        -------
        The amount of keys revoked
        """

        revoked_keys = 0

        for (hash, key) in self.authkeys:
            if (key.has_expired(cur_time, lifetime)):
                self.revoke_authkey(hash)
                revoked_keys = revoked_keys + 1

        return revoked_keys
