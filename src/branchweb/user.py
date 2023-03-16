
import bcrypt

from .key import key

#
# user class
#
class user():

    name: str = ""
    phash: str = ""
    authkeys: dict[str, key] = { }

    def __init__(self, name: str, phash :str):
        """
        Creates a new user

        Args:
            name (str): The username for the user
            phash (str): The password hash
        """

        self.name = name
        self.phash = phash

    def authenticate(self, chash: str) -> key:
        """
        Checks if the supplied hash is valid for the user

        Returns
        -------
        The new authkey or None on failure
        """

        if (bcrypt.checkpw(chash.encode("utf-8"), self.phash.encode("utf-8"))):
            newkey = key()
            self.authkeys[newkey.key_id] = newkey
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

        return authkey in self.authkeys

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
