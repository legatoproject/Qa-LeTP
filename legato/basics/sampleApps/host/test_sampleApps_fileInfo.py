r"""!FileInfo Sample apps test.

Set of functions to test the fileInfo sample apps.

@package fileInfoAppsModule
@file
\ingroup sampleAppTests
"""
import os

import pytest

from pytest_letp.lib import swilog

__copyright__ = "Copyright (C) Sierra Wireless Inc."
# ====================================================================================
# Constants and Globals
# ====================================================================================
# Determine the resources folder (legato apps)
LEGATO_ROOT = os.environ["LEGATO_ROOT"]

APP_NAME = "fileInfo"
APP_PATH = "%s/apps/sample/commandLine/" % LEGATO_ROOT
APP_SANDBOX_PATH = "/legato/systems/current/appsWriteable/%s" % APP_NAME


# ====================================================================================
# Functions
# ====================================================================================
def help_test(target, flag):
    """!Check the 'help' command.

    @param target: fixture to communicate with the target
    @param flag: fixture to provide option
    """
    stdout = target.run(
        "cd %s/bin/; ./%s %s" % (APP_SANDBOX_PATH, APP_NAME, flag), check=False
    )
    assert "Print a help message and exit. Ignore all other " "arguments." in stdout, (
        "[FAILED] Could not find " "help message output (%s)" % flag
    )
    swilog.info("[PASSED] Successfully found the help message output (%s)" % flag)


def permissions_test(target, owner_permissions, group_permissions, others_permissions):
    """!Change the file permissions.

    @param target: fixture to communicate with the target
    @param owner_permissions: fixture to provide owner permissions
    @param group_permissions: fixture to provide group permissions
    @param others_permissions: fixture to provide others permissions
    """
    stdout = target.run(
        "cd %s/bin/; ./%s -mc 2 permissions %s/testFile1"
        % (APP_SANDBOX_PATH, APP_NAME, APP_SANDBOX_PATH)
    )
    text = "the owner can %s, group members can %s, and others can %s." % (
        owner_permissions,
        group_permissions,
        others_permissions,
    )
    assert text in stdout, (
        "[FAILED] Did not find correct permissions for "
        "all groups (owner: %s, group: %s, others: %s)"
        % (owner_permissions, group_permissions, others_permissions)
    )

    swilog.info(
        "[PASSED] Successfully found correct permissions for all "
        "groups (owner: %s, group: %s, others: %s)"
        % (owner_permissions, group_permissions, others_permissions)
    )


def type_test(target, path, type_test):
    """!Check the 'type' command.

    @param target: fixture to communicate with the target
    @param path: fixture to get path of sandbox app
    @param type_test: fixture to provide type test
    """
    stdout = target.run(
        "cd %s/bin/; ./%s -mc 2 type %s" % (APP_SANDBOX_PATH, APP_NAME, path),
        check=False,
    )
    assert "is a %s." % type_test in stdout, (
        "[FAILED] Did not find correct " "type (%s)" % type_test
    )
    swilog.info("[PASSED] Successfully found correct type (%s)" % type_test)


def extreme_test(target, flag):
    """!Check the 'extreme' flag.

    @param target: fixture to communicate with the target
    @param flag: fixture to provide flag
    """
    stdout = target.run(
        "cd %s/bin/; ./%s -mc 2 %s permissions %s/testFile1"
        % (APP_SANDBOX_PATH, APP_NAME, flag, APP_SANDBOX_PATH),
        check=False,
    )
    swilog.step(stdout)
    error_msg = "[FAILED] Did not find response for extreme flag (%s)" % flag
    assert (
        "the owner can read, group members can read, and others can "
        "read!!!!!!! 8^O" in stdout
    ), error_msg
    swilog.info("[PASSED] Successfully found response for extreme flag (%s)" % flag)


def max_count_test(target, flag):
    """!Check the 'max count' flag.

    @param target: fixture to communicate with the target
    @param flag: fixture to provide option
    """
    stdout = target.run(
        "cd %s/bin/; ./%s %s permissions %s/testFile1"
        % (APP_SANDBOX_PATH, APP_NAME, flag, APP_SANDBOX_PATH)
    )
    error_msg = "[FAILED] Did not find 'Maximum file count " "reached' (%s)" % flag
    assert "Maximum file count reached." in stdout, error_msg
    swilog.info(
        "[PASSED] Successfully found 'Maximum file count reached' " "(%s)" % flag
    )


# ====================================================================================
# Test functions
# ====================================================================================
@pytest.mark.usefixtures("app_leg")
def L_SampleApps_FileInfo_0001(target):
    """!Script will.

        1. Make and install the test app <br>
        2. Run the test app <br>
        3. Check if expected messages appears in log

    @param target: fixture to communicate with the target
    @param app_leg: fixture to make, install and remove application
    """
    swilog.step("Execute L_SampleApps_FileInfo_0001")

    # ***Testing 'help' flag/command***
    help_test(target, "--help")
    help_test(target, "-h")
    help_test(target, "help")

    # ***Testing 'permissions' command***--
    # Create a file in the fileInfo sandbox to use for testing
    cmd = "cd %s/; touch testFile1" % APP_SANDBOX_PATH
    exit_status, rsp = target.run(cmd, withexitstatus=True)
    swilog.debug(rsp)
    assert exit_status == 0

    # Change the files permissions to 'read', 'write',
    # And 'execute' for all users
    cmd = "cd %s/;  chmod a=rwx testFile1" % APP_SANDBOX_PATH
    exit_status, rsp = target.run(cmd, withexitstatus=True)
    swilog.debug(rsp)
    assert exit_status == 0

    permissions_test(
        target, "read write execute", "read write execute", "read write execute"
    )

    # Change the files permissions to 'read' and 'write', for user, 'execute'
    # For group members, and 'read' for others
    cmd = "cd %s/;  chmod u=rw,g=x,o=r testFile1" % APP_SANDBOX_PATH
    exit_status, rsp = target.run(cmd, withexitstatus=True)
    swilog.debug(rsp)
    assert exit_status == 0

    permissions_test(target, "read write", "execute", "read")

    # ***Testing 'type' command***---
    type_test(target, "%s/testFile1" % APP_SANDBOX_PATH, "regular file")
    type_test(target, "%s/" % APP_SANDBOX_PATH, "directory")

    # ***Testing 'extreme' flag
    # Change the files permissions to 'read' for all users
    cmd = "cd %s/;  chmod a=r testFile1" % APP_SANDBOX_PATH
    exit_status, rsp = target.run(cmd, withexitstatus=True)
    swilog.debug(rsp)
    assert exit_status == 0
    extreme_test(target, "-x")
    extreme_test(target, "--extreme")

    # ***Testing 'max count' flag***
    max_count_test(target, "-mc 1")
    max_count_test(target, "--max-count=1")

    swilog.info("[PASSED] L_SampleApps_FileInfo_0001")
