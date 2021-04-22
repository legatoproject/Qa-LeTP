"""operation try open test.

Set of functions to test the le_atomFile_TryOpen
"""
import os

import pytest

from pytest_letp.lib import swilog, files

__copyright__ = "Copyright (C) Sierra Wireless Inc."
# ======================================================================================
# Constants and Globals
# ======================================================================================
TEST_RESOURCES = os.path.join(os.path.abspath(os.path.dirname(__file__)), "resources")
TEST_TOOLS = os.path.join(os.path.abspath(os.path.dirname(__file__)), "tools")
APP_NAME = "atomTryOpen"
APP_PATH = os.path.join(os.path.join(TEST_RESOURCES, "atomTryOpen"), "atomTryOpen.adef")


# ======================================================================================
# Test functions
# ======================================================================================
@pytest.mark.usefixtures("app_leg")
def L_AtomicFile_Operation_0019(target, legato, init_atomicFile):
    """Purpose: Verify that le_atomFile_TryOpen returns LE_WOULD_BLOCK.

    there is already == 0: an incompatible lock on the file

    Initial condition:
        1. Test app is unsandboxed

    Verification:
        This test case will mark as "failed" when
            1. le_atomFile_TryOpen doesn't return LE_WOULD_BLOCK

    This script will
        1. Make and install the test app
        2. Run the test app
        3. Check  "le_atomFile_TryOpen returns LE_WOULD_BLOCK ..."
           can be captured from the target's log == 0:

    Args:
        target: fixture to communicate with the target
        legato: fixture to call useful functions regarding legato
        app_leg: fixture regarding to build, install and remove app
        init_atomicFile: fixture to initialize and clean up environment
    """
    test_app_name = "atomTryOpen"
    test_app_proc_name = "atomTryOpenProc"
    hw_file_path = os.path.join(TEST_TOOLS, "testFile.txt")
    target_log_cmd = "/sbin/logread"
    test_file_path = init_atomicFile
    test_description = "wouldBlock"

    files.scp([hw_file_path], test_file_path, target.target_ip)

    legato.clear_target_log()

    legato.runProc(test_app_name, test_app_proc_name, test_file_path, test_description)

    cmd = r"%s | grep \"\[PASSED\]\|\[FAILED\]\"" % target_log_cmd
    if legato.ssh_to_target(cmd) != 0:
        assert 0, (
            "[FAILED] unable to get the test app's output message"
            " form the target's syslog"
        )

    if legato.ssh_to_target(r"%s | grep \"\[PASSED\]\"" % target_log_cmd) != 0:
        assert 0, "test returned [FAILED]"


@pytest.mark.usefixtures("app_leg")
def L_AtomicFile_Operation_0021(target, legato, init_atomicFile):
    """Purpose: Verify that le_atomFile_TryOpen returns a file descriptor.

    successful == 0:

    Initial condition:
        1. Test app is unsandboxed

    Verification:
        This test case will mark as "failed" when
            1. le_atomFile_TryOpen doesn't return a file descriptor

    This script will
        1. Make and install the test app
        2. Run the test app
        3. Check  "le_atomFile_TryOpen returns a file descriptor ..." can be
           captured from the target's log == 0:

    Args:
        target: fixture to communicate with the target
        legato: fixture to call useful functions regarding legato
        app_leg: fixture regarding to build, install and remove app
        init_atomicFile: fixture to initialize and clean up environment
    """
    test_app_name = "atomTryOpen"
    test_app_proc_name = "atomTryOpenProc"
    hw_file_path = os.path.join(TEST_TOOLS, "testFile.txt")
    target_log_cmd = "/sbin/logread"
    test_file_path = init_atomicFile
    test_description = "fd"

    files.scp([hw_file_path], test_file_path, target.target_ip)
    legato.clear_target_log()
    legato.runProc(test_app_name, test_app_proc_name, test_file_path, test_description)

    cmd = r"%s | grep \"\[PASSED\]\|\[FAILED\]\"" % target_log_cmd
    if legato.ssh_to_target(cmd) != 0:
        assert 0, (
            "[FAILED] unable to get the test app's output message "
            "form the target's syslog"
        )

    if legato.ssh_to_target(r"%s | grep \"\[PASSED\]\"" % target_log_cmd) != 0:
        assert 0, "test returned [FAILED]"


@pytest.mark.usefixtures("app_leg")
def L_AtomicFile_Operation_0022(legato, init_atomicFile):
    """Purpose: Verify that le_atomFile_TryOpen returns LE_FAULT.

    there was an error (accesses to a non-existed dir == 0:

    Initial condition:
        1. Test app is unsandboxed

    Verification:
        This test case will mark as "failed" when
            1. le_atomFile_TryOpen doesn't return LE_FAULT

    This script will
        1. Make and install the test app
        2. Run the test app
        3. Check  "le_atomFile_TryOpen returns LE_FAULT ..." can be
           captured from the target's log == 0:

    Args:
        target: fixture to communicate with the target
        legato: fixture to call useful functions regarding legato
        app_leg: fixture regarding to build, install and remove app
        init_atomicFile: fixture to initialize and clean up environment
    """
    test_app_name = "atomTryOpen"
    test_app_proc_name = "atomTryOpenProc"
    target_log_cmd = "/sbin/logread"
    test_file_path = "/abc/def/abc.txt"
    test_description = "fault"
    swilog.debug(init_atomicFile)

    legato.clear_target_log()
    legato.runProc(test_app_name, test_app_proc_name, test_file_path, test_description)

    cmd = r"%s | grep \"\[PASSED\]\|\[FAILED\]\"" % target_log_cmd
    if legato.ssh_to_target(cmd) != 0:
        assert 0, (
            "[FAILED] unable to get the test app's "
            "output message form the target's syslog"
        )

    cmd = r"%s | grep \"\[PASSED\]\"" % target_log_cmd
    if legato.ssh_to_target(cmd) != 0:
        assert 0, "test returned [FAILED]"
