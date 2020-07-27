"""@package updateControlModule The update control API test.

Set of functions to test the le_updateCtrl_FailProbation
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


# ======================================================================================
# Local fixtures
# ======================================================================================
@pytest.fixture()
@pytest.mark.usefixtures("clean_test")
def init_UpdateCrtl(request, legato):
    """Initialize and build app.

    Args:
        request: object to access data
        legato: fixture to call useful functions regarding legato
        clean_test: fixture to clean up environment
    """
    test_name = request.node.name.split("[")[0]
    if legato.get_current_system_status() != "good":
        legato.restore_golden_legato()

    old_sys_index = 0

    if test_name == "L_UpdateCtrl_FailProbation_0001":
        # Get the system index from a 'good' system by
        # setting the probation period
        # to 1s to turn the system into 'good'
        legato.set_probation_timer(1)

        # Wait 3s to allow the probation period to pass
        time.sleep(3)

        # Store the current system index of a 'good' system for verification
        old_sys_index = legato.get_current_system_index()

        # Since this test case is required to run under probation,
        # the pre-set probation
        # Period has to be changed to the default, 30mins
        legato.reset_probation_timer()

    legato.make_install(APP_NAME_01, APP_PATH_01)
    swilog.info("[PASSED] Make and install the test app successfully.")

    yield old_sys_index


# ======================================================================================
# Test Functions
# ======================================================================================
def L_UpdateCtrl_FailProbation_0001(target, legato, init_UpdateCrtl):
    """Verify that le_updateCtrl_FailProbation() marks the current system as.

    bad and rolls back to a previous good system when the system is under
    probation.

    Initial Conditions:
        1. Current system state is marked as "good"
        2. Current system index is "N"

    Test Procedures:
        1. Install the app that invokes le_updateCtrl_FailProbation()
        onto the target device
        2. During the probation period, check the current system index
        is "N + 1" and run the app
        3. Check the target device is rebooting
        4. Check the current system state is marked as "good"
        5. Check the current system index is "N"

    (Notes: the current system index, the current system state and
    the current system status can be verified by
    the command line "legato status")

    Args:
        target: fixture to communicate with the target
        legato: fixture to call useful functions regarding legato
        init_UpdateCrtl: initial and build app
    """
    swilog.step("Test L_UpdateCtrl_FailProbation_0001")
    old_sys_index = 0
    new_sys_index = 0
    new_system_status = ""
    old_system_status = ""
    is_tc_passed = False
    is_target_reboot = False

    old_sys_index = init_UpdateCrtl

    # StartTC(target)
    # Set the parameter of the testUpdateCtrl app to
    # "failProbation" "1" to run this test case
    target.run(
        "config set apps/%s/procs/%s/args/1"
        " failProbation" % (APP_NAME_01, APP_NAME_01)
    )
    target.run("config set apps/%s/procs/%s/args/2 1" % (APP_NAME_01, APP_NAME_01))
    time.sleep(5)
    rsp = target.run("app start %s" % APP_NAME_01)
    swilog.info(rsp)

    # Store the system status after le_updateCtrl_FailProbation()
    # is called when the system is
    # under probation for verification
    old_system_status = legato.get_current_system_status()

    # ==========================================================
    # whether the reboot is necessary before the roll-back
    # If this test case is failed then, the system
    # may perform roll-back so, target device will reboot
    # Ticket: LE-5080
    # ==========================================================

    # Wait 10s to check whether the target device is shutting down to reboot
    time.sleep(5)
    if target.wait_for_device_down(10) == 0:
        target.wait_for_reboot(120)
        is_target_reboot = True
    swilog.info(is_target_reboot)
    time.sleep(5)
    # Store the current system index after le_updateCtrl_FailProbation()
    # is called when the system is
    # under probation for verification
    new_sys_index = legato.get_current_system_index()

    # Store the current system status after le_updateCtrl_FailProbation()
    # is called when the system is
    # under probation for verification
    new_system_status = legato.get_current_system_status()

    # Since the behaviours of a system roll-back are
    #   1)Current system index rolls-back to a previous 'good' system index
    #   2)Target device reboot
    #   3)Current system status is marked as 'good' after roll-back
    #   4)Current system status is marked as 'bad' before roll-back
    #   5)Previous 'good' doesn't has the testUpdateCtrl app installed
    # If any of the previous5 behaviours wasn't inspected,
    #  mark this test case failed
    if old_sys_index != new_sys_index:
        swilog.error(
            "[FAILED] FailProbation() doesn't "
            "roll-back when the system is under probation"
        )
    elif new_system_status != "good":
        swilog.error(
            "[FAILED] FailProbation() doesn't roll-back to"
            " a previous 'good' system when the system is"
            " under probation - %s" % new_system_status
        )
    elif old_system_status != "bad":
        swilog.error(
            "[FAILED] FailProbation() doesn't mark the current"
            " system as 'bad' before the roll-back occurred"
            " when the system is under probation"
        )
    elif legato.is_app_exist(APP_NAME_01):
        swilog.error(
            "[FAILED] FailProbation() rolls-back to a system that"
            " doesn't match to a previous 'good' system which"
            " doesn't has the testUpdateCtrl app when"
            " the system is under probation"
        )
    elif is_target_reboot is False:
        swilog.error(
            "[FAILED] FailProbation() doesn't cause the target"
            " to reboot to complete the system roll-back when"
            " the system is under probation"
        )
    else:
        swilog.info(
            "[PASSED] FailProbation() rolls-back to a previous"
            " 'good' system when the system is under probation"
        )
        is_tc_passed = True

    assert is_tc_passed, "[FAILED] L_UpdateCtrl_FailProbation_0001"
    swilog.step("[PASSED] L_UpdateCtrl_FailProbation_0001")


def L_UpdateCtrl_FailProbation_0002(target, legato, init_UpdateCrtl):
    """Verify that le_updateCtrl_FailProbation() is ignored if the probation.

    period has already ended.

    Initial Conditions:
        1. Current system state is marked as "good"
        2. Current system index is "N"
        3. Probation period is 10ms

    Test Procedures:
        1. Install the app that invokes le_updateCtrl_FailProbation()
           onto the target device
        2. After the probation period, run the app
        3. Check the current system state is marked as "good"
        4. Check the current system index is "N + 1"

    (Notes: the current system index, the current system state and
    the current system status can be verified by
    the command line "legato status")

    Args:
        target: fixture to communicate with the target
        legato: fixture to call useful functions regarding legato
        init_UpdateCrtl: initial and build app
    """
    swilog.step("Test L_UpdateCtrl_FailProbation_0002")
    old_sys_index = 0
    new_sys_index = 0
    system_status = ""
    is_tc_passed = False
    is_target_reboot = False
    swilog.debug(init_UpdateCrtl)

    # Start TC2(target)
    # Set the probation period to 1s so that
    # the system status can turn into 'good'
    legato.set_probation_timer(1)

    # Wait 3s to allow the probation period to pass
    time.sleep(3)

    # Set the parameter of the testUpdateCtrl app to "failProbation" "2"
    target.run(
        "config set apps/%s/procs/%s/args/1"
        " failProbation" % (APP_NAME_01, APP_NAME_01)
    )
    target.run(
        "config set apps/%s/procs/$APP_NAME_01/" "args/2 2" % APP_NAME_01,
        withexitstatus=True,
    )

    # Store the current system index of a 'good' system before
    # invoking le_updateCtrl_FailProbation()
    # for verification
    old_sys_index = legato.get_current_system_index()

    target.run("app start %s" % APP_NAME_01, withexitstatus=True)

    # Store the current system index of a 'good' system after
    # le_updateCtrl_FailProbation() was invoked
    # for verification
    new_sys_index = legato.get_current_system_index()

    # Store the current system status after le_updateCtrl_FailProbation()
    # was invoked for verification
    system_status = legato.get_current_system_status()

    time.sleep(3)
    if target.wait_for_device_down(10) == 0:
        target.wait_for_reboot(120)
        is_target_reboot = True

    # After le_updateCtrl_FailProbation() is called when
    # the system is already 'good',
    # if the system TRIED to perform a system roll-back;
    # If the new system index is not identical
    # to the old system index before and after
    # le_updateCtrl_FailProbation() is called;
    # The current system status is not marked as "good".
    # Mark this test case failed

    # ==========================================================
    # whether the reboot is necessary before the roll-back
    # if this test case is failed then, the system
    # may perform roll-back so, target device will reboot
    # Ticket: LE-5080
    # ==========================================================
    if is_target_reboot:
        swilog.error(
            "[FAILED] FailProbation() performs roll-back when"
            " the probation period has already ended"
        )
    elif old_sys_index != new_sys_index:
        swilog.error(
            "[FAILED] FailProbation() modified the system index when"
            " the probation period has already ended"
        )
    elif system_status != "good":
        swilog.info(system_status)
        swilog.error(
            "[FAILED] FailProbation() modified the system status"
            " when the probation period has already ended"
        )
    else:
        swilog.info(
            "[PASSED] FailProbation() is ignored when"
            " the probation period has already ended"
        )
        is_tc_passed = True
    assert is_tc_passed, (
        "[FAILED]"
        " Test \
                                             L_UpdateCtrl_FailProbation_0002"
    )
    swilog.step("[PASSED] Test L_UpdateCtrl_FailProbation_0002")
