r"""!atomicFile operation open test.

Set of functions to test the le_atomFile_Open

@package atomicFileOperationOpenModule
@file
\ingroup runtimeTests
"""
import os
import time

import pytest

import files
import swilog

__copyright__ = "Copyright (C) Sierra Wireless Inc."
# ======================================================================================
# Constants and Globals
# ======================================================================================
TEST_RESOURCES = os.path.join(os.path.abspath(os.path.dirname(__file__)), "resources")
TEST_TOOLS = os.path.join(os.path.abspath(os.path.dirname(__file__)), "tools")
APP_NAME = "atomOpen"
APP_PATH = os.path.join(TEST_RESOURCES, "atomOpen")


# ======================================================================================
# Test functions
# ======================================================================================
@pytest.mark.usefixtures("app_leg")
def L_AtomicFile_Operation_0001(target, legato, init_atomicFile):
    """!Purpose: Verify that le_atomFile_Open returns LE_NOT_FOUND.

    when tries to open a non-existed file

    Initial condition:
        1. test app is unsandboxed

    Verification:
        This test case will mark as "failed" when
            1. le_atomFile_Open doesn't return LE_NOT_FOUND

    This script will
        1. Make and install the test app
        2. Run the test app
        3. Check  "le_atomFile_Open returns LE_NOT_FOUND ..."
        can be captured from the target's log == 0:

    @param target: fixture to communicate with the target
    @param legato: fixture to call useful functions regarding legato
    @param app_leg: fixture regarding to build, install and remove app
    @param init_atomicFile: fixture to setup and cleanup environment
    """
    test_app_name = "atomOpen"
    test_app_proc_name = "atomOpenProc"
    target_log_cmd = "/sbin/logread"
    test_description = "notFound"
    swilog.debug(init_atomicFile)

    legato.clear_target_log()

    rsp = legato.runProc(test_app_name, test_app_proc_name, APP_PATH, test_description)

    time.sleep(5)
    cmd = target_log_cmd
    rsp = target.run(cmd)
    swilog.info(rsp)
    assert "PASSED" in rsp or "FAILED" in rsp, (
        "[FAILED] unable to get the "
        "test app's output message "
        "form the target's syslog"
    )


@pytest.mark.usefixtures("app_leg")
def L_AtomicFile_Operation_0002(target, legato, init_atomicFile):
    """!Purpose: Verify that le_atomFile_Open returns LE_FAULT.

    there was an error (accesses to a non-existed dir == 0:

    Initial condition:
        1. test app is unsandboxed

    Verification:
        This test case will mark as "failed" when
            1. le_atomFile_Open doesn't return LE_FAULT

    This script will
        1. Make and install the test app
        2. Run the test app
        3. Check  "le_atomFile_Open returns LE_FAULT ..."
        can be captured from the target's log == 0:

    @param target: fixture to communicate with the target
    @param legato: fixture to call useful functions regarding legato
    @param app_leg: fixture regarding to build, install and remove app
    @param init_atomicFile: fixture to setup and cleanup environment
    """
    test_app_name = "atomOpen"
    test_app_proc_name = "atomOpenProc"
    target_log_cmd = "/sbin/logread"
    test_file_path = "/abc/def/abc.txt"
    test_description = "fault"
    swilog.debug(init_atomicFile)

    legato.clear_target_log()

    rsp = legato.runProc(
        test_app_name, test_app_proc_name, test_file_path, test_description
    )

    time.sleep(5)
    cmd = target_log_cmd
    rsp = target.run(cmd)
    swilog.info(rsp)
    assert "PASSED" in rsp or "FAILED" in rsp, (
        "[FAILED] unable to get the"
        " test app's output message "
        "form the target's syslog"
    )


@pytest.mark.usefixtures("app_leg")
def L_AtomicFile_Operation_0003(target, legato, init_atomicFile):
    """!Purpose: Verify that le_atomFile_Open returns the file descriptor.

    when successfully opens the file

    Initial condition:
        1. test app is unsandboxed

    Verification:
        This test case will mark as "failed" when
            1. le_atomFile_Open doesn't return a file descriptor

    This script will
        1. Make and install the test app
        2. Run the test app
        3. Check  "le_atomFile_Open returns a file descriptor ..."
        can be captured from the target's log == 0:

    @param target: fixture to communicate with the target
    @param legato: fixture to call useful functions regarding legato
    @param app_leg: fixture regarding to build, install and remove app
    @param init_atomicFile: fixture to setup and cleanup environment
    """
    test_app_name = "atomOpen"
    test_app_proc_name = "atomOpenProc"
    hw_file_path = os.path.join(TEST_TOOLS, "testFile.txt")
    target_log_cmd = "/sbin/logread"
    test_file_path = init_atomicFile
    test_description = "fd"

    files.scp([hw_file_path], test_file_path, target.target_ip)

    legato.clear_target_log()

    rsp = legato.runProc(
        test_app_name, test_app_proc_name, test_file_path, test_description
    )

    time.sleep(5)
    cmd = target_log_cmd
    rsp = target.run(cmd)
    swilog.info(rsp)
    assert "PASSED" in rsp or "FAILED" in rsp, (
        "[FAILED] unable to get the "
        "test app's output message "
        "form the target's syslog"
    )
