""" @package atomicFileOperationCreateModule atomicFile operation create test

    Set of functions to test the le_atomFile_Createy
"""
import os
import files
import swilog
import time

__copyright__ = 'Copyright (C) Sierra Wireless Inc.'
# ==================================================================================================
# Constants and Globals
# ==================================================================================================
TEST_RESOURCES = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                              'resources')
TEST_TOOLS = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                          'tools')
APP_NAME = "atomCreate"
APP_PATH = os.path.join(os.path.join(TEST_RESOURCES, "atomCreate"),
                        "atomCreate.adef")


# ==================================================================================================
# Test functions
# ==================================================================================================
def L_AtomicFile_Operation_0008(target, legato, app_leg, init_atomicFile):
    """
    Purpose: Verify that le_atomFile_Create returns LE_DUPLICATE
            if the target file already existed and
            LE_FLOCK_FAIL_IF_EXIST is specified in createMode
    Initial condition:
        1. Test app is unsandboxed
    Verification:
        This test case will mark as "failed" when
            1. le_atomFile_Create doesn't return LE_DUPLICATE
    This script will
        1. Transfer a file to the target
        2. Make and install the test app
        3. Run the test app
        4. Check if "le_atomFile_Create returns LE_DUPLICATE ..."
        can be captured from the target's log

    Args:
        target: fixture to communicate with the target
        legato: fixture to call useful functions regarding legato
        app_leg: fixture regarding to build, install and remove app
        init_atomicFile: fixture to initialize and clean up environment

    """

    test_app_name = "atomCreate"
    test_app_proc_name = "atomCreateProc"
    hw_file_path = os.path.join(TEST_TOOLS, "testFile.txt")
    target_log_cmd = "/sbin/logread"
    test_file_path = init_atomicFile
    test_description = "duplicate"

    files.scp([hw_file_path], test_file_path, target.target_ip)

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
    assert "PASSED" in rsp, "test returned [FAILED]"


def L_AtomicFile_Operation_0010(target, legato, app_leg, init_atomicFile):
    """
    Purpose: Verify that le_atomFile_Create can create and
            open file with specified file permission if the
            target file wasn't existed before
    Initial condition:
        1. Test app is unsandboxed
    Verification:
        This test case will mark as "failed" when
            1. le_atomFile_Create can't create and open a file
            with specified file permission
    This script will
        1. Make and install the test app
        2. Run the test app
        3. Check if "le_atomFile_Create can create ..." can be
        captured from the target's log

    Args:
        target: fixture to communicate with the target
        legato: fixture to call useful functions regarding legato
        app_leg: fixture regarding to build, install and remove app
        init_atomicFile: fixture to initialize and clean up environment

    """

    test_app_name = "atomCreate"
    test_app_proc_name = "atomCreateProc"
    target_log_cmd = "/sbin/logread"
    test_file_path = init_atomicFile
    test_description = "fd"

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
    assert "PASSED" in rsp, "test returned [FAILED]"


def L_AtomicFile_Operation_0018(target, legato, app_leg, init_atomicFile):
    """
    Purpose: Verify the atomicity of le_atomFile_Create is guaranteed
            once the process acquires the file lock if the target file
            wasn't existed
    Initial condition:
        1. Test app is unsandboxed
    Verification:
        This test case will mark as "failed" when
            1. The second process who calls le_atomFile_Create does not
            block after the first process of the test app held
            the file lock
            2. The second process who calls le_atomFile_Create does block
            after the first process of the test app released
            the file lock
            3. The data written by the first process are not preserved
            after the interruption of the second process's write operation
   This script will
        1. Transfer a file to the target
        2. Make and install the test app
        3. Run the test app
        4. Check if the second process does block after the first process
        successfully acquired the lock
        5. Check if the second process doesn't block after the first process
        successfully released the lock
        6. Interrupts the second process's write operation by stopping
        the test app
        7. Check if the data of the file have been changed after interruption

    Args:
        target: fixture to communicate with the target
        legato: fixture to call useful functions regarding legato
        app_leg: fixture regarding to build, install and remove app
        init_atomicFile: fixture to initialize and clean up environment

    """

    test_app_name = "atomCreate"
    test_app_proc_name = "atomCreateProc"
    target_app_cmd = "/legato/systems/current/bin/app"
    test_file_path = "/home/root/testFile.txt"
    test_description = "atomicMultiAccess"

    # Wait for the occurrence of the specified message in the target's log
    # Pre:
    # Param: $1 - message to be expected from the log; $2 - wait time period
    # Post: return 0 when the message has been found; 1 otherwise

    legato.clear_target_log()
    rsp = legato.runProc(test_app_name, test_app_proc_name,
                         test_file_path, test_description)
    assert legato.wait_for_log_msg("first process is holding a file lock",
                                   20) is True
    assert legato.wait_for_log_msg("second process is holding a file lock",
                                   20) is False
    # Process of the test app held the file lock"

    assert legato.wait_for_log_msg("first process\'s file lock is released",
                                   45) is True
    assert legato.wait_for_log_msg("second process is holding a file lock",
                                   20) is True
    # Previous file lock was released"

    expected_log = "second process writes string 123 to the file"
    assert legato.wait_for_log_msg(expected_log, 20) is True

    rsp = target.run(" %s stop %s" % (target_app_cmd, test_app_name))

    exit, rsp = target.run("cat %s" % (test_file_path), withexitstatus=1)
    swilog.info(rsp)
    assert "string 123" not in rsp, "[FAILED] the atomicity of "\
                                    "le_atomFile_Create isn't guaranteed "\
                                    "once the process acquires the file "\
                                    "lock if the target file "\
                                    "was already existed"
