""" @package dataHubAppsModule DataHub Sample apps test

    Set of functions to test the Legato DataHub sample apps
"""
import os
import swilog
import pexpect

__copyright__ = 'Copyright (C) Sierra Wireless Inc.'
# ==================================================================================================
# Constants and Globals
# ==================================================================================================
LEGATO_ROOT = os.environ["LEGATO_ROOT"]

APP_PATH_L_SampleApps_DataHub_0001 = "%s/apps/sample/dataHub/" % (LEGATO_ROOT)


# ==================================================================================================
# Test functions
# ==================================================================================================
def L_SampleApps_DataHub_0001(target, legato, installapp_cleanup):
    """
    Test sample dataHub

    Args:
        target: fixture to communicate with
            the target ar758x/ar759x/wp76xx/wp77xx/wp85
        legato: fixture to call useful functions regarding legato
        installsys_cleanup: this function is called from the fixture
            in conftest.py, that will make and install sample app

    """

    data_hub_app = "dataHub"
    actuator_app = "actuator"
    sensor_app = "sensor"

    # Check app is running
    failed_msg = "[FAILED] Status of '%s' is not correct" % data_hub_app
    assert ("[running]" in legato.get_app_status(data_hub_app)), failed_msg
    failed_msg = "[FAILED] Status of '%s' is not correct" % actuator_app
    assert ("[running]" in legato.get_app_status(actuator_app)), failed_msg
    failed_msg = "[FAILED] Status of '%s' is not correct" % sensor_app
    assert ("[running]" in legato.get_app_status(sensor_app)), failed_msg

    # Alias datahub
    cmd = "alias dhub=/legato/systems/current/appsWriteable/dataHub/bin/dhub\n"
    target.run(cmd)

    # Enable the temperature sensor
    cmd = "dhub set override /app/%s/temperature/enable true" % sensor_app
    target.run(cmd)

    # Set period time for temperature sensor in sensor_app and check data will
    # Update after timer expired.
    cmd = "dhub set override /app/%s/temperature/period 1\n" % sensor_app
    target.run(cmd)

    # Watch /value path. data will update in every 1s
    cmd = "dhub watch --json /app/%s/temperature/value\n" % sensor_app
    target.send(cmd)
    for i in range(10):
        data = target.expect_in_order(["{", "ts", "val", "}"], timeout=1.1)
        swilog.info(data)

    # Execute ctrl C
    target.sendcontrol('c')

    # Set period time for counter of sensor_app
    # Check data will not update as default enable is false
    cmd = "dhub set override /app/%s/counter/period 1\n" % sensor_app
    target.run(cmd)

    # Watch /value path. data will NOT update
    cmd = "dhub watch --json /app/%s/counter/value\n" % sensor_app
    target.send(cmd)
    id = target.expect([pexpect.TIMEOUT, "ts"], timeout=10)
    assert id == 0
    swilog.info("[PASSED] timeout received")

    # Execute ctrl C
    target.sendcontrol('c')

    # Now Enable counter and watch /value path. data will update in every 1s
    cmd = "dhub set override /app/%s/counter/enable true\n" % sensor_app
    target.run(cmd)

    # Watch /value path. data will update in every 1s
    cmd = "dhub watch --json /app/%s/counter/value\n" % sensor_app
    target.send(cmd)
    for i in range(10):
        data = target.expect_in_order(["{", "ts", "val", "}"], timeout=1.1)
        swilog.info(data)

    # Execute ctrl C
    target.sendcontrol('c')

    # Now disable
    cmd = "dhub set override /app/%s/counter/enable false\n" % sensor_app
    target.run(cmd)

    # Check no asset failed in actuator_app. App in status running
    failed_msg = "[FAILED] Status of '%s' is not correct" % actuator_app
    assert ("[running]" in legato.get_app_status(actuator_app)), failed_msg

    # Test actuator_app with path dummy/output will change to placeholder
    cmd = "dhub list /app/%s\n" % actuator_app
    target.send(cmd)
    expect_value = "output <placeholder> = \"A Default Value\""
    assert target.expect_in_order(["%s" % expect_value], timeout=10)

    swilog.info("[PASSED] L_SampleApps_DataHub_0001")
