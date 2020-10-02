r"""!atomicFile Stream try open test.

Set of functions to test the le_atomFile_TryOpenStream

@package atomicFileStreamTryOpenModule
@file
\ingroup runtimeTests
"""
import os

import pytest

import files
import swilog

__copyright__ = "Copyright (C) Sierra Wireless Inc."
# ======================================================================================
# Constants and Globals
# ======================================================================================
TEST_RESOURCES = os.path.join(os.path.abspath(os.path.dirname(__file__)), "resources")
TEST_TOOLS = os.path.join(os.path.abspath(os.path.dirname(__file__)), "tools")
APP_NAME = "atomTryOpenStream"
APP_PATH = os.path.join(
    os.path.join(TEST_RESOURCES, "atomTryOpenStream"), "atomTryOpenStream.adef"
)


# ======================================================================================
# Test functions
# ======================================================================================
@pytest.mark.usefixtures("app_leg")
def L_AtomicFile_Stream_0019(target, legato, init_atomicFile):
    """!Purpose: Verify that resultPtr of le_atomFile_TryOpenStream returns.

    LE_WOULD_BLOCK  there is already == 0:
    an incompatible lock on the file

    Initial condition:
        1. Test app is unsandboxed

    Verification:
        This test case will mark as "failed" when
            1. le_atomFile_TryOpenStream doesn't return LE_WOULD_BLOCK

    This script will
        1. Make and install the test app
        2. Run the test app
        3. Check  "le_atomFile_TryOpenStream returns LE_WOULD_BLOCK ..."
        can be captured from the target's log == 0:

    @param target: fixture to communicate with the target
    @param legato: fixture to call useful functions regarding legato
    @param app_leg: fixture regarding to build, install and remove app
    @param init_atomicFile: fixture to initialize and clean up environment
    """
    test_app_name = "atomTryOpenStream"
    test_app_proc_name = "atomTryOpenStreamProc"
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
            "[FAILED] unable to get the test app's "
            "output message form the target's syslog"
        )

    cmd = r"%s | grep \"\[PASSED\]\"" % target_log_cmd
    if legato.ssh_to_target(cmd) != 0:
        assert 0, "test returned [FAILED]"


@pytest.mark.usefixtures("app_leg")
def L_AtomicFile_Stream_0020(legato, init_atomicFile):
    """!Purpose: Verify resultPtr of that le_atomFile_TryOpenStream returns.

    LE_NOT_FOUND  the file does not exist == 0

    Initial condition:
        1. Test app is unsandboxed

    Verification:
        This test case will mark as "failed" when
            1. le_atomFile_TryOpenStream doesn't return LE_NOT_FOUND

    This script will
        1. Make and install the test app
        2. Run the test app
        3. Check  "le_atomFile_TryOpenStream returns LE_NOT_FOUND ..."
        can be captured from the target's log == 0:

    @param target: fixture to communicate with the target
    @param legato: fixture to call useful functions regarding legato
    @param app_leg: fixture regarding to build, install and remove app
    @param init_atomicFile: fixture to initialize and clean up environment
    """
    test_app_name = "atomTryOpenStream"
    test_app_proc_name = "atomTryOpenStreamProc"
    target_log_cmd = "/sbin/logread"
    test_file_path = init_atomicFile
    test_description = "notFound"

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


