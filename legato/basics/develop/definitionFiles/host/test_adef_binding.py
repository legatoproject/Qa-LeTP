""" @package applicationModule Application Definition Files test

    Set of functions to test the Legato application definition files
"""
import pytest
import os
import time
import swilog

__copyright__ = 'Copyright (C) Sierra Wireless Inc.'
# =================================================================================================
# Constants and Globals
# =================================================================================================
# Determine the resources folder (legato apps)
TEST_RESOURCES = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                              'resources')


# =================================================================================================
# Functions
# =================================================================================================
def verify_run_correctly(legato, should_fail=False):
    """
    Verify the application is running properly or not

    Args:
        legato: fixture to call useful functions regarding legato
        should_fail: the application is run properly or not

    """

    expected = True if should_fail is False else False
    rsp = legato.find_in_target_log("Message received: USER1")
    if rsp != expected:
        swilog.error("USER1 binding")

    rsp = legato.find_in_target_log("Message received: USER2")
    if rsp != expected:
        swilog.error("USER2 binding")


# =================================================================================================
# Local fixtures
# =================================================================================================
@pytest.fixture(params=[("binded", "", False, False),
                        ("unbinded", "", True, False),
                        ("wrongbind", "", True, False),
                        ("dupbinding", "", True, False),
                        ("client", "server", False, False),
                        ("requires", "", False, True)])
def init_cleanup_test(legato, request, tmpdir):
    """
    Initial and clean up the test.

    Args:
        legato: fixture to call useful functions regarding legato
        request: object to read the params
        tmpdir: fixture to provide a temporary directory
                unique to the test invocation

    Returns:
        app_name: first application name
        app_name2: second application name
        make_should_fail: expected status of the building application result
        run_fail: expected status that the application is run
                  properly or not

    """
    app_name = request.param[0]
    app_name2 = request.param[1]
    make_should_fail = request.param[2]
    run_fail = request.param[3]

    # Clear target log when each test starts.
    swilog.step("Start init test")
    legato.clear_target_log()

    # Go to temp directory
    os.chdir(str(tmpdir))

    yield (app_name, app_name2, make_should_fail, run_fail)
    swilog.step("Clean up test")
    swilog.step("Test with application name: %s" % app_name)
    swilog.step("Test with application name: %s" % app_name2)
    # Clean up applications

    if legato.is_app_exist(app_name):
        legato.clean(app_name)
    if app_name2 != "" and legato.is_app_exist(app_name2):
        legato.clean(app_name2)


# =================================================================================================
# Test functions
# =================================================================================================
def L_ADEF_0001(legato, tmpdir, init_cleanup_test):
    """
    Verify that applications are built and run properly or not

    Args:
        legato: fixture to call useful functions regarding legato
        tmpdir: fixture to provide a temporary directory
                unique to the test invocation
        init_cleanup_test: fixture to init and clean up the test

    """
    # Read returned values from the fixture
    app_name = init_cleanup_test[0]
    app_name2 = init_cleanup_test[1]
    make_should_fail = init_cleanup_test[2]
    run_fail = init_cleanup_test[3]

    swilog.step("Test with application name: %s" % app_name)
    swilog.info("Make application status: %s" % make_should_fail)
    swilog.info("Run application status: %s" % run_fail)

    test_path = "%s/adef/binding" % TEST_RESOURCES

    # Make the first application
    legato.make(os.path.join(test_path, app_name),
                "",
                should_fail=make_should_fail)

    # Make the second application
    if app_name2 != "":
        legato.make(os.path.join(test_path, app_name2),
                    "",
                    should_fail=make_should_fail)

    if make_should_fail is True:
        swilog.info("Make app failed as expected.")
        return

    # Install the first application
    legato.install(app_name)

    # Install the second application
    if app_name2 != "":
        legato.install(app_name2)

    time.sleep(15)
    verify_run_correctly(legato, should_fail=run_fail)

    # Get the error list
    failed_testcases_list = swilog.get_error_list()
    if failed_testcases_list != []:
        assert 0, "Some tests failed:\n%s" % "\n".join(failed_testcases_list)
