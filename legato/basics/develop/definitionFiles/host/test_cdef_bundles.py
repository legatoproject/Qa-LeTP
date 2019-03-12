""" @package bundlesComponentModule Component Definition Files test

    Set of functions to test the Legato component definition files
"""
import pytest
import os
import time
import swilog
import shutil

__copyright__ = 'Copyright (C) Sierra Wireless Inc.'
# =================================================================================================
# Constants and Globals
# =================================================================================================
# Determine the resources folder (legato apps)
TEST_RESOURCES = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                              'resources')

APP_NAME = "bundles"
TEST_FOLDER = "testFolder"
TEST_FILE = "testFile1.txt"


# =================================================================================================
# Functions
# =================================================================================================
def is_file_on_target(target, path, file_name):
    """
    Checks for <file> relative to path

    Agrs:
        legato: fixture to call useful functions regarding legato
        path: path of file
        file_name: the name of file

    """

    exit, rsp = target.run("[ -f %s/%s ]" % (path, file_name),
                           withexitstatus=1)

    if exit == 0:
        swilog.info("Found bundled file %s" % file_name)
    else:
        swilog.error("Could not find bundled file %s" % file_name)


def is_directory_on_target(target, path, directory):
    """
    Checks for <directory> relative to path

    Agrs:
        target: fixture to communicate with the target
        path: path of directory
        directory: name of directory

    """

    exit, rsp = target.run("[ -d %s/%s ]" % (path, directory),
                           withexitstatus=1)
    if exit == 0:
        swilog.info("Found bundled directory %s" % directory)
    else:
        swilog.error("Could not find bundled directroy %s" % directory)


# =================================================================================================
# Local fixtures
# =================================================================================================
@pytest.fixture(scope='function')
def test_init(legato):
    """
    Fixture to init and clean up the test

    Agrs:
        legato: fixture to call useful functions regarding legato

    """

    os.chdir("%s/cdef/bundles" % TEST_RESOURCES)
    legato.clear_target_log()

    # Create test file to include in bundles "file" section
    with open("bundlesComponent/%s" % TEST_FILE, "a"):
        os.utime("bundlesComponent/%s" % TEST_FILE, None)

    # Create test directory with contents to include in bundles "dir" section
    if not os.path.exists("bundlesComponent/%s" % TEST_FOLDER):
        os.makedirs("bundlesComponent/%s" % TEST_FOLDER)

    with open("bundlesComponent/%s/file1.txt" % TEST_FOLDER, "a"):
        os.utime("bundlesComponent/%s/file1.txt" % TEST_FOLDER, None)

    if not os.path.exists("bundlesComponent/%s/folder1" % TEST_FOLDER):
        os.makedirs("bundlesComponent/%s/folder1" % TEST_FOLDER)

    with open("bundlesComponent/%s/folder1/file2.txt" % TEST_FOLDER, "a"):
        os.utime("bundlesComponent/%s/folder1/file2.txt" % TEST_FOLDER, None)

    yield
    # Remove the apps from the target
    legato.clean(APP_NAME)

    # Remove the created file and directory
    shutil.rmtree("%s/cdef/bundles/bundlesComponent/%s"
                  % (TEST_RESOURCES, TEST_FOLDER))
    os.remove("%s/cdef/bundles/bundlesComponent/%s"
              % (TEST_RESOURCES, TEST_FILE))


# =================================================================================================
# Test functions
# =================================================================================================
def L_CDEF_0001(target, legato, tmpdir, test_init):
    """
    This test verifies the functionality of the "bundles" section
    in cdef files.

    Agrs:
        target: fixture to communicate with the target
        legato: fixture to call useful functions regarding legato
        tmpdir: fixture to provide a temporary directory
                unique to the test invocation
        test_init: fixture to init and clean up the test

    """

    # Go to temp directory
    os.chdir(str(tmpdir))
    legato.make_install(APP_NAME, "%s/cdef/bundles" % TEST_RESOURCES)

    # Check that bundled file was included
    path = "/legato/systems/current/appsWriteable/%s/bin" % APP_NAME
    is_file_on_target(target, path, TEST_FILE)

    # Check that bundled directory and its contents were included
    is_directory_on_target(target, path, TEST_FOLDER)
    is_file_on_target(target, path, "%s/file1.txt" % TEST_FOLDER)
    is_directory_on_target(target, path, "%s/folder1" % TEST_FOLDER)
    is_file_on_target(target, path, "%s/folder1/file2.txt" % TEST_FOLDER)

    failed_testcases_list = swilog.get_error_list()
    if failed_testcases_list != []:
        assert 0, "Some tests failed:\n%s" % "\n".join(failed_testcases_list)
