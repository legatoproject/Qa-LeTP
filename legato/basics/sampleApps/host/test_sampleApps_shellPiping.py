"""@package shellPipingAppsModule ShellPiping Sample apps test.

Set of functions to test the ShellPiping sample apps.
"""
import os
import pytest
import swilog

__copyright__ = "Copyright (C) Sierra Wireless Inc."
# ====================================================================================
# Constants and Globals
# ====================================================================================
# Determine the resources folder (legato apps)
LEGATO_ROOT = os.environ["LEGATO_ROOT"]

APP_NAME = "shellPipe"
APP_PATH = "%s/apps/sample/shellPiping/" % LEGATO_ROOT


# ====================================================================================
# Test functions
# ====================================================================================
@pytest.mark.usefixtures("app_leg")
def L_SampleApps_ShellPiping_0001(legato):
    """Script will.

        1. Make and install the test app
        2. Run the test app
        3. Check if expected messages appears in log

    Args:
        legato: fixture to call useful functions regarding legato
        app_leg: fixture to make, install and cleanup application
    """
    swilog.step("Execute L_SampleApps_ShellPiping_0001")
    legato.start(APP_NAME)
    swilog.info("[PASSED] Start app")
    error_msg = "[FAILED] Log is not found."
    assert legato.find_in_target_log("Starting script"), error_msg
    assert legato.find_in_target_log("usr"), error_msg
    assert legato.find_in_target_log("Done script"), error_msg

    swilog.info("[PASSED] L_SampleApps_ShellPiping_0001")
