USER_FILE = "users.meta"

import secrets
import os
import string
import bcrypt

from .user import user
from . import webserver

#
# usermanager class
# 
class usermanager():

    users: list[user] = [ ]
    userfile: str = ""

    def __init__(self, user_file: str = USER_FILE):
        """
        Creates a new usermanager and reads or creates the userfile

        Args
        ----
            user_file (str, optional): The path to the userfile. Defaults to USER_FILE.
        """

        webserver.debug("Initializing new user manager with userfile at {}".format(user_file))

        self.userfile = user_file
        self.read_file(user_file)

    def get_user(self, name: str) -> user:
        """
        Retrieves a user with the provided username

        Args
        ----
            name (str): The username to search for

        Returns
        -------
        The user object or None if the user is not registered
        """

        for u in self.users:
            if(u.name == name):
                return u

        return None

    def get_key_user(self, key_id: str) -> user:
        """
        Returns the user that matches the supplied key_id

        Args
        ----
            key_id (str): The key id (UUID) that was generated when user.authenticate() was called

        Returns
        -------
        The user object or None if the key has not been authenticated
        """

        for u in self.users:
            if (u.has_authkey(key_id)):
                return u

        return None

    def revoke_authkey(self, key_id: str) -> user:
        """
        Revokes the supplied authkey

        Args
        ----
            key_id (str): The key is (UUID) to be revoked

        Returns
        -------
        The user that owned the authkey, None if the key was never valid
        """

        user = self.get_key_user(key_id)

        if (user is None):
            return None

        if (not user.revoke_authkey(key_id)):
            return None

        return user

    # add a user
    def add_user(self, username: str, password: str) -> bool:
        """
        Adds a user with the provided username and password to them manager

        Args
        ----
            username (str): The username to allocate
            password (str): The password to use

        Returns
        -------
        True, False if the username is already taken
        """

        for u in self.users:
            if(u.name == username):
                return False

        user_obj = user(username, password)
        self.users.append(user_obj)

        webserver.debug("New user {}: updating file..".format(username))
        self.write_file(self.userfile)

        return True

    def write_file(self, user_file_path: str = ""):
        """
        Writes out the current users to the (optionally) provided path

        Args
        ----
            user_file_path (str, optional): The file to write into. Defaults to the userfile supplied to the constructor.
        """

        if (user_file_path == ""):
            user_file_path = self.userfile

        webserver.debug("Writing userfile to {}".format(user_file_path))
        user_file = open(user_file_path, "w")

        for u in self.users:
            user_file.write("{}={}\n".format(u.name, u.phash))

    def read_file(self, user_file_path: str):
        """
        Reads the userfile from the supplied path or creates it with a new root user

        Args
        ----
            user_file_path (str): The file to read or create
        """

        if(not os.path.exists(user_file_path)):
            self.create_userfile(user_file_path)

        webserver.debug("Reading user file from {}".format(user_file_path))

        user_file = open(user_file_path, "r")
        user_file_arr = user_file.read().split("\n")

        for userl in user_file_arr:
            if(len(userl) == 0):
                continue

            # skip comments
            if(userl[0] == '#'):
                continue

            user_arr = userl.split("=")
            usern = user_arr[0]
            phash = user_arr[1]

            self.users.append(user.from_pw_hash(usern, phash))

    def create_userfile(self, user_file_path: str):
        """
        Creates a new userfile with a root user and random password

        Args
        ----
            user_file_path (str): The userfile to create
        """

        webserver.info("Creating new userfile at {}".format(user_file_path))
        user_file = open(user_file_path, "w")

        generator_chars = string.ascii_letters + string.digits + string.punctuation

        pwd = ""
        for i in range(16):
            pwd += "".join(secrets.choice(generator_chars))

        webserver.info("============================")
        webserver.info("!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        webserver.info("NEW ROOT PASSWORD GENERATED!")
        webserver.info("!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        webserver.info("Password: {}".format(pwd))
        webserver.info("============================")

        byte_array = pwd.encode("utf-8")
        salt = bcrypt.gensalt()
        phash = bcrypt.hashpw(byte_array, salt)

        user_file.write("root={}\n".format(phash.decode("utf-8")))
        user_file.close()
