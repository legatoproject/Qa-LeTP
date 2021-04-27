"""operation try close test.

Set of functions to test the le_atomFile_Close
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
APP_NAME = "atomClose"
APP_PATH = os.path.join(os.path.join(TEST_RESOURCES, "atomClose"), "atomClose.adef")


# ======================================================================================
# Test functions
# ======================================================================================
@pytest.mark.usefixtures("app_leg")
def L_AtomicFile_Operation_0029(target, legato, init_atomicFile):
    """Purpose: Verify that le_atomFile_Close commits all changes.

    closes the file descriptor
    and returns LE_OK for
    le_atomFile_Open(, le_atomFile_TryOpen(, le_atomFile_Create(
    and le_atomFile_TryCreate( with a write file lock

    Initial condition:
        1. Test app is unsandboxed

    Verification:
        This test case will mark as "failed" when
            1. le_atomFile_Close doesn't commits all changes
            2. le_atomFile_Close doesn't return LE_OK

    This script will
        1. Make and install the test app
        2. Run the test app
        3. Check  "le_atomFile_Close returns LE_OK ..." \
        can be captured from the target's log == 0:
        4. Check  latest changes were committed after \
        le_atomFile_Close is called == 0:
        5. Repeat above for different test scenarios

    :param target: fixture to communicate with the target
    :param legato: fixture to call useful functions regarding legato
    :param app_leg: fixture regarding to build, install and remove app
    :param init_atomicFile: fixture to initialize and clean up environment
    """
    test_app_name = "atomClose"
    test_app_proc_name = "atomCloseProc"
    hw_file_path = os.path.join(TEST_TOOLS, "testFile.txt")
    test_file_path = init_atomicFile
    test_descriptions = [
        "openWrtFlockOK",
        "tryOpenWrtFlockOK",
        "createWrtFlockOK",
        "tryCreateWrtFlockOK",
    ]

    for td in test_descriptions:
        files.scp([hw_file_path], test_file_path, target.target_ip)
        legato.clear_target_log()
        legato.runProc(test_app_name, test_app_proc_name, test_file_path, td)
        assert legato.wait_for_log_msg("le_atomFile_Close is called", 20) is True

        if (
            legato.ssh_to_target(r" cat %s | grep -q \"String Foo\"" % (test_file_path))
            != 0
        ):
            assert 0, (
                "[FAILED] le_atomFile_Close doesn't"
                "commit all changes for test scenario of %s" % td
            )
        exp_log = "le_atomFile_Close returns LE_OK"
        if legato.find_in_target_log(exp_log) is False:
            assert 0, (
                "[FAILED] le_atomFile_Close doesn't"
                "return LE_OK for test scenario of %s" % td
            )

    swilog.info(
        "[PASSED] le_atomFile_Close commits all changes"
        ", closes the file descriptor and returns LE_OK for "
        "le_atomFile_Open(, le_atomFile_TryOpen(,"
        " le_atomFile_Create( and le_atomFile_TryCreate( "
        "with a write file lock"
    )


@pytest.mark.usefixtures("app_leg")
def L_AtomicFile_Operation_0030(target, legato, init_atomicFile):
    """Purpose: Verify that le_atomFile_Close commits all changes.

    closes the file descriptor
    and returns LE_OK for le_atomFile_Open(,
    le_atomFile_TryOpen(, le_atomFile_Create(
    and le_atomFile_TryCreate( with a read file lock

    Initial condition:
        1. Test app is unsandboxed

    Verification:
        This test case will mark as "failed" when
            1. File's contents being modified
            2. le_atomFile_Close doesn't return LE_OK

    This script will
       1. Make and install the test app
       2. Run the test app
       3. Check  "le_atomFile_Close returns LE_OK ..." \
       can be captured from the target's log == 0:
       4. Check  file's contents remain unchanged == 0:
       5. Repeat above for different test scenarios

    :param target: fixture to communicate with the target
    :param legato: fixture to call useful functions regarding legato
    :param app_leg: fixture regarding to build, install and remove app
    :param init_atomicFile: fixture to initialize and clean up environment
    """
    test_app_name = "atomClose"
    test_app_proc_name = "atomCloseProc"
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

        assert legato.wait_for_log_msg("le_atomFile_Close is called", 20) is True

        target.run("diff %s %s" % (test_file_path, ref_file_path))

        exp_log = "le_atomFile_Close returns LE_OK"
        if legato.find_in_target_log(exp_log) is False:
            assert 0, (
                "[FAILED] le_atomFile_Close doesn't return "
                "LE_OK for test scenario of %s" % td
            )

    swilog.info(
        "[PASSED] le_atomFile_Close commits all changes,"
        " closes the file descriptor and returns LE_OK for "
        "le_atomFile_Open(, le_atomFile_TryOpen(,"
        " le_atomFile_Create( and le_atomFile_TryCreate( "
        "with a read file lock"
    )
