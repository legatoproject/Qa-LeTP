"""@package componentModule Component Definition Files test.

Set of functions to test the Legato component definition files.
"""
import os
import re
import pytest
import swilog

__copyright__ = "Copyright (C) Sierra Wireless Inc."
# ====================================================================================
# Constants and Globals
# ====================================================================================
# Determine the resources folder (legato apps)
TEST_RESOURCES = os.path.join(os.path.abspath(os.path.dirname(__file__)), "resources")
APP_NAME = "optional_withoutBindings"
APP_PATH = (
    "%s/cdef/interfaceOptions/optional/legatoAPI/clientIPC/mkapp" % TEST_RESOURCES
)


# ====================================================================================
# Local fixtures
# ====================================================================================
@pytest.fixture(autouse=True)
def init_cleanup_test(legato, tmpdir):
    """Init and clean up the test.

    Args:
        legato: fixture to call useful functions regarding legato
        tmpdir: fixture to provide a temporary directory
                unique to the test invocation
    """
    # Go to temp directory
    os.chdir(str(tmpdir))
    yield
    # Clean up on the target
    legato.clean(APP_NAME)


# ====================================================================================
# Test functions
# ====================================================================================
def L_CDEF_0028(target, legato):
    """Verify the binding is not existed after app's deployment.

    when its client-side IPC API is not bounded to any server-side API
    with the interface option: [optional]
    Verification:
        This test case will mark as "failed" when
        1. Arbitrary binding is existed in the output of the command line
        "sdir list"

    This script will
         1. Build and install the test app, optional_withoutBindings
         2. Run the command line in the target, "sdir list"
         3. Check the existence of the binding

    Args:
        target: fixture to communicate with the target
        legato: fixture to call useful functions regarding legato
    """
    cmd = "/legato/systems/current/bin/sdir list"

    # LogClient is the default hardcoded binding which created
    # When any user app has been deployed onto the target
    log_client_binding_name = "LogClient"

    # Make and install
    legato.make_install(APP_NAME, APP_PATH)

    rsp = target.run(cmd)
    if re.search(APP_NAME, rsp):
        if re.search(log_client_binding_name, rsp):
            swilog.info(
                "Arbitrary binding does not exist after app's "
                "deployment when its client-side IPC API is not "
                "bounded to any server-side API with the interface "
                "option: [optional]"
            )
    else:
        swilog.error(
            "Arbitrary binding does not exist after app's deployment "
            "when its client-side IPC API is not bounded to any "
            "server-side API with the interface option: [optional]"
        )

    failed_testcases_list = swilog.get_error_list()
    if failed_testcases_list != []:
        assert 0, "Some tests failed:\n%s" % "\n".join(failed_testcases_list)
