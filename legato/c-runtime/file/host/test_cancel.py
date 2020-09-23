"""@package atomicFilecancelModule atomicFile operation try cancel test.

Set of functions to test the le_atomFile_Cancel
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
APP_NAME = "atomCancel"
APP_PATH = os.path.join(os.path.join(TEST_RESOURCES, "atomCancel"), "atomCancel.adef")


# ======================================================================================
# Test functions
# ======================================================================================
@pytest.mark.usefixtures("app_leg")
def L_AtomicFile_Operation_0031(target, legato, init_atomicFile):
    """Purpose: Verify that le_atomFile_Cancel cancels all changes.

    and closes the file descriptor for
    le_atomFile_Open(, le_atomFile_TryOpen(,le_atomFile_Create(
    and le_atomFile_TryCreate( with a write file lock

    Initial condition:
        1. test app is unsandboxed
    Verification:
       This test case will mark as "failed" when
            1. le_atomFile_Cancel commits all changes
    This script will
        1. Make and install the test app
        2. Run the test app
        3. Check  latest changes weren't committed after
        le_atomFile_Cancel is called == 0:
        4. Repeat above for different test scenarios

    Args:
        target: fixture to communicate with the target
        legato: fixture to call useful functions regarding legato
        app_leg: fixture regarding to build, install and remove app
        init_atomicFile: fixture to initialize and clean up environment
    """
    test_app_name = "atomCancel"
    test_app_proc_name = "atomCancelProc"
    hw_file_path = os.path.join(TEST_TOOLS, "testFile.txt")
    test_file_path = init_atomicFile
    test_descriptions = [
        "openWrtFlockOK",
        "tryOpenWrtFlockOK",
        "createWrtFlockOK",
        "tryCreateWrtFlockOK",
    ]

    ref_file_path = "/home/root/refFile.txt"
    files.scp([hw_file_path], ref_file_path, target.target_ip)

    for td in test_descriptions:
        files.scp([hw_file_path], test_file_path, target.target_ip)
        legato.clear_target_log()
        legato.runProc(test_app_name, test_app_proc_name, test_file_path, td)
        assert legato.wait_for_log_msg("le_atomFile_Cancel is called", 20) is True
        target.run("diff %s %s" % (test_file_path, ref_file_path))

    swilog.info(
        "\n[PASSED] le_atomFile_Cancel"
        " cancels all changes and closes the file descriptor) for "
        "le_atomFile_Open(, le_atomFile_TryOpen(, le_atomFile_Create("
        " and le_atomFile_TryCreate( with a write file lock"
    )


@pytest.mark.usefixtures("app_leg")
def L_AtomicFile_Operation_0032(target, legato, init_atomicFile):
    """Purpose: Verify that le_atomFile_Cancel cancels all changes.

    and closes the file descriptor for
    le_atomFile_Open(, le_atomFile_TryOpen(, le_atomFile_Create( and
    le_atomFile_TryCreate( with a read file lock

    Initial condition:
        1. Test app is unsandboxed
    Verification:
        This test case will mark as "failed" when
            1. File's contents being modified
    This script will
        1. Make and install the test app
        2. Run the test app
        3. Check  file's contents remain unchanged == 0:
        4. Repeat above for different test scenarios

    Args:
        target: fixture to communicate with the target
        legato: fixture to call useful functions regarding legato
        app_leg: fixture regarding to build, install and remove app
        init_atomicFile: fixture to initialize and clean up environment
    """
    test_app_name = "atomCancel"
    test_app_proc_name = "atomCancelProc"
    hw_file_path = os.path.join(TEST_TOOLS, "testFile.txt")
    test_file_path = init_atomicFile
    test_descriptions = [
        "openReadFlockOK",
        "tryOpenReadFlockOK",
        "createReadFlockOK",
        "tryCreateReadFlockOK",
    ]

    ref_file_path = "/home/root/refFile.txt"
    files.scp([hw_file_path], ref_file_path, target.target_ip)

    for td in test_descriptions:
        files.scp([hw_file_path], test_file_path, target.target_ip)
        legato.clear_target_log()
        legato.runProc(test_app_name, test_app_proc_name, test_file_path, td)
        assert legato.wait_for_log_msg("le_atomFile_Cancel is called", 20) is True
        target.run("diff %s %s" % (test_file_path, ref_file_path))

    swilog.info(
        "\n[PASSED] le_atomFile_Cancel cancels "
        "all changes and closes the file descriptor) for "
        "le_atomFile_Open(, le_atomFile_TryOpen(, le_atomFile_Create("
        " and le_atomFile_TryCreate( with a read file lock"
    )
