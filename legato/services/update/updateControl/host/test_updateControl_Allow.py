r"""!The update control API test.

Set of functions to test the le_updateCtrl_Allow

@package updateControlModule
@file
\ingroup updateTests
"""
import os
import time
import pytest
import swilog

__copyright__ = "Copyright (C) Sierra Wireless Inc."
# ======================================================================================
# Constants and Globals
# ======================================================================================
# Determine the resources folder (legato apps)
TEST_RESOURCES = os.path.join(os.path.abspath(os.path.dirname(__file__)), "resources")
APP_PATH_00 = os.path.join(TEST_RESOURCES, "updateCtrlApi")

APP_NAME_01 = "testUpdateCtrl"
APP_PATH_01 = os.path.join(APP_PATH_00, "testUpdateCtrlApp")

APP_NAME_02 = "helloWorld"
APP_PATH_02 = os.path.join(APP_PATH_00, "helloWorldApp")


# ======================================================================================
# Local fixtures
# ======================================================================================
@pytest.fixture(autouse=True)
def install_and_clean_app(legato, clean_test):
    """!Clean up environment and install app.

    @param legato: fixture to call useful functions regarding legato
    @param clean_test: fixture to clean up environment
    """
    assert clean_test
    if legato.get_current_system_index() != 0:
        legato.restore_golden_legato()
    # Make install application
    legato.make_install(APP_NAME_01, APP_PATH_01)
    swilog.info("[PASSED] Make and install the test app successfully.")
    yield
    # Clean environment
    for app_name in [APP_NAME_01, APP_NAME_02]:
        # Stop the app if it is running
        if legato.is_app_running(app_name):
            legato.stop(app_name)
        legato.clean(app_name)


# ======================================================================================
# Test Functions
# ======================================================================================
def L_UpdateCtrl_Allow_0001(target, legato):
    """!Verify that le_updateCtrl_Allow() will not allow updates to.

    go ahead until no clients are deferring updates in a single process

    Initial Conditions:
        1. le_updateCtrl_Defer() is verified

    Test Procedures:
        1. Install the first app that invokes le_updateCtrl_Defer()
        twice first, invokes le_updateCtrl_Allow()  once second
        , waits for 20s and invokes le_updateCtrl_Allow()
        once again onto the target device
        2. Install the second app (e.g. helloWorld) onto the target device
        3. Check 2. is unsuccessful
        4. After 20s, install the second app again
        5. Check 5. is successful

    @param target: fixture to communicate with the target
    @param legato: fixture to call useful functions regarding legato
    @param init_UpdateCrtl: fixture to clean up environment and build app
    """
    swilog.step("Test L_UpdateCtrl_Allow_0001")

    # Set the parameter of the testUpdateCtrl app to
    # "allow" "1" to run this test case
    target.run("config set apps/%s/procs/%s/args/1 allow" % (APP_NAME_01, APP_NAME_01))
    target.run("config set apps/%s/procs/%s/args/2 1" % (APP_NAME_01, APP_NAME_01))

    status, rsp = target.run("app start %s" % APP_NAME_01, withexitstatus=True)
    swilog.debug(rsp)
    assert status == 0, "[FAILED] App could not be started."

    # Perform the first system update attempt to
    # the system by installing the new helloWorld app
    # If the installtion was successful then,
    # the first update attempt is proceed
    legato.make(APP_NAME_02, APP_PATH_02)
    legato.install(APP_NAME_02, APP_PATH_02, should_fail=True)

    # Wait for 20s so that the last le_updateCtrl_Allow() will be called
    time.sleep(20)

    # Perform the second update to the system by
    # installing the new helloWorld app again
    # If the installation was successful then,
    # the second update attempt is proceed
    legato.make_install(APP_NAME_02, APP_PATH_02)

    # For the first system update attempt , the first le_updateCtrl_Allow()
    # call shouldn't clear the defer lock
    # while the last le_updateCtrl_Allow() call should.
    # Therefore, if the first system update attempt is successful or the
    # second system update attempt is not then,
    # This test case is marked as failed
    swilog.info(
        "[PASSED] the matching number of Allow() and Defer()"
        " calls in one process releases the defer lock"
    )

    swilog.info("[PASSED] Test L_UpdateCtrl_Allow_0001")


def L_UpdateCtrl_Allow_0002(target, legato):
    """!Verify that le_updateCtrl_Allow() will not allow updates to.

    go ahead until no clients are deferring updates in multiple processes

    Initial Conditions:
        1. le_updateCtrl_Defer() is verified

    Test Procedures:
        1. Install the first app that
        has two running processes onto the target device
        2. The first process invokes le_updateCtrl_Defer() twice,
        waits 20 seconds and followed by two le_updateCtrl_Allow()
        3. The second process invokes two le_updateCtrl_Allow()
        4. Run the app
        5. Install the second app (e.g. helloWorld)
        6. Check 5. is unsuccessful
        7. After 20 seconds, install the second app again
        8. Check 7. is successful

    @param target: fixture to communicate with the target
    @param legato: fixture to call useful functions regarding legato
    @param init_UpdateCrtl: fixture to clean up environment and build app
    """
    swilog.step("Test L_UpdateCtrl_Allow_0002")

    # Set the parameter of the testUpdateCtrl process to
    # "allow" "2" to run this test case

    target.run("config set apps/%s/procs/testUpdateCtrl" "/args/1 allow" % APP_NAME_01)
    target.run("config set apps/%s/procs/testUpdateCtrl" "/args/2 2" % APP_NAME_01)

    # Set the parameter of the otherTestUpdateCtrl process to
    # "allow" "2" to run this test case
    target.run(
        "config set apps/%s/procs/" "otherTestUpdateCtrl/args/1 allow" % APP_NAME_01
    )

    target.run(
        "config set apps/%s/procs/" "otherTestUpdateCtrl/args/1 allow" % APP_NAME_01
    )
    target.run("config set apps/%s/procs/otherTestUpdateCtrl" "/args/2 2" % APP_NAME_01)

    status, rsp = target.run("app start %s" % APP_NAME_01, withexitstatus=True)
    swilog.debug(rsp)
    assert status == 0, "[FAILED] App could not be started."

    # Perform the first system update attempt to
    # the system by installing the new helloWorld app
    # if the installation was successful,
    # the first update attempt is proceed
    legato.make(APP_NAME_02, APP_PATH_02)
    legato.install(APP_NAME_02, APP_PATH_02, should_fail=True)

    # Wait for 20s so that the last le_updateCtrl_Allow()
    # call in the testUpdateCtrl process
    # will be invoked
    time.sleep(20)

    # Perform the second system update attempt to
    # the system by installing the new helloWorld app again
    # if the installation was successful, the first update attempt is proceed
    legato.make_install(APP_NAME_02, APP_PATH_02)

    # For the first system update attempt ,
    # the two le_updateCtrl_Allow() calls in the otherUpdateCtrl process
    # shouldn't clear the defer lock from the testUpdateCtrl process while
    # the last le_updateCtrl_Allow() call
    # in the testUpdateCtrl process should. Therefore,
    # if the first system update attempt is successful or the
    # second system update attempt is not then,
    # This test case is marked as failed
    swilog.info(
        "[PASSED] the matching number of Allow() and Defer()"
        " calls in multiple processes releases the defer lock"
    )

    swilog.info("[PASSED] Test L_UpdateCtrl_Allow_0002")
