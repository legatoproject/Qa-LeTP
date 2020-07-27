"""@package updateControlModule The update control API test.

Set of functions to test the le_updateCtrl_Allow
"""
import os
import time
import swilog
import pytest

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
@pytest.fixture()
@pytest.mark.usefixtures("clean_test")
def init_UpdateCrtl(legato):
    """Clean up environment and build app.

    Args:
        legato: fixture to call useful functions regarding legato
        clean_test: fixture to clean up environment
    """
    if legato.get_current_system_index() != 0:
        legato.restore_golden_legato()
    # Make install application
    legato.make_install(APP_NAME_01, APP_PATH_01)
    swilog.info("[PASSED] Make and install the test app successfully.")


# ======================================================================================
# Test Functions
# ======================================================================================
@pytest.mark.usefixtures("init_UpdateCrtl")
def L_UpdateCtrl_Allow_0001(target, legato):
    """Verify that le_updateCtrl_Allow() will not allow updates to.

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

    Args:
        target: fixture to communicate with the target
        legato: fixture to call useful functions regarding legato
        init_UpdateCrtl: fixture to clean up environment and build app
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


@pytest.mark.usefixtures("init_UpdateCrtl")
def L_UpdateCtrl_Allow_0002(target, legato):
    """Verify that le_updateCtrl_Allow() will not allow updates to.

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

    Args:
        target: fixture to communicate with the target
        legato: fixture to call useful functions regarding legato
        init_UpdateCrtl: fixture to clean up environment and build app
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


@pytest.mark.usefixtures("clean_test")
def L_UpdateCtrl_Allow_0003(target, legato):
    """Verify that rollback will be called when defers are lifted.

    Initial Conditions:
        1. le_updateCtrl_Defer() is verified
        2. le_updateCtrl_FailProbation() is verified
        3. current system status is marked as 'good'

    Test Procedures:
        1. Install the app that invokes le_updateCtrl_Defer(),
        le_updateCtrl_FailProbation() and le_updateCtrl_Allow()
        onto the target device
        2. Run the app
        3. Check the system is rolling back to previous 'good' system

    Args:
        target: fixture to communicate with the target
        legato: fixture to call useful functions regarding legato
        clean_test: fixture to clean up environment
    """
    swilog.step("Test L_UpdateCtrl_Allow_0003")
    old_sys_index = 0
    new_sys_index = 0
    old_system_status = ""
    new_system_status = ""
    is_target_reboot = False

    # Get the system index from a 'good' system by setting the probation period
    # to 1s to turn the system into 'good'
    legato.set_probation_timer(1)

    # Wait 3s to allow the probation period to pass
    time.sleep(3)

    # Store the system index of a 'good' system
    old_sys_index = legato.get_current_system_index()

    # Since this test case is required to run under probation,
    # the pre-set probation period has to be changed
    # to the default, 30mins
    legato.reset_probation_timer()

    # Begin of the this TC
    legato.make_install(APP_NAME_01, APP_PATH_01)
    swilog.info("[PASSED] Make and install the test app successfully.")

    # Set the parameter of the testUpdateCtrl app to
    # "allow" "3" to run this test case
    target.run("config set apps/%s/procs/%s/args/1 allow" % (APP_NAME_01, APP_NAME_01))
    target.run("config set apps/%s/procs/%s/args/2 3" % (APP_NAME_01, APP_NAME_01))

    target.run("app start %s" % APP_NAME_01, withexitstatus=True)

    # Store the current system status when the system rollback has began
    old_system_status = legato.get_current_system_status()

    # ==========================================================
    # whether the reboot is necessary before the roll-back
    # if this test case is failed then, the system
    # may perform roll-back so, target device will reboot
    # ticket: LE-5080
    # ==========================================================

    # Wait 10s to check whether the target device is shutting down to reboot
    if target.wait_for_device_down(10) == 0:
        # Wait for the reboot is finished
        target.wait_for_reboot(120)
        is_target_reboot = True

    # Store the current system index after le_updateCtrl_FailProbation()
    # is called when the system is
    # under probation for verification
    new_sys_index = legato.get_current_system_index()

    # Store the current system status after the reboot for verification
    new_system_status = legato.get_current_system_status()

    # Since the behaviours of a system roll-back are
    #   1)current system index rolls-back to a previous 'good' system index
    #   2)target device reboot
    #   3)current system status is marked as 'good' after roll-back
    #   4)current system status is marked as 'bad' before roll-back
    #   5)previous 'good' system doesn't has the testUpdateCtrl app installed
    # If any of the previous behaviours wasn't inspected,
    # roll-back wasn't proceed when the defer lock is released and
    # mark this test case failed
    tc_passed = True
    if old_sys_index != new_sys_index:
        swilog.error(
            "sytem index mismatch old:{} != new:{}".format(old_sys_index, new_sys_index)
        )
        tc_passed = False
    if legato.is_app_exist(target, APP_NAME_01):
        swilog.error("app still on target: {}".format(APP_NAME_01))
        tc_passed = False
    if not is_target_reboot:
        swilog.error("target did not reboot")
        tc_passed = False
    if old_system_status != "bad":
        swilog.error("old system status is not bad: {}".format(old_system_status))
        tc_passed = False
    if new_system_status != "good":
        swilog.error("new system status is not good: {}".format(new_system_status))
        tc_passed = False
    assert tc_passed, "[FAILED] rollback is not successful when defers are lifted."
    swilog.info("[PASSED] rollback is successful when defers are lifted")
    swilog.info("[PASSED] Test L_UpdateCtrl_Allow_0003")
