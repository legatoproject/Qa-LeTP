"""@package atomicFileStreamCancelModule atomicFile Stream cancel test.

Set of functions to test the le_atomFile_CancelStream
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
APP_NAME = "atomCancelStream"
APP_PATH = os.path.join(
    os.path.join(TEST_RESOURCES, "atomCancelStream"), "atomCancelStream.adef"
)


# ======================================================================================
# Test functions
# ======================================================================================
@pytest.mark.usefixtures("app_leg")
def L_AtomicFile_Stream_0031(target, legato, init_atomicFile):
    """Purpose: Verify that le_atomFile_CancelStream cancels.

    all changes and close the file
    pointer returned by le_atomFile_OpenStream,
    le_atomFile_TryOpenStream,
    le_atomFile_CreateStream and le_atomFile_TryCreateStream
    with a write file lock

    Initial condition:
       1. Test app is unsandboxed
    Verification:
        This test case will mark as "failed" when
            1. le_atomFile_CancelStream commits all changes
    This script will
        1. Make and install the test app
        2. Run the test app
        3. Check  latest changes weren't committed after
        le_atomFile_CancelStream is called == 0:
        4. Repeat above for different test scenarios

    Args:
        target: fixture to communicate with the target
        legato: fixture to call useful functions regarding legato
        app_leg: fixture regarding to build, install and remove app
        init_atomicFile: fixture to initialize and clean up environment
    """
    test_app_name = "atomCancelStream"
    test_app_proc_name = "atomCancelStreamProc"
    hw_file_path = os.path.join(TEST_TOOLS, "testFile.txt")
    test_file_path = init_atomicFile
    test_descriptions = [
        "openStreamWrtFlockOK",
        "tryOpenStreamWrtFlockOK",
        "createStreamWrtFlockOK",
        "tryCreateStreamWrtFlockOK",
    ]

    ref_file_path = "/home/root/refFile.txt"
    files.scp([hw_file_path], ref_file_path, target.target_ip)

    for td in test_descriptions:
        files.scp([hw_file_path], test_file_path, target.target_ip)
        legato.clear_target_log()
        legato.runProc(test_app_name, test_app_proc_name, test_file_path, td)
        assert legato.wait_for_log_msg("le_atomFile_CancelStream is called", 20) is True
        target.run("diff %s %s" % (test_file_path, ref_file_path))
        swilog.info(
            "[PASSED] le_atomFile_CancelStream cancels"
            " all changes and closes the file pointer) "
            "for le_atomFile_OpenStream(, "
            "le_atomFile_TryOpenStream(, "
            "le_atomFile_CreateStream( and "
            "le_atomFile_TryCreateStream( with a write file lock"
        )


@pytest.mark.usefixtures("app_leg")
def L_AtomicFile_Stream_0032(target, legato, init_atomicFile):
    """Purpose: Verify that le_atomFile_CancelStream cancels.

    all changes and close the file
    pointer returned by le_atomFile_OpenStream,
    le_atomFile_TryOpenStream,
    le_atomFile_CreateStream and le_atomFile_TryCreateStream
    with a read file lock

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
    test_app_name = "atomCancelStream"
    test_app_proc_name = "atomCancelStreamProc"
    hw_file_path = os.path.join(TEST_TOOLS, "testFile.txt")
    test_file_path = init_atomicFile
    test_descriptions = [
        "openStreamReadFlockOK",
        "tryOpenStreamReadFlockOK",
        "createStreamReadFlockOK",
        "tryCreateStreamReadFlockOK",
    ]

    ref_file_path = "/home/root/refFile.txt"
    files.scp([hw_file_path], ref_file_path, target.target_ip)

    for td in test_descriptions:
        files.scp([hw_file_path], test_file_path, target.target_ip)
        legato.clear_target_log()
        legato.runProc(test_app_name, test_app_proc_name, test_file_path, td)
        assert legato.wait_for_log_msg("le_atomFile_CancelStream is called", 20) is True
        target.run("diff %s %s" % (test_file_path, ref_file_path))

    swilog.info(
        "[PASSED] le_atomFile_CancelStream cancels"
        " all changes and closes the file pointer) "
        "for le_atomFile_OpenStream(, "
        "le_atomFile_TryOpenStream(, le_atomFile_CreateStream( and "
        "le_atomFile_TryCreateStream( with a read file lock"
    )
