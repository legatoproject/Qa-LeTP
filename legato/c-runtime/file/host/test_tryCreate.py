r"""!atomicFile operation try create test.

Set of functions to test the le_atomFile_TryCreate

@package atomicFileTryCreateModule
@file
\ingroup runtimeTests
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
APP_NAME = "atomTryCreate"
APP_PATH = os.path.join(
    os.path.join(TEST_RESOURCES, "atomTryCreate"), "atomTryCreate.adef"
)


# ======================================================================================
# Test functions
# ======================================================================================
@pytest.mark.usefixtures("app_leg")
def L_AtomicFile_Operation_0024(target, legato, init_atomicFile):
    """!Purpose: Verify that le_atomFile_TryCreate returns LE_DUPLICATE.

    the target file already == 0: existed and LE_FLOCK_FAIL_IF_EXIST
    is specified in createMode

    Initial condition:
        1. Test app is unsandboxed

    Verification:
        This test case will mark as "failed" when
            1. le_atomFile_TryCreate doesn't return LE_DUPLICATE

    This script will
        1. Transfer a file to the target
        2. Make and install the test app
        3. Run the test app
        4. Check  "le_atomFile_TryCreate returns LE_DUPLICATE ..."
        can be captured from the target's log == 0:

    @param target: fixture to communicate with the target
    @param legato: fixture to call useful functions regarding legato
    @param app_leg: fixture regarding to build, install and remove app
    @param init_atomicFile: fixture to initialize and clean up environment
    """
    test_app_name = "atomTryCreate"
    test_app_proc_name = "atomTryCreateProc"
    hw_file_path = os.path.join(TEST_TOOLS, "testFile.txt")
    target_log_cmd = "/sbin/logread"
    test_file_path = init_atomicFile
    test_description = "duplicate"

    files.scp([hw_file_path], test_file_path, target.target_ip)
    legato.clear_target_log()
    legato.runProc(test_app_name, test_app_proc_name, test_file_path, test_description)

    cmd = r"%s | grep \"\[PASSED\]\|\[FAILED\]\"" % target_log_cmd
    if legato.ssh_to_target(cmd) != 0:
        assert 0, (
            "[FAILED] unable to get the test app's output message "
            "form the target's syslog"
        )

    cmd = r"%s | grep \"\[PASSED\]\"" % target_log_cmd
    if legato.ssh_to_target(cmd) != 0:
        assert 0, "test returned [FAILED]"


@pytest.mark.usefixtures("app_leg")
def L_AtomicFile_Operation_0025(target, legato, init_atomicFile):
    """!Purpose: Verify that le_atomFile_TryCreate returns LE_WOULD_BLOCK.

    the target file already == 0: existed and LE_FLOCK_FAIL_IF_EXIST
    is specified in createMode

    Initial condition:
        1. Test app is unsandboxed

    Verification:
        This test case will mark as "failed" when
            1. le_atomFile_TryCreate doesn't return LE_WOULD_BLOCK

    This script will
        1. Transfer a file to the target
        2. Make and install the test app
        3. Run the test app
        4. Check  "le_atomFile_TryCreate returns LE_WOULD_BLOCK ..."
        can be captured from the target's log == 0:

    @param target: fixture to communicate with the target
    @param legato: fixture to call useful functions regarding legato
    @param app_leg: fixture regarding to build, install and remove app
    @param init_atomicFile: fixture to initialize and clean up environment
    """
    test_app_name = "atomTryCreate"
    test_app_proc_name = "atomTryCreateProc"
    target_log_cmd = "/sbin/logread"
    test_file_path = init_atomicFile
    test_description = "wouldBlock"

    legato.clear_target_log()
    target.run("ls -a /tmp")
    legato.runProc(test_app_name, test_app_proc_name, test_file_path, test_description)

    cmd = r"%s | grep \"\[PASSED\]\|\[FAILED\]\"" % target_log_cmd
    if legato.ssh_to_target(cmd) != 0:
        assert 0, (
            "[FAILED] unable to get the test app's output message "
            "form the target's syslog"
        )

    cmd = r"%s | grep \"\[PASSED\]\"" % target_log_cmd
    if legato.ssh_to_target(cmd) != 0:
        assert 0, "test returned [FAILED]"


@pytest.mark.usefixtures("app_leg")
def L_AtomicFile_Operation_0026(target, legato, init_atomicFile):
    """!Purpose: Verify that le_atomFile_TryCreate returns a file descriptor.

    successful == 0:

    Initial condition:
        1. Test app is unsandboxed

    Verification:
        This test case will mark as "failed" when
            1. le_atomFile_TryCreate doesn't return a file descriptor

    This script will
        1. Transfer a file to the target
        2. Make and install the test app
        3. Run the test app
        4. Check  "le_atomFile_TryCreate returns a file descriptor ..."
        can be captured from the target's log == 0:

    @param target: fixture to communicate with the target
    @param legato: fixture to call useful functions regarding legato
    @param app_leg: fixture regarding to build, install and remove app
    @param init_atomicFile: fixture to initialize and clean up environment
    """
    test_app_name = "atomTryCreate"
    test_app_proc_name = "atomTryCreateProc"
    target_log_cmd = "/sbin/logread"
    test_file_path = init_atomicFile
    test_description = "fd"

    legato.clear_target_log()
    target.run("ls -a /tmp")
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
def L_AtomicFile_Operation_0027(legato, init_atomicFile):
    """!Purpose: Verify that le_atomFile_TryCreate returns LE_FAULT.

    there was an error (accesses to a non-existed dir == 0:

    Initial condition:
        1. Test app is unsandboxed

    Verification:
        This test case will mark as "failed" when
            1. le_atomFile_TryCreate doesn't return LE_FAULT

    This script will
        1. Transfer a file to the target
        2. Make and install the test app
        3. Run the test app
        4. Check  "le_atomFile_TryCreate returns LE_FAULT ..."
        can be captured from the target's log == 0:

    @param target: fixture to communicate with the target
    @param legato: fixture to call useful functions regarding legato
    @param app_leg: fixture regarding to build, install and remove app
    @param init_atomicFile: fixture to initialize and clean up environment
    """
    test_app_name = "atomTryCreate"
    test_app_proc_name = "atomTryCreateProc"
    target_log_cmd = "/sbin/logread"
    test_file_path = "/abc/def/abc.txt"
    test_description = "fault"
    swilog.debug(init_atomicFile)

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
def L_AtomicFile_Operation_0028(legato, init_atomicFile):
    """!Purpose: Verify that le_atomFile_TryCreate can successfully.

    acquire a file lock to the target file

    Initial condition:
        1. Test app is unsandboxed

    Verification:
        This test case will mark as "failed" when
            1. The second process who calls le_atomFile_Create
            does not block after the first process of the test
            app held the file lock

    This script will
        1. Transfer a file to the target
        1. Make and install the test app
        2. Run the test app
        3. Check  the second process does block after the
        first process successfully acquired the lock == 0:

    @param target: fixture to communicate with the target
    @param legato: fixture to call useful functions regarding legato
    @param app_leg: fixture regarding to build, install and remove app
    @param init_atomicFile: fixture to initialize and clean up environment
    """
    test_app_name = "atomTryCreate"
    test_app_proc_name = "atomTryCreateProc"
    test_file_path = "/home/root/testFile.txt"
    test_description = "acquireFlock"
    swilog.debug(init_atomicFile)

    # Wait for the occurrence of the specified message in the target's log
    # Pre:
    # Param: $1 - message to be expected from the log; $2 - wait time period
    # Post: return 0 when the message has been found; 1 otherwise

    legato.clear_target_log()
    legato.runProc(test_app_name, test_app_proc_name, test_file_path, test_description)
    assert legato.wait_for_log_msg("first process is holding a file lock", 5) is True, (
        "[FAILED] the first process"
        " can't acquire a file lock "
        "when it calls "
        "le_atomFile_TryCreate"
    )

    assert (
        legato.wait_for_log_msg("second process is holding a file lock", 120) is True
    ), (
        "[FAILED] "
        "le_atomFile_TryCreate can't"
        " successfully acquire a "
        "file lock to the target file"
    )
