r"""!HelloWorld Sample apps test.

Set of functions to test the helloWorld sample apps.

@package helloWorldAppsModule
@file
\ingroup sampleAppTests
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

APP_NAME = "helloWorld"
APP_PATH = "%s/apps/sample/%s/" % (LEGATO_ROOT, APP_NAME)


# ====================================================================================
# Test functions
# ====================================================================================
@pytest.mark.usefixtures("app_leg")
def L_SampleApps_HelloWorld_0002(legato):
    """!Script will.

        1. Make and install the test app <br>
        2. Run the test app <br>
        3. Check if expected messages appears in log

    @param legato: fixture to call useful functions regarding legato
    @param app_leg: fixture to make, install and remove application
    """
    text_log = "Hello, world."
    swilog.step("Execute L_SampleApps_ HelloWorld_0002")

    error_msg = "[FAILED] Could not find '%s'" % text_log
    assert legato.find_in_target_log(text_log), error_msg

    swilog.info("[PASSED] L_SampleApps_ HelloWorld_0002")
