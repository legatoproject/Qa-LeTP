""" @package atomicFileStreamOpenModule atomicFile Stream open test

    Set of functions to test the le_atomFile_OpenStream
"""
import pytest
import os
import time
import files
import swilog

__copyright__ = 'Copyright (C) Sierra Wireless Inc.'
# ==================================================================================================
# Constants and Globals
# ==================================================================================================
TEST_RESOURCES = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                              'resources')
TEST_TOOLS = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                          'tools')
APP_NAME = "atomOpenStream"
APP_PATH = os.path.join(os.path.join(TEST_RESOURCES, "atomOpenStream"),
                        "atomOpenStream.adef")


# ==================================================================================================
# Test functions
# ==================================================================================================
def L_AtomicFile_Stream_0001(target, legato, app_leg, init_atomicFile):
    """
    Purpose: Verify that resultPtr of le_atomFile_OpenStream returns
    LE_NOT_FOUND when tries to open a non-existed file

    Initial condition:
        1. Test app is unsandboxed
    Verification:
        This test case will mark as "failed" when
            1. le_atomFile_OpenStream doesn't return LE_NOT_FOUND
    This script will
        1. Make and install the test app
        2. Run the test app
        3. Check  "resultPtr of le_atomFile_OpenStream returns
        LE_NOT_FOUND ..." can be captured from the target's log == 0

    Args:
        target: fixture to communicate with the target
        legato: fixture to call useful functions regarding legato
        app_leg: fixture regarding to build, install and remove app
        init_atomicFile: fixture to initialize and clean up environment

    """

    test_app_name = "atomOpenStream"
    test_app_proc_name = "atomOpenStreamProc"
    target_log_cmd = "/sbin/logread"
    test_file_path = init_atomicFile
    test_description = "notFound"

    legato.clear_target_log()
    rsp = legato.runProc(test_app_name, test_app_proc_name,
                         test_file_path, test_description)

    time.sleep(5)
    cmd = target_log_cmd
    rsp = target.run(cmd)
    swilog.info(rsp)
    assert "PASSED" in rsp or "FAILED" in rsp, "[FAILED] unable to get the "\
                                               "test app's output message "\
                                               "form the target's syslog"


def L_AtomicFile_Stream_0002(target, legato, app_leg, init_atomicFile):
    """
    Purpose: Verify that resultPtr of le_atomFile_OpenStream returns LE_FAULT
    there was == 0: an error (accesses to a non-existed dir)
    Initial condition:
        1. Test app is unsandboxed
    Verification:
        This test case will mark as "failed" when
            1. resultPtr doesn't return LE_FAULT
    This script will
        1. Make and install the test app
        2. Run the test app
        3. Check  "resultPtr of le_atomFile_Open returns LE_FAULT ..."
        can be captured from the target's log == 0:

    Args:
        target: fixture to communicate with the target
        legato: fixture to call useful functions regarding legato
        app_leg: fixture regarding to build, install and remove app
        init_atomicFile: fixture to initialize and clean up environment

    """

    test_app_name = "atomOpenStream"
    test_app_proc_name = "atomOpenStreamProc"
    target_log_cmd = "/sbin/logread"
    test_file_path = "/abc/def/abc.txt"
    test_description = "fault"

    legato.clear_target_log()
    rsp = legato.runProc(test_app_name, test_app_proc_name,
                         test_file_path, test_description)
    time.sleep(5)
    cmd = target_log_cmd
    rsp = target.run(cmd)
    swilog.info(rsp)
    assert "PASSED" in rsp or "FAILED" in rsp, "[FAILED] unable to get" \
                                               " the test app's output "\
                                               "message form the "\
                                               "target's syslog"


def L_AtomicFile_Stream_0003(target, legato, app_leg, init_atomicFile):
    """
    Purpose: Verify that le_atomFile_OpenStream returns the buffered file
    stream handle to the file  successfully == 0
    Initial condition:
        1. Test app is unsandboxed
    Verification:
        This test case will mark as "failed" when
            1. le_atomFile_OpenStream doesn't return a file stream
    This script will
        1. Make and install the test app
        2. Run the test app
        3. Check  "le_atomFile_OpenStream returns a file stream ..."
        can be captured from the target's log == 0:

    Args:
        target: fixture to communicate with the target
        legato: fixture to call useful functions regarding legato
        app_leg: fixture regarding to build, install and remove app
        init_atomicFile: fixture to initialize and clean up environment

    """

    test_app_name = "atomOpenStream"
    test_app_proc_name = "atomOpenStreamProc"
    hw_file_path = os.path.join(TEST_TOOLS, "testFile.txt")
    target_log_cmd = "/sbin/logread"
    test_file_path = init_atomicFile
    test_description = "fp"

    files.scp([hw_file_path], test_file_path, target.target_ip)
    legato.clear_target_log()
    rsp = legato.runProc(test_app_name, test_app_proc_name,
                         test_file_path, test_description)
    time.sleep(5)
    cmd = target_log_cmd
    rsp = target.run(cmd)
    swilog.info(rsp)
    assert "PASSED" in rsp or "FAILED" in rsp, "[FAILED] unable to get the" \
                                               " test app's output message "\
                                               "form the target's syslog"
