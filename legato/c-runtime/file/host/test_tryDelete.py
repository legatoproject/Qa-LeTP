""" @package atomicFileTryDeleteModule atomicFile operation try delete test

    Set of functions to test the le_atomFile_TryDelete
"""
import os
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
APP_NAME = "atomTryDelete"
APP_PATH = os.path.join(os.path.join(TEST_RESOURCES, "atomTryDelete"),
                        "atomTryDelete.adef")


# ==================================================================================================
# Test functions
# ==================================================================================================
def L_AtomicFile_Operation_0037(target, legato, app_leg, init_atomicFile):
    """
    Purpose: Verify that le_atomFile_TryDelete returns LE_NOT_FOUND
    file doesn't exists == 0
    Initial condition:
        1. Test app is unsandboxed
    Verification:
        This test case will mark as "failed" when
            1. le_atomFile_TryDelete doesn't return LE_NOT_FOUND
    This script will
        1. Make and install the test app
        2. Run the test app
        3. Check  "le_atomFile_TryDelete returns LE_NOT_FOUND ..."
        can be captured from the target's log == 0:

    Args:
        target: fixture to communicate with the target
        legato: fixture to call useful functions regarding legato
        app_leg: fixture regarding to build, install and remove app
        init_atomicFile: fixture to initialize and clean up environment

    """

    test_app_name = "atomTryDelete"
    test_app_proc_name = "atomTryDeleteProc"
    target_log_cmd = "/sbin/logread"
    test_file_path = init_atomicFile
    test_description = "notFound"

    legato.clear_target_log()
    legato.runProc(test_app_name, test_app_proc_name,
                   test_file_path, test_description)

    cmd = r"%s | grep \"\[PASSED\]\|\[FAILED\]\"" % target_log_cmd
    if legato.ssh_to_target(cmd) != 0:
        assert 0, "[FAILED] unable to get the test app's output"\
                  " message form the target's syslog"

    if legato.ssh_to_target(r"%s | grep \"\[PASSED\]\"" % target_log_cmd) != 0:
        assert 0, "test returned [FAILED]"


def L_AtomicFile_Operation_0038(target, legato, app_leg, init_atomicFile):
    """
    Purpose: Verify that le_atomFile_TryDelete returns LE_FAULT
    there was an error (accesses to a non-existed dir == 0
    Initial condition:
        1. Test app is unsandboxed
    Verification:
        This test case will mark as "failed" when
            1. le_atomFile_TryDelete doesn't return LE_FAULT
    This script will
        1. Make and install the test app
        2. Run the test app
        3. Check  "le_atomFile_TryDelete returns LE_FAULT ..."
        can be captured from the target's log == 0:

    Args:
        target: fixture to communicate with the target
        legato: fixture to call useful functions regarding legato
        app_leg: fixture regarding to build, install and remove app
        init_atomicFile: fixture to initialize and clean up environment

    """

    test_app_name = "atomTryDelete"
    test_app_proc_name = "atomTryDeleteProc"
    target_log_cmd = "/sbin/logread"
    test_file_path = "/abc/def/abc.txt"
    test_description = "fault"

    legato.clear_target_log()
    legato.runProc(test_app_name, test_app_proc_name,
                   test_file_path, test_description)

    cmd = r"%s | grep \"\[PASSED\]\|\[FAILED\]\"" % target_log_cmd
    if legato.ssh_to_target(cmd) != 0:
        assert 0, "[FAILED] unable to get the test app's"\
                  " output message form the target's syslog"

    if legato.ssh_to_target(r"%s | grep \"\[PASSED\]\"" % target_log_cmd) != 0:
        assert 0, "test returned [FAILED]"