@pytest.mark.usefixtures("app_leg")
def L_AtomicFile_Stream_0021(target, legato, init_atomicFile):
    """!Purpose: Verify that le_atomFile_TryOpenStream returns.

    a file pointer  successful == 0

    Initial condition:
        1. Test app is unsandboxed

    Verification:
        This test case will mark as "failed" when
            1. le_atomFile_TryOpenStream doesn't return a file pointer

    This script will
        1. Make and install the test app
        2. Run the test app
        3. Check  "le_atomFile_TryOpenStream returns a file pointer ..."
        can be captured from the target's log == 0:

    @param target: fixture to communicate with the target
    @param legato: fixture to call useful functions regarding legato
    @param app_leg: fixture regarding to build, install and remove app
    @param init_atomicFile: fixture to initialize and clean up environment
    """
    test_app_name = "atomTryOpenStream"
    test_app_proc_name = "atomTryOpenStreamProc"
    hw_file_path = os.path.join(TEST_TOOLS, "testFile.txt")
    target_log_cmd = "/sbin/logread"
    test_file_path = init_atomicFile
    test_description = "fp"

    files.scp([hw_file_path], test_file_path, target.target_ip)
    legato.clear_target_log()
    legato.runProc(test_app_name, test_app_proc_name, test_file_path, test_description)

    cmd = r"%s | grep \"\[PASSED\]\|\[FAILED\]\"" % target_log_cmd
    if legato.ssh_to_target(cmd) != 0:
        assert 0, (
            "[FAILED] unable to get the test app's"
            " output message form the target's syslog"
        )

    cmd = r"%s | grep \"\[PASSED\]\"" % target_log_cmd
    if legato.ssh_to_target(cmd) != 0:
        assert 0, "test returned [FAILED]"


@pytest.mark.usefixtures("app_leg")
def L_AtomicFile_Stream_0022(legato, init_atomicFile):
    """!Purpose: Verify that resultPtr of le_atomFile_TryOpenStream returns.

    LE_FAULT  there was an error (accesses to a non-existed dir == 0

    Initial condition:
        1. Test app is unsandboxed

    Verification:
        This test case will mark as "failed" when
            1. le_atomFile_TryOpenStream doesn't return LE_FAULT

    This script will
        1. Make and install the test app
        2. Run the test app
        3. Check  "le_atomFile_TryOpenStream returns LE_FAULT ..."
        can be captured from the target's log == 0:

    @param target: fixture to communicate with the target
    @param legato: fixture to call useful functions regarding legato
    @param app_leg: fixture regarding to build, install and remove app
    @param init_atomicFile: fixture to initialize and clean up environment
    """
    test_app_name = "atomTryOpenStream"
    test_app_proc_name = "atomTryOpenStreamProc"
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


@pytest.mark.usefixtures("app_leg")
def L_AtomicFile_Stream_0023(target, legato, init_atomicFile):
    """!Purpose: Verify that le_atomFile_TryOpenStream can successfully.

    acquire a file lock to the target file

    Initial condition:
        1. Test app is unsandboxed

    Verification:
        This test case will mark as "failed" when
            1. The second process who calls le_atomFile_OpenStream
               does not block after the first
               process of the test app held the file lock

    This script will
        1. Transfer a file to the target
        1. Make and install the test app
        2. Run the test app
        3. Check  the second process does block after the first process
        successfully acquired the lock == 0:

    @param target: fixture to communicate with the target
    @param legato: fixture to call useful functions regarding legato
    @param app_leg: fixture regarding to build, install and remove app
    @param init_atomicFile: fixture to initialize and clean up environment
    """
    test_app_name = "atomTryOpenStream"
    test_app_proc_name = "atomTryOpenStreamProc"
    hw_file_path = os.path.join(TEST_TOOLS, "testFile.txt")
    test_file_path = "/home/root/testFile.txt"
    test_description = "acquireFlock"
    swilog.debug(init_atomicFile)

    # Wait for the occurrence of the specified message in the target's log
    # Pre:
    # Param: $1 - message to be expected from the log; $2 - wait time period
    # Post: return 0 when the message has been found; 1 otherwise

    files.scp([hw_file_path], test_file_path, target.target_ip)
    legato.clear_target_log()

    legato.runProc(test_app_name, test_app_proc_name, test_file_path, test_description)

    assert legato.wait_for_log_msg("first process is holding a file lock", 5) is True, (
        "[FAILED] the first process "
        "can't acquire a file lock "
        "when it calls "
        "le_atomFile_TryOpenStream"
    )

    assert (
        legato.wait_for_log_msg("second process is holding a file lock", 120) is True
    ), (
        "[FAILED] "
        "le_atomFile_TryOpenStream"
        " can't successfully "
        "acquire a file lock to the"
        " target file"
    )
