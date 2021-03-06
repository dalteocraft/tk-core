# Copyright (c) 2018 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Hook that gets executed when the current user is being retrieved.

Please note that this hook will only be called whenever Toolkit doesn't
have an authenticated user present. In releases prior to v0.16, this was the case
for all users and projects. However, as of Core v0.16 and above, projects are set
up to require users to log in by default, meaning that there already is a well
established notion of who the current user is.

Even with such projects, there are environments, e.g. render farms, where a user
cannot easily log in, and a Shotgun script user typically is being used for
"headless" operation of Toolkit. In these cases, Toolkit doesn't know which
Shotgun user is associated with the operation and this hook will be called.

The return value from this hook will then be compared with the available logins
for all users in Shotgun and if a match is found, this is deemed to be the
current user.
"""

from tank import Hook
import os
from tank.util import is_windows


class GetCurrentLogin(Hook):
    def execute(self, **kwargs):
        """
        Retrieves the login name for the Shotgun user.

        This is used by Toolkit to resolve against the ``login`` field in the
        Shotgun users table in order to extract further metadata.

        The default implementation will return the OS user's login name.

        :returns: A name that matches the user's ``login`` field in Shotgun.
        :rtype: str
        """
        if is_windows():
            # http://stackoverflow.com/questions/117014/how-to-retrieve-name-of-current-windows-user-ad-or-local-using-python
            return os.environ.get("USERNAME", None)
        else:
            try:
                import pwd

                pwd_entry = pwd.getpwuid(os.geteuid())
                return pwd_entry[0]
            except:
                return None
