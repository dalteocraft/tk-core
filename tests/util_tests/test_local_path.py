# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from __future__ import with_statement

import os
import sys
import copy

from tank_test.tank_test_base import *
from tank import TankError
from tank.util import LocalFileStorageManager

class TestLocalFileStorage(TankTestBase):
    """
    tests the ShotgunPath class
    """

    def setUp(self):
        super(TestLocalFileStorage, self).setUp()

    def test_global(self):
        """
        tests the global root
        """
        pref_path = LocalFileStorageManager.get_global_root(LocalFileStorageManager.PREFERENCES)
        cache_path = LocalFileStorageManager.get_global_root(LocalFileStorageManager.CACHE)
        persistent_path = LocalFileStorageManager.get_global_root(LocalFileStorageManager.PERSISTENT)
        log_path = LocalFileStorageManager.get_global_root(LocalFileStorageManager.LOGGING)

        if sys.platform == "darwin":
            self.assertEqual(cache_path, os.path.expanduser("~/Library/Caches/Shotgun"))
            self.assertEqual(pref_path, os.path.expanduser("~/Library/Preferences/Shotgun"))
            self.assertEqual(persistent_path, os.path.expanduser("~/Library/Application Support/Shotgun"))
            self.assertEqual(log_path, os.path.expanduser("~/Library/Logs/Shotgun"))

        elif sys.platform == "win32":
            app_data = os.environ.get("APPDATA", "APPDATA_NOT_SET")
            self.assertEqual(cache_path, os.path.join(app_data, "Shotgun"))
            self.assertEqual(pref_path, os.path.join(app_data, "Shotgun", "Preferences"))
            self.assertEqual(persistent_path, os.path.join(app_data, "Shotgun", "Data"))
            self.assertEqual(log_path, os.path.join(app_data, "Shotgun", "Logs"))

        else:
            # linux
            self.assertEqual(cache_path, os.path.expanduser("~/.shotgun"))
            self.assertEqual(pref_path, os.path.expanduser("~/.shotgun/preferences"))
            self.assertEqual(persistent_path, os.path.expanduser("~/.shotgun/data"))
            self.assertEqual(log_path, os.path.expanduser("~/.shotgun/logs"))

    def test_legacy_global(self):
        """
        tests the global root, 0.17 style
        """
        cache_path = LocalFileStorageManager.get_global_root(LocalFileStorageManager.CACHE, LocalFileStorageManager.CORE_V17)
        persistent_path = LocalFileStorageManager.get_global_root(LocalFileStorageManager.PERSISTENT, LocalFileStorageManager.CORE_V17)
        log_path = LocalFileStorageManager.get_global_root(LocalFileStorageManager.LOGGING, LocalFileStorageManager.CORE_V17)

        if sys.platform == "darwin":
            self.assertEqual(cache_path, os.path.expanduser("~/Library/Caches/Shotgun"))
            self.assertEqual(persistent_path, os.path.expanduser("~/Library/Application Support/Shotgun"))
            self.assertEqual(log_path, os.path.expanduser("~/Library/Logs/Shotgun"))

        elif sys.platform == "win32":
            app_data = os.environ.get("APPDATA", "APPDATA_NOT_SET")
            self.assertEqual(cache_path, os.path.join(app_data, "Shotgun"))
            self.assertEqual(persistent_path, os.path.join(app_data, "Shotgun"))
            self.assertEqual(log_path, os.path.join(app_data, "Shotgun"))

        else:
            # linux
            self.assertEqual(cache_path, os.path.expanduser("~/.shotgun"))
            self.assertEqual(persistent_path, os.path.expanduser("~/.shotgun"))
            self.assertEqual(log_path, os.path.expanduser("~/.shotgun"))

    def test_site(self):
        """
        tests the site config root
        """

        with self.assertRaises(TankError):
            LocalFileStorageManager.get_site_root(None, LocalFileStorageManager.CACHE)

        new_path_types = [
            LocalFileStorageManager.PREFERENCES,
            LocalFileStorageManager.CACHE,
            LocalFileStorageManager.PERSISTENT,
            LocalFileStorageManager.LOGGING
        ]

        for path_type in new_path_types:

            cache_path = LocalFileStorageManager.get_site_root(
                "https://test.shotgunstudio.com",
                path_type
            )

            self.assertEqual(
                cache_path,
                os.path.join(LocalFileStorageManager.get_global_root(path_type), "test")
            )

            cache_path = LocalFileStorageManager.get_site_root(
                "http://shotgun",
                path_type
            )

            self.assertEqual(
                cache_path,
                os.path.join(LocalFileStorageManager.get_global_root(path_type), "shotgun")
            )

            cache_path = LocalFileStorageManager.get_site_root(
                "https://shotgun.int",
                path_type
            )

            self.assertEqual(
                cache_path,
                os.path.join(LocalFileStorageManager.get_global_root(path_type), "shotgun.int")
            )

        old_path_types = [
            LocalFileStorageManager.CACHE,
            LocalFileStorageManager.PERSISTENT,
            LocalFileStorageManager.LOGGING
        ]

        for path_type in old_path_types:

            cache_path = LocalFileStorageManager.get_site_root(
                "https://test.shotgunstudio.com",
                path_type,
                LocalFileStorageManager.CORE_V17
            )

            self.assertEqual(
                cache_path,
                os.path.join(
                    LocalFileStorageManager.get_global_root(path_type, LocalFileStorageManager.CORE_V17),
                    "test.shotgunstudio.com"
                )
            )

            cache_path = LocalFileStorageManager.get_site_root(
                "http://shotgun",
                path_type,
                LocalFileStorageManager.CORE_V17
            )

            self.assertEqual(
                cache_path,
                os.path.join(
                    LocalFileStorageManager.get_global_root(path_type, LocalFileStorageManager.CORE_V17),
                    "shotgun"
                )
            )

            cache_path = LocalFileStorageManager.get_site_root(
                "https://shotgun.int",
                path_type,
                LocalFileStorageManager.CORE_V17
            )

            self.assertEqual(
                cache_path,
                os.path.join(
                    LocalFileStorageManager.get_global_root(
                        path_type,
                        LocalFileStorageManager.CORE_V17
                    ),
                    "shotgun.int"
                )
            )

    def _compute_config_root(self, project_id, entry_point, pc_id, expected_suffix):

        hostname = "http://test.shotgunstudio.com"

        path_types = [
            LocalFileStorageManager.PREFERENCES,
            LocalFileStorageManager.CACHE,
            LocalFileStorageManager.PERSISTENT,
            LocalFileStorageManager.LOGGING
        ]

        for path_type in path_types:
            root = LocalFileStorageManager.get_configuration_root(
                hostname,
                project_id,
                entry_point,
                pc_id,
                path_type
            )

            site_root = LocalFileStorageManager.get_site_root(hostname, path_type)

            self.assertEqual(root, os.path.join(site_root, expected_suffix))


    def test_config_root(self):
        """
        tests logic for config root computations
        """

        self._compute_config_root(
            project_id=123,
            entry_point=None,
            pc_id=1234,
            expected_suffix="p123c1234"
        )

        self._compute_config_root(
            project_id=None,
            entry_point="foo",
            pc_id=None,
            expected_suffix="site.foo"
        )

        self._compute_config_root(
            project_id=None,
            entry_point="foo",
            pc_id=1234,
            expected_suffix="sitec1234"
        )

        self._compute_config_root(
            project_id=123,
            entry_point="foo",
            pc_id=1234,
            expected_suffix="p123c1234"
        )

        self._compute_config_root(
            project_id=123,
            entry_point="flame",
            pc_id=None,
            expected_suffix="p123.flame"
        )


    def _compute_legacy_config_root(self, project_id, entry_point, pc_id, expected_suffix):

        hostname = "http://test.shotgunstudio.com"

        path_types = [
            LocalFileStorageManager.CACHE,
            LocalFileStorageManager.PERSISTENT,
            LocalFileStorageManager.LOGGING
        ]

        for path_type in path_types:
            root = LocalFileStorageManager.get_configuration_root(
                hostname,
                project_id,
                entry_point,
                pc_id,
                path_type,
                LocalFileStorageManager.CORE_V17
            )

            site_root = LocalFileStorageManager.get_site_root(hostname, path_type, LocalFileStorageManager.CORE_V17)

            self.assertEqual(root, os.path.join(site_root, expected_suffix))


    def test_legacy_config_root(self):
        """
        tests logic for legacy config root computations
        """

        self._compute_legacy_config_root(
            project_id=123,
            entry_point=None,
            pc_id=1234,
            expected_suffix=os.path.join("project_123", "config_1234")
        )

        self._compute_legacy_config_root(
            project_id=None,
            entry_point="foo",
            pc_id=None,
            expected_suffix=os.path.join("project_0", "config_None")
        )

        self._compute_legacy_config_root(
            project_id=None,
            entry_point="foo",
            pc_id=1234,
            expected_suffix=os.path.join("project_0", "config_1234")
        )

        self._compute_legacy_config_root(
            project_id=123,
            entry_point="foo",
            pc_id=1234,
            expected_suffix=os.path.join("project_123", "config_1234")
        )

        self._compute_legacy_config_root(
            project_id=123,
            entry_point="flame",
            pc_id=None,
            expected_suffix=os.path.join("project_123", "config_None")
        )
