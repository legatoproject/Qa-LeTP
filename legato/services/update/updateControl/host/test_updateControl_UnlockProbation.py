"""@package updateControlModule The update control API test.

Set of functions to test the le_updateCtrl_UnLockProbation
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

system_status = ""
old_sys_index = 0
new_sys_index = 0


# ======================================================================================
# Local fixtures
# ======================================================================================
@pytest.fixture()
@pytest.mark.usefixtures("clean_test")
def init_UpdateCrtl(request, legato):
    """Initialize environment and build app.

    Args:
        request: object to access data
        legato: fixture to call useful functions regarding legato
        clean_test: fixture to clean up environment
    """
    test_name = request.node.name.split("[")[0]
    if legato.get_current_system_status() != "good":
        legato.restore_golden_legato()

    if test_name != "L_UpdateCtrl_UnlockProbation_0001":
        # Since the test framwork would change the probation period to 1ms,
        # it is neccessary to change it back to the default (30mins)
        # because this testcase requires to run under probation
        legato.reset_probation_timer()

    # Make install application
    legato.make_install(APP_NAME_01, APP_PATH_01)
    swilog.info("[PASSED] Make and install the test app successfully.")


# ======================================================================================
# Test functions
# ======================================================================================
@pytest.mark.usefixtures("init_UpdateCrtl")
def L_UpdateCtrl_UnlockProbation_0001(target, legato):
    """Verify that le_updateCtrl_UnLockProbation() is ignored if the probation.

    period has already ended and the process who called
    le_updateCtrl_UnLockProbation() is terminated.

    Initial Condition:
        1. Probation period is 10ms
        2. Current system index is "N"

    Test Procedures:
    1. Install the app that invokes le_updateCtrl_UnLockProbation()
    onto the target device
    2. After the probation period, check the current system index is
    "N + 1" and run the app
    3. Check the current system state is marked as "good" and
    the current system index is "N + 1"
    4. Check the app doesn't crash and doesn't exit wilth
    a non-zero value (LE-6183)

    (Notes: the current system index, the current system state and the current
    system status can be verified by the command line "legato status")

    Args:
        target: fixture to communicate with the target
        legato: fixture to call useful functions regarding legato
        init_UpdateCrtl: initial environment and build app
    """
    swilog.step("Test L_UpdateCtrl_UnlockProbation_0001")
    is_tc_passed = False

    # Set the probation period to 1s so that
    # the system status can turn into 'good'
    legato.set_probation_timer(1)

    # Wait 2s to allow the probation period to pass
    time.sleep(2)

    # Set the parameter of the testUpdateCtrl app to "unLockProbation"
    # "1" to run this test case
    target.run(
        "config set apps/%s/procs"
        "/%s/args/1 unLockProbation" % (APP_NAME_01, APP_NAME_01)
    )
    target.run("config set apps/%s/procs" "/%s/args/2 1" % (APP_NAME_01, APP_NAME_01))

    # Store the system index before le_updateCtrl_UnlockProbation()
    # is called when the system is already 'good' for verification
    old_sys_index = legato.get_current_system_index()

    target.run("app start %s" % APP_NAME_01)

    # Store the system index after le_updateCtrl_UnlockProbation()
    # is called when the system is already 'good' for verification
    new_sys_index = legato.get_current_system_index()

    # Store the system status after le_updateCtrl_UnlockProbation()
    # is called when the system is already 'good' for verification
    system_status = legato.get_current_system_status()

    # After le_updateCtrl_UnlockProbation() is called when
    # the system is already 'good', if the current system status is not "good"
    # or the system indexes are different before and after
    # le_updateCtrl_UnlockProbation() is called, mark this test case failed
    if system_status != "good":
        swilog.error(
            "[FAILED] UnlockProbation() modifies the current system"
            " status when the probation period has already ended"
        )
    elif old_sys_index != new_sys_index:
        swilog.error(
            "[FAILED] UnlockProbation() modifies the system index"
            " when the probation period has already ended"
        )
    else:
        swilog.info(
            "[PASSED] UnlockProbation() is ignored when"
            " the probation period has already ended"
        )
        is_tc_passed = True

    assert is_tc_passed, "[FAILED] L_UpdateCtrl_UnlockProbation_0001"
    swilog.info("[PASSED] L_UpdateCtrl_UnlockProbation_0001")


@pytest.mark.usefixtures("init_UpdateCrtl")
def L_UpdateCtrl_UnlockProbation_0002(target, legato):
    """Verify that each call to le_updateCtrl_LockProbation() must be matched.

    with a call to le_updateCtrl_UnLockProbation() in a single process to
    terminate the probation period.

    Initial Conditions:
        1. Probation period is 20s
        2. le_updateCtrl_LockProbation() is verified

    Test Procedures:
        1. Install the app that invokes le_updateCtrl_LockProbation()
        twice first, invokes le_updateCtrl_UnLockProbation()
        once second, waits for 30s and invokes
        le_updateCtrl_UnLockProbation() once again onto the target device
        2. During the probation period, run the app
        3. Check the system is still under probation after 20s
        4. Check the current system state is marked as "good" around 50s

    (Notes: the current system index, the current system state and the current
    system status can be verified by the command line "legato status")

    Args:
        target: fixture to communicate with the target
        legato: fixture to call useful functions regarding legato
        init_UpdateCrtl: initial environment and build app
    """
    swilog.step("Test L_UpdateCtrl_UnlockProbation_0002")
    is_first_unlock_success = False
    is_second_unlock_success = False
    is_tc_passed = False

    # Set the probation period to 20s for verification convenience
    legato.set_probation_timer(20)

    # Set the parameter of the testUpdateCtrl app to "unLockProbation"
    # "2" to run this test case
    target.run(
        "config set apps/%s/procs"
        "/%s/args/1 unLockProbation" % (APP_NAME_01, APP_NAME_01)
    )
    target.run("config set apps/%s/procs" "/%s/args/2 2" % (APP_NAME_01, APP_NAME_01))

    target.run("app start %s" % APP_NAME_01, withexitstatus=True)

    # Store the current system status after the first
    # le_updateCtrl_UnLockProbation() is called
    # when system is under probation for verification
    system_status = legato.get_current_system_status()

    # If the current system status is "good" then, the first
    # le_updateCtrl_UnLockProbation() call clears the probation
    # lock from the first two le_updateCtrl_LockProbation() calls
    if system_status == "good":
        is_first_unlock_success = True

    # Wait for 35s to check wheather the system is under probation
    # after the second le_updateCtrl_UnLockProbation()
    # is called when the system is under probation
    time.sleep(35)

    # Store the current system status after the second
    # le_updateCtrl_UnLockProbation() is called when the
    # system is under probation for verification
    system_status = legato.get_current_system_status()

    # If the current system status is "good" then, the second
    # le_updateCtrl_UnLockProbation() call clears the probation
    # lock from the first two le_updateCtrl_LockProbation() calls
    if system_status == "good":
        is_second_unlock_success = True

    # The first le_updateCtrl_UnLockProbation() call shouldn't clear
    # the probation lock while the last le_updateCtrl_UnLockProbation()
    # call should. Therefore, if the first unlock
    # probation is successful or the second unlock probation is not then,
    # this test case is marked as failed
    if is_first_unlock_success:
        swilog.error(
            "[FAILED] the one UnlockProbation() call releases"
            " the probation lock from the two LockProbation() calls"
        )
    elif not is_second_unlock_success:
        swilog.info(
            "[FAILED] the two UnlockProbation() calls doesn't"
            " release the probation lock from "
            "the two LockProbation() calls"
        )
    else:
        swilog.info(
            "[PASSED] the matching number of UnlockProbation() and "
            "LockProbation() calls in one process"
            " releases the probation lock"
        )
        is_tc_passed = True

    # If TC is not passed, reboot the system to clear
    # the probation lock counter
    # before performing the clean up on the target
    if not is_tc_passed:
        target.reboot(120)

    assert is_tc_passed, "[FAILED] L_UpdateCtrl_UnlockProbation_0002"
    swilog.info("[PASSED] L_UpdateCtrl_UnlockProbation_0002")


@pytest.mark.usefixtures("init_UpdateCrtl")
def L_UpdateCtrl_UnlockProbation_0003(target, legato):
    """Verify that each call to "le_updateCtrl_LockProbation()" must be.

    matched with a call to le_updateCtrl_UnLockProbation() in multiple processes to
    terminate the probation period.

    Initial Conditions:
        1. Probation period is 20s
        2. le_updateCtrl_LockProbation() is verified

    Test Procedures:
        1. Install the app that has two running processes
        onto the target device.
        2. The first process invokes le_updateCtrl_LockProbation() twice,
        waits 30s and followed by two le_updateCtrl_UnLockProbation()
        3. The  second process invokes two le_updateCtrl_UnLockProbation()
        4. During the probation period, run the app
        5. Check the system is still under probation after 20s
        6. Check the current system state is marked as "good" around 50s

    (Notes: the current system index, the current system state and the current
    system status can be verified by the command line "legato status")

    Args:
        target: fixture to communicate with the target
        legato: fixture to call useful functions regarding legato
        init_UpdateCrtl: initial environment and build app
    """
    swilog.step("Test L_UpdateCtrl_UnlockProbation_0003")
    is_first_unlock_success = False
    is_second_unlock_success = False
    is_tc_passed = False

    # Set the probation period to 20s for verification convenience
    legato.set_probation_timer(20)

    # Set the parameter of the testUpdateCtrl process to "unLockProbation"
    # "3" to run this test case
    target.run(
        "config set apps/%s/procs"
        "/%s/args/1 unLockProbation" % (APP_NAME_01, APP_NAME_01)
    )
    target.run("config set apps/%s/procs" "/%s/args/2 3" % (APP_NAME_01, APP_NAME_01))

    # Set the parameter of the otherTestUpdateCtrl process to
    # "unLockProbation" "3" to run this test case
    target.run(
        "config set apps/%s/procs"
        "/otherTestUpdateCtrl/args/1 unLockProbation" % APP_NAME_01
    )
    target.run("config set apps/%s/procs" "/otherTestUpdateCtrl/args/2 3" % APP_NAME_01)

    target.run("app start %s" % APP_NAME_01, withexitstatus=True)

    # Store the current system status for verification
    system_status = legato.get_current_system_status()

    # If the current system status is "good" then,
    # the first two le_updateCtrl_UnLockProbation() calls in
    # the otherTestUpdateCtrl process clears the probation lock from
    # the first two le_updateCtrl_LockProbation() calls
    # in the testUpdateCtrl process
    if system_status == "good":
        is_first_unlock_success = True

    # Wait another 35s to check wheather the system is under probation
    # after the second le_updateCtrl_UnLockProbation() is called in
    # the testUpdateCtrl process when the system is under probation
    time.sleep(35)

    # Store the current system system status for verification
    system_status = legato.get_current_system_status()

    # If the current system status is "good" then, the last
    # le_updateCtrl_UnLockProbation() call in
    # the testUpdateCtrl process clears its probation lock
    # from the first two le_updateCtrl_LockProbation() calls
    if system_status == "good":
        is_second_unlock_success = True

    # The first two le_updateCtrl_UnLockProbation()
    # calls in the otherTestUpdateCtrl process
    # shouldn't clear the probation lock in the testUpdateCtrl process while
    # the last le_updateCtrl_UnLockProbation()
    # call in the testUpdateCtrl process should.
    # Therefore, if the first unlock probation is successful or the  second
    # unlock probation is not then, this test case is marked as failed
    if is_first_unlock_success:
        swilog.error(
            "[FAILED] the two UnlockProbation() calls"
            " in the otherUpdateCtrl process releases"
            " the probation lock from the one LockProbation()"
            " call in the testUpdateCtrl process"
        )
    elif not is_second_unlock_success:
        swilog.error(
            "[FAILED] the two UnlockProbation() calls"
            " doesn't release the probation lock from"
            " its two LockProbation() calls"
        )
    else:
        swilog.info(
            "[PASSED] the matching number of UnlockProbation() and "
            "LockProbation() calls in multiple processes releases"
            " the probation lock"
        )
        is_tc_passed = True

    # If TC is not passed, reboot the system to clear
    # the probation lock counter before performing the clean up on the target
    if not is_tc_passed:
        target.reboot()

    assert is_tc_passed, "[FAILED] L_UpdateCtrl_UnlockProbation_0003"
    swilog.info("[PASSED] L_UpdateCtrl_UnlockProbation_0003")
