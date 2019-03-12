""" @package componentModule Component Definition Files test

    Set of functions to test the Legato component definition files
"""
import os
import swilog
import pytest

__copyright__ = 'Copyright (C) Sierra Wireless Inc.'
# =================================================================================================
# Constants and Globals
# =================================================================================================
# Determine the resources folder (legato apps)
TEST_RESOURCES = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                              'resources')

SERVER_APP_NAME = "printServer"
CLIENT_APP_NAME = "printClient"


# =================================================================================================
# Local fixtures
# =================================================================================================
@pytest.fixture
def init_cleanup_test(legato, tmpdir):
    """
    Initial and clean up the test

    Args:
        legato: fixture to call useful functions regarding legato
        tmpdir: fixture to provide a temporary directory
                unique to the test invocation

    """

    legato.clear_target_log()

    # Go to temp directory
    os.chdir(str(tmpdir))
    app_path = "%s/cdef/helloIpc" % TEST_RESOURCES

    # Create both the client and server app
    legato.make(os.path.join(app_path, SERVER_APP_NAME))
    legato.make(os.path.join(app_path, CLIENT_APP_NAME))

    # Install/start both apps
    legato.install(SERVER_APP_NAME)
    legato.install(CLIENT_APP_NAME)
    yield
    # Remove the apps from the target
    legato.clean(SERVER_APP_NAME)
    legato.clean(CLIENT_APP_NAME)


# =================================================================================================
# Test functions
# =================================================================================================
def L_CDEF_0004(legato, init_cleanup_test):
    """
    This test verifies the provides and requires sections of cdef files

    Args:
        legato: fixture to call useful functions regarding legato
        init_cleanup_test: fixture to init and clean up the test

    """

    # Provide/Require Section:
    # Look for string to ensure apps are communicating using API
    rsp = legato.find_in_target_log("Client says 'Hello, world!'")
    if rsp is True:
        swilog.info("Found Server response string")
    else:
        swilog.error("Did not find Server response string")

    failed_testcases_list = swilog.get_error_list()
    if failed_testcases_list != []:
        assert 0, "Some tests failed:\n%s" % "\n".join(failed_testcases_list)
