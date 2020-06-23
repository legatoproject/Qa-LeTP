"""@package applicationModule Application Definition Files test.

Set of functions to test the Legato application definition files.
"""
import os
import swilog
import pytest

__copyright__ = "Copyright (C) Sierra Wireless Inc."
# ====================================================================================
# Constants and Globals
# ====================================================================================
# Determine the resources folder (legato apps)
TEST_RESOURCES = os.path.join(os.path.abspath(os.path.dirname(__file__)), "resources")
APP_NAME = "version"
VERSION = "14.07.0"
VERSION_APPEND = "Beta.rc1"


# ====================================================================================
# Local fixtures
# ====================================================================================
@pytest.fixture(params=["", VERSION_APPEND])
def init_cleanup_app_version(request, legato, tmpdir):
    """Make application with append version Install application.

    Clean up after the test.

    Args:
        request: object to access data
        legato: fixture to call useful functions regarding legato
        tmpdir: fixture to provide a temporary directory
                unique to the test invocation
    """
    version_append = request.param

    # Go to temp directory
    os.chdir(str(tmpdir))

    make_option = (
        "--append-to-version=%s" % version_append if version_append != "" else ""
    )
    app_path = "%s/adef/version" % TEST_RESOURCES

    # Make and install application
    legato.make(os.path.join(app_path, APP_NAME), option=make_option)
    legato.install(APP_NAME)

    yield {"version_append": version_append}
    legato.clean(APP_NAME)


# ====================================================================================
# Test functions
# ====================================================================================
def L_ADEF_0004(legato, init_cleanup_app_version):
    """Test append version in application definition files.

    Args:
        legato: fixture to call useful functions regarding legato
        init_cleanup_app_version: fixture to initial and cleanup the test
    """
    version_append = init_cleanup_app_version["version_append"]
    extra = "no" if version_append == "" else ""

    swilog.step("Test %s appended" % extra)

    version_to_check = (
        "%s" % VERSION if version_append == "" else "%s.%s" % (VERSION, version_append)
    )

    legato.verify_app_version(APP_NAME, APP_NAME + " " + version_to_check)
