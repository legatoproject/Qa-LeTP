""" @package modemDemoAppsModule Modem Demo apps test

    Set of functions to test the Legato modemDemo sample app
"""
import pytest
import os
import time
import swilog
import pexpect

__copyright__ = 'Copyright (C) Sierra Wireless Inc.'
# ==================================================================================================
# Constants and Globals
# ==================================================================================================
LEGATO_ROOT = os.environ["LEGATO_ROOT"]
APP_NAME_L_SampleApps_Sms_0001 = "sms"
APP_PATH_L_SampleApps_Sms_0001 = "%s/apps/sample/%s/" \
                                 % (LEGATO_ROOT, APP_NAME_L_SampleApps_Sms_0001)


# ==================================================================================================
# Functions
# ==================================================================================================
def check_log(logread, text_log):
    """
    Check expected log message.

    Args:
        logread: fixture to check log
        text_log: expected log display on the target

    """
    fail_msg = "[FAILED] Could not find '%s'" % text_log
    assert logread.expect([pexpect.TIMEOUT, text_log], 60) == 1, fail_msg
    swilog.info("[PASSED] Successfully found '%s'" % text_log)


# ==================================================================================================
# Test functions
# ==================================================================================================
@pytest.mark.config("config/uicc/sim.xml")
def L_SampleApps_Sms_0001(target, legato, logread, installapp_cleanup):
    """
    This automated test verifies the sms sample application.

    Args:
        target: fixture to communicate with the target
        legato: fixture to call useful functions regarding legato
        logread: fixture to check log on the target
        installapp_cleanup: fixture to make, install and remove application

    """

    swilog.step("Execute L_SampleApps_Sms_0001")

    phone_num = installapp_cleanup

    # Start the app if it is not running
    if not legato.is_app_running(APP_NAME_L_SampleApps_Sms_0001):
        legato.start(APP_NAME_L_SampleApps_Sms_0001)

    time.sleep(15)

    cmd = "/legato/systems/current/bin/cm sms send %s Test" % phone_num
    exit, rsp = target.run(cmd, timeout=100, withexitstatus=1)
    assert exit == 0, "[FAILED] Send test sms"

    # Check the log for the Rx messages
    check_log(logread, "Message is received from")
    check_log(logread, "Message timestamp is")
    check_log(logread, "Message content: \"Test\"")
    # Check the log for the Tx messages
    check_log(logread, "the message has been successfully sent.")
    check_log(logread,
              "the message has been successfully deleted from storage.")

    swilog.info("[PASSED] L_SampleApps_Sms_0001")