def L_AtomicFile_Operation_0039(target, legato, app_leg, init_atomicFile):
    """
    Purpose: Verify that le_atomFile_TryDelete returns LE_OK successful == 0
    Initial condition:
        1. Test app is unsandboxed
    Verification:
        This test case will mark as "failed" when
            1. le_atomFile_TryDelete doesn't return LE_OK
            2. Target file wasn't removed
    This script will
        1. Make and install the test app
        2. Run the test app
        3. Check  "le_atomFile_TryDelete returns LE_OK ..."
        can be captured from the target's log == 0:
        4. Check  target file is deleted == 0:

    Args:
        target: fixture to communicate with the target
        legato: fixture to call useful functions regarding legato
        app_leg: fixture regarding to build, install and remove app
        init_atomicFile: fixture to initialize and clean up environment

    """

    test_app_name = "atomTryDelete"
    test_app_proc_name = "atomTryDeleteProc"
    hw_file_path = os.path.join(TEST_TOOLS, "testFile.txt")
    target_log_cmd = "/sbin/logread"
    test_file_path = init_atomicFile
    test_description = "ok"

    files.scp([hw_file_path], test_file_path, target.target_ip)
    legato.clear_target_log()
    legato.runProc(test_app_name, test_app_proc_name,
                   test_file_path, test_description)

    cmd = r"%s | grep \"\[PASSED\]\|\[FAILED\]\"" % target_log_cmd
    if legato.ssh_to_target(cmd) != 0:
        assert 0, "[FAILED] unable to get the test app's"\
                  " output message form the target's syslog"

    if legato.ssh_to_target(r"%s | grep \"\[PASSED\]\"" % target_log_cmd) != 0:
        assert 0, "test returned [FAILED]"

    if target.run(" [ -e %s ]" % (test_file_path), withexitstatus=1)[0] != 0:
        swilog.info("[PASSED] le_atomFile_TryDelete successfully"
                    " removed the target file")
    else:
        assert 0, "[FAILED] le_atomFile_TryDelete wasn't"\
                  " successfully removed the target file"


def L_AtomicFile_Operation_0040(target, legato, app_leg, init_atomicFile):
    """
    Purpose: Verify that le_atomFile_TryDelete returns LE_WOULD_BLOCK
    file is already locked == 0
    Initial condition:
        1. Test app is unsandboxed
    Verification:
        This test case will mark as "failed" when
            1. le_atomFile_TryDelete doesn't return LE_WOULD_BLOCK
            2. Target file is removed
    This script will
        1. Make and install the test app
        2. Run the test app
        3. Check  "le_atomFile_TryDelete returns LE_WOULD_BLOCK ..."
        can be captured from the target's log == 0:
        4. Check  target file isn't deleted == 0:

    Args:
        target: fixture to communicate with the target
        legato: fixture to call useful functions regarding legato
        app_leg: fixture regarding to build, install and remove app
        init_atomicFile: fixture to initialize and clean up environment

    """

    test_app_name = "atomTryDelete"
    test_app_proc_name = "atomTryDeleteProc"
    hw_file_path = os.path.join(TEST_TOOLS, "testFile.txt")
    target_log_cmd = "/sbin/logread"
    test_file_path = init_atomicFile
    test_description = "wouldBlock"

    files.scp([hw_file_path], test_file_path, target.target_ip)
    legato.clear_target_log()
    legato.runProc(test_app_name, test_app_proc_name,
                   test_file_path, test_description)

    cmd = r"%s | grep \"\[PASSED\]\|\[FAILED\]\"" % target_log_cmd
    if legato.ssh_to_target(cmd) != 0:
        assert 0, "[FAILED] unable to get the test app's"\
                  " output message form the target's syslog"

    if legato.ssh_to_target(r"%s | grep \"\[PASSED\]\"" % target_log_cmd) != 0:
        assert 0, "test returned [FAILED]"

    if target.run(" [ -e %s ]" % (test_file_path), withexitstatus=1)[0] == 0:
        swilog.info("[PASSED] le_atomFile_TryDelete won't delete"
                    " the file which it has an associated file lock")
    else:
        assert 0, "[FAILED] le_atomFile_TryDelete deleted the "\
                  "file which it has an associated file lock"
