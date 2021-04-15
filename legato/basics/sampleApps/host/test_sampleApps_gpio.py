"""Gpio Sample apps test.

Set of functions to test the gpioCf3Demo sample apps.
"""
import os
import re
import time
import pytest
from pytest_letp.lib import swilog

__copyright__ = "Copyright (C) Sierra Wireless Inc."
# ====================================================================================
# Constants and Globals
# ====================================================================================
# Determine the resources folder (legato apps)
LEGATO_ROOT = os.environ["LEGATO_ROOT"]

APP_NAME = "gpioCf3Demo"
APP_PATH = "%s/apps/sample/%s/" % (LEGATO_ROOT, APP_NAME)


# ====================================================================================
# Functions
# ====================================================================================
def read_wiocfg(target, gpio_num):
    """Read gpio for linux (16).

    Args:
        target: fixture to communicate with the target
        gpio_num: fixture to provide gpio number
    """
    rsp_wiocfg = target.run_at_cmd("at+wiocfg?", 5, ["OK"])
    swilog.info(rsp_wiocfg)
    rsp_wiocfg = rsp_wiocfg.replace("\r\n", "")

    match_obj = re.match(r"(.*)WIOCFG: %d,(\d{1,2}).*" % gpio_num, rsp_wiocfg, re.M)

    wiocfg_func = ""
    if match_obj:
        wiocfg_func = match_obj.group(2)
        swilog.info("GPIO %d is [%s]" % (gpio_num, wiocfg_func))
    assert wiocfg_func != "", "[FAILED] GPIO %d not configured." % gpio_num

    return wiocfg_func


def set_and_check_wiocfg(target, gpio_num):
    """Set and check gpio for linux (16).

    Args:
        target: fixture to communicate with the target
        gpio_num: fixture to provide gpio number
    """
    wiocfg_func = read_wiocfg(target, gpio_num)

    if wiocfg_func != "16":
        # Set 16 for GPIO
        cmd = "at+wiocfg=%d,16" % gpio_num
        target.run_at_cmd(cmd, 5, ["OK"])

        # Read after set
        wiocfg_func = read_wiocfg(target, gpio_num)
        swilog.info("GPIO %d is [%s]" % (gpio_num, wiocfg_func))

    # Check after read
    error_msg = "[FAILED] GPIO %d not available to linux" % gpio_num
    assert wiocfg_func == "16", error_msg
    swilog.info("[PASSED] GPIO %d is available to linux" % gpio_num)


def check_log(legato, text_log):
    """Check a text in the target logs.

    Args:
        legato: fixture to call useful functions regarding legato
        text_log: fixture to provide a necessary text
    """
    error_msg = "[FAILED] Could not find '%s'" % text_log
    assert legato.find_in_target_log(text_log), error_msg
    swilog.info("[PASSED] Successfully found '%s'" % text_log)


# ====================================================================================
# Local fixtures
# ====================================================================================
@pytest.fixture()
def init_gpio(target):
    """Set, check and restore GPIO.

    Args:
        target: fixture to communicate with the target
    """
    if target.target_name.startswith("ar"):
        pytest.skip("AR devices are not CF3, skipping.")

    if target.target_name.startswith("ar"):
        pytest.skip("AR devices are not CF3, skipping.")

    # Check if gpio 21 is available to linux
    gpio_num_21 = 21
    restore_val_21 = read_wiocfg(target, gpio_num_21)
    set_and_check_wiocfg(target, gpio_num_21)

    # Check if gpio 22 is available to linux
    gpio_num_22 = 22
    restore_val_22 = read_wiocfg(target, gpio_num_22)
    set_and_check_wiocfg(target, gpio_num_22)
    if restore_val_21 != "16" or restore_val_22 != "16":
        target.reboot()

    yield
    if restore_val_21 != "16":
        cmd = "at+wiocfg=%d,%s" % (gpio_num_21, restore_val_21)
        target.run_at_cmd(cmd, 5, ["OK"])
    if restore_val_22 != "16":
        cmd = "at+wiocfg=%d,%s" % (gpio_num_22, restore_val_22)
        target.run_at_cmd(cmd, 5, ["OK"])


# ====================================================================================
# Test functions
# ====================================================================================
@pytest.mark.usefixtures("app_leg", "init_gpio")
def L_SampleApps_Gpio_0001(legato):
    """Validate that the sample app gpioCf3Demo works well.

    and validate LE-10420.

    This script will
        1. Make and install the test app
        2. Run the test app
        3. Check if expected messages appears in log

    Args:
        legato: fixture to call useful functions regarding legato
        init_gpio: fixture to set, check and restore GPIO.
        app_leg: fixture to make, install and remove application
    """
    time.sleep(5)
    swilog.step("Execute L_SampleApps_Gpio_0001")
    # Check to see if app started
    check_log(legato, "Starting process 'gpioCf3Demo'")

    # Check to see if GPIO 21 is assigned
    check_log(legato, "Assigning GPIO 21")

    # Check to see if GPIO 22 is assigned
    check_log(legato, "Assigning GPIO 22")

    # Check to see if GPIO 21 is released
    check_log(legato, "Releasing GPIO 21")

    # Check to see if GPIO 22 is released
    check_log(legato, "Releasing GPIO 22")

    # Check to see if Application 'gpioCf3Demo' has stopped.
    check_log(legato, "Application 'gpioCf3Demo' has stopped.")
    swilog.info("[PASSED] L_SampleApps_Gpio_0001")
