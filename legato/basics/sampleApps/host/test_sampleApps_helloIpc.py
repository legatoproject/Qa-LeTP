"""HelloIpc Sample apps test.

Set of functions to test the HelloIpc sample apps.
"""
import os
import pytest
from pytest_letp.lib import swilog

__copyright__ = "Copyright (C) Sierra Wireless Inc."
# ====================================================================================
# Constants and Globals
# ====================================================================================
# Determine the resources folder (legato apps)
LEGATO_ROOT = os.environ["LEGATO_ROOT"]
APP_PATH_L_SampleApps_HelloIpc_0001 = "%s/apps/sample/helloIpc/" % LEGATO_ROOT


# ====================================================================================
# Test functions
# ====================================================================================
@pytest.mark.usefixtures("installapp_cleanup")
def L_SampleApps_HelloIpc_0001(legato):
    """Script will.

        1. Make and install the test app
        2. Run the test app
        3. Check if expected messages appears in log

    Args:
        legato: fixture to call useful functions regarding legato
        installapp_cleanup: fixture to make, install and remove application
    """
    swilog.step("Execute L_SampleApps_HelloIpc_0001")

    text_log1 = "Asking server to print 'Hello, world!'"
    text_log2 = "Hello, world."

    assert legato.find_in_target_log(text_log1), "[FAILED] Could not find out the log"
    swilog.info("[PASSED] Found client request string")

    assert legato.find_in_target_log(text_log2), "[FAILED] Could not find out the log"
    swilog.info("[PASSED] Found server response string")

    swilog.info("[PASSED] L_SampleApps_HelloIpc_0001")
