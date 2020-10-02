r"""!Application Definition Files test.

Set of functions to test the Legato application definition files.

@package applicationModule
@defgroup definitionFileTests Definition File Tests

@file
\ingroup definitionFileTests
"""
import os
import pytest
import swilog

__copyright__ = "Copyright (C) Sierra Wireless Inc."
# ====================================================================================
# Constants and Globals
# ====================================================================================
# Determine the resources folder (legato apps)
TEST_RESOURCES = os.path.join(os.path.abspath(os.path.dirname(__file__)), "resources")

APP_NAME = "link_app"
APP_PATH = "%s/adef/link" % TEST_RESOURCES


# ====================================================================================
# Functions
# ====================================================================================
def verify_run_correctly(legato):
    """!Verify the application is run correctly.

    @param legato: Fixture to call useful functions regarding legato
    """
    rsp = legato.find_in_target_log("Server started")
    if rsp:
        swilog.info("Server started.")
    else:
        swilog.error("Server did not start.")

    rsp = legato.find_in_target_log("foo_f is called")
    if rsp:
        swilog.info("C1 started and successfully called foo_f on the server.")
    else:
        swilog.error("C1 may not have called.")

    rsp = legato.find_in_target_log("bar_f is called")
    if rsp:
        swilog.info("C2 started and successfully called bar_f on the server.")
    else:
        swilog.error("C2 may not have called bar_f on the server.")


# ====================================================================================
# Test functions
# ====================================================================================
@pytest.mark.usefixtures("app_leg")
def L_ADEF_0006(legato):
    """!Check link (Validate defect #2472).

    @param legato fixture to call useful functions regarding legato
    @param app_leg fixture to make install application
                 and cleanup it after the test
    """
    verify_run_correctly(legato)

    failed_testcases_list = swilog.get_error_list()
    if failed_testcases_list != []:
        assert 0, "Some tests failed:\n%s" % "\n".join(failed_testcases_list)
