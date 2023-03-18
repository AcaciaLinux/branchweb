
import bcrypt

from .key import key

#
# user class
#
class user():

    name: str = ""
    phash: str = ""
    authkeys: dict[str, key] = { }

    def __init__(self, name: str, passwd :str):
        """
        Creates a new user

        Args
        ----
            name (str): The username for the user
            passwd (str): The password in plaintext
        """

        self.name = name

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

        u = user(name, "")
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
