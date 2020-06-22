"""@package updateControlModule The update control API test.

Set of functions to test the le_updateCtrl_MarkGood
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
# Functions
# ======================================================================================
@pytest.fixture()
@pytest.mark.usefixtures("clean_test")
def init_UpdateCrtl(request, legato):
    """Initialize and build app for testing.

    Args:
        request: object to access data
        legato: fixture to call useful functions regarding legato
        clean_test: fixture to clean up environment
    """
    test_name = request.node.name.split("[")[0]
    if legato.get_current_system_index() != 0:
        legato.restore_golden_legato()
    old_sys_index = 0

    # Clear the target log since this test case require
    # the context from the target log for verification
    legato.clear_target_log()

    if test_name not in ("L_UpdateCtrl_MarkGood_0005", "L_UpdateCtrl_MarkGood_0006"):
        # Since the test framework would change the probation period to 1ms,
        # it is necessary to change it
        # back to the default (30mins) because this test case is
        # required to run under probation
        legato.reset_probation_timer()

        # Store the current system index before running
        # this test case for verification
        old_sys_index = legato.get_current_system_index()

    # Make install application
    legato.make_install(APP_NAME_01, APP_PATH_01)
    swilog.info("[PASSED] Make and install the test app successfully.")

    yield old_sys_index


def end_test(is_tc_passed, request):
    """Verify the result of test case.

    Args:
        is_tc_passed: status of test case
        request: object to access data
    """
    test_name = request.node.name.split("[")[0]
    assert is_tc_passed, "[FAILED] %s" % test_name
    swilog.info("[PASSED] Test %s" % test_name)


# ======================================================================================
# Test functions
# ======================================================================================
def L_UpdateCtrl_MarkGood_0001(target, request, legato, init_UpdateCrtl):
    """Verify that le_updateCtrl_MarkGood(True) returns LE_OK, marks current.

    system as 'good' and terminates probation period when the system is under
    probation.

    Initial Condition:
        1. Current system is under probation
        2. Current system index is "N"

    Test Procedures:
        1. Install the app that invokes le_updateCtrl_MarkGood(True)
        onto the target device
        2. During the probation period, run the app
        3. Check the current system index is "N+ 1"
        and the current system state is marked as "good"
        4. Check "return LE_OK : The system was marked Good"
        is shown from system log

    (Notes: the current system index, the current system state
    and the current system status can be verified by
    the command line "legato status")

    Args:
        target: fixture to communicate with the target
        request: object to access data
        legato: fixture to call useful functions regarding legato
        init_UpdateCrtl: initial and build app for testing
    """
    swilog.step("Test L_UpdateCtrl_MarkGood_0001")
    old_sys_index = 0
    new_sys_index = 0
    is_leok_return = False
    is_tc_passed = False

    old_sys_index = init_UpdateCrtl

    # Store the current system index which refers to the index
    # after the testUpdateCtrl app has installed onto the target
    new_sys_index = legato.get_current_system_index()

    # Set the parameter of the testUpdateCtrl app to "markGood"
    # "1" to run this test case
    target.run(
        "config set apps/%s/procs/%s/args/1" " markGood" % (APP_NAME_01, APP_NAME_01)
    )
    target.run("config set apps/%s/procs/%s/args/2 1" % (APP_NAME_01, APP_NAME_01))

    target.run("app start %s" % APP_NAME_01, withexitstatus=True)

    # Store the current system status after le_updateCtrl_MarkGood(True)
    # is called during the probation period for verification
    system_status = legato.get_current_system_status()

    # Capture "return LE_OK: The system was marked Good" from the system log
    # after le_updateCtrl_MarkGood(True) is called during the
    # probation period for verification
    if legato.find_in_target_log("return LE_OK:" " The system was marked Good"):
        is_leok_return = True

    # After le_updateCtrl_MarkGood(True) is called during
    # the probation period, if the current system status
    # is not marked as "good"; "return LE_OK:
    # The system was marked Good" wasn't captured in the system log;
    # The current system index is not greater than
    # the system index before running this test case by 1, mark
    # This test case failed
    if is_leok_return is False:
        swilog.error(
            "[FAILED] MarkGood(True) doesn't return"
            " LE_OK when system is under probation "
            "and without any probation lock"
        )
    elif system_status != "good":
        swilog.error(
            "[FAILED] MarkGood(True) doesn't mark the current system"
            " as 'good' when the system is under probation and"
            " without any probation lock"
        )
    elif (new_sys_index - old_sys_index) != 1:
        swilog.error(
            "[FAILED] MarkGood(True) doesn't mark the current system"
            " as 'good' when the system is under probation and"
            " without any probation lock"
        )
    else:
        swilog.info(
            "[PASSED] MarkGood(True) marks the current system"
            " as 'good' and returns LE_OK when the system"
            " is under probation and without any probation lock"
        )
        is_tc_passed = True

    end_test(is_tc_passed, request)


def L_UpdateCtrl_MarkGood_0002(target, request, legato, init_UpdateCrtl):
    """Verify that le_updateCtrl_MarkGood(False) returns LE_OK, marks current.

    system as 'good' and terminates probation period when the system is under
    probation.

    Initial Condition:
        1. Current system is under probation
        2. Current system index is "N"

    Test Procedures:

        1. Install the app that invokes le_updateCtrl_MarkGood(False)
        onto the target device
        2. During the probation period, run the app
        3. Check the current system index is "N+ 1" and
        the current system state is marked as "good"
        4. Check "return LE_OK : The system was marked Good"
        is shown from system log

    (Notes: the current system index, the current system state
    and the current system status can be verified by
    the command line "legato status")

    Args:
        target: fixture to communicate with the target
        request: object to access data
        legato: fixture to call useful functions regarding legato
        init_UpdateCrtl: initial and build app for testing
    """
    swilog.step("Test L_UpdateCtrl_MarkGood_0002")
    old_sys_index = 0
    new_sys_index = 0
    is_leok_return = False
    is_tc_passed = False
    old_sys_index = init_UpdateCrtl

    # Store the current system index which refers to the index
    # after the testUpdateCtrl app has installed onto the target
    new_sys_index = legato.get_current_system_index()

    # Set the parameter of the testUpdateCtrl app to
    # "markGood" "2" to run this test case
    target.run(
        "config set apps/%s/procs/%s/args/1" " markGood" % (APP_NAME_01, APP_NAME_01)
    )
    target.run("config set apps/%s/procs/%s/args/2 2" % (APP_NAME_01, APP_NAME_01))

    target.run("app start %s" % APP_NAME_01, withexitstatus=True)

    # Store the current system status after le_updateCtrl_MarkGood(False)
    # is called during the probation period for verification
    system_status = legato.get_current_system_status()

    # Capture "return LE_OK: The system was marked Good" from the system log
    # after after le_updateCtrl_MarkGood(False) is called
    # during the probation period for verification
    if legato.find_in_target_log("return LE_OK:" " The system was marked Good"):
        is_leok_return = True

    # After le_updateCtrl_MarkGood(True) is called during
    # the probation period, if the current system status
    # is not marked as "good"; "return LE_OK:
    # The system was marked Good" is not appeared in the system log;
    # The current system index is not greater than the system index
    # before running this test case by 1, mark
    # This test case failed
    if is_leok_return is False:
        swilog.error(
            "[FAILED] MarkGood(False) doesn't return LE_OK when"
            " system is under probation and"
            " without any probation lock"
        )
    elif system_status != "good":
        swilog.error(
            "[FAILED] MarkGood(False) doesn't mark the current"
            " system as 'good' when the system is under"
            " probation and without any probation lock"
        )
    elif (new_sys_index - old_sys_index) != 1:
        swilog.error(
            "[FAILED] MarkGood(False) doesn't mark the current"
            " system as 'good' when the system is under"
            " probation and without any probation lock"
        )
    else:
        swilog.info(
            "[PASSED] MarkGood(False) marks the current system"
            " as 'good' and returns LE_OK when the system"
            " is under probation and without any probation lock"
        )
        is_tc_passed = True

    end_test(is_tc_passed, request)


def L_UpdateCtrl_MarkGood_0003(target, request, legato, init_UpdateCrtl):
    """Verify that le_updateCtrl_MarkGood(True) returns LE_OK to set current.

    system 'good' even if someone holds a probation lock.

    Initial Condition:
        1. le_updateCtrl_LockProbation() is verified
        2. Current system index is "N"

    Test Procedures:
        1. Install the app that invokes le_updateCtrl_LockProbation() first
        and  le_updateCtrl_MarkGood(True)  second onto the target device
        2. During the probation period, run the app
        3. Check the current index is "N + 1" and
        the current system state is marked as "good"
        4. Check "return LE_OK : The system was marked Good" is shown
        from system log

    (Notes: the current system index, the current system state
    and the current system status can be verified by
    the command line "legato status")

    Args:
        target: fixture to communicate with the target
        request: object to access data
        legato: fixture to call useful functions regarding legato
        init_UpdateCrtl: initial and build app for testing
    """
    swilog.step("Test L_UpdateCtrl_MarkGood_0003")
    old_sys_index = 0
    new_sys_index = 0
    is_leok_return = False
    is_tc_passed = False

    old_sys_index = init_UpdateCrtl

    # Set the parameter of the testUpdateCtrl app to "markGood"
    # "3" to run this test case
    target.run(
        "config set apps/%s/procs/%s/args/1" " markGood" % (APP_NAME_01, APP_NAME_01)
    )
    target.run("config set apps/%s/procs/%s/args/2 3" % (APP_NAME_01, APP_NAME_01))

    target.run("app start %s" % APP_NAME_01, withexitstatus=True)

    # Now, the current system has a probation lock
    # store the current system index after le_updateCtrl_MarkGood(True)
    # is called when there is a probation lock for verification
    new_sys_index = legato.get_current_system_index()

    # Store the current system status after le_updateCtrl_MarkGood(True)
    # is called when there is a probation lock for verification
    system_status = legato.get_current_system_status()

    # Capture "return LE_OK: The system was marked Good" from
    # the system log after le_updateCtrl_MarkGood(True) is called
    # when there is a probation lock for verification
    if legato.find_in_target_log("return LE_OK:" " The system was marked Good"):
        is_leok_return = True

    # After le_updateCtrl_MarkGood(True) is
    # called when there is a probation lock,
    # if the current system status is not marked as "good";
    # "return LE_OK: The system was marked Good"
    # is not appeared in the system log; the current system index
    # is not greater than the system index
    # before running this test case by 1, mark this test case failed
    if is_leok_return is False:
        swilog.error(
            "[FAILED] MarkGood(True) doesn't return LE_OK"
            " when system is under probation"
            " and there is a probation lock"
        )
    elif system_status != "good":
        swilog.error(
            "[FAILED] MarkGood(True) doesn't mark the current system"
            " as 'good' when the system is under probation and"
            " there is a probation lock"
        )
    elif (new_sys_index - old_sys_index) != 1:
        swilog.error(
            "[FAILED] MarkGood(True) doesn't mark the current system"
            " as 'good' when the system is under probation and"
            " there is a probation lock"
        )
    else:
        swilog.info(
            "[PASSED] MarkGood(True) marks the current system"
            " as 'good' when the system is under probation"
            " and there is a probation lock"
        )
        is_tc_passed = True

    # After StartTC, the current system is marked as
    # "good' and the current system holds a probation lock
    # reboot the system to clear the probation lock
    # before performing the clean up on the target
    target.reboot()
    end_test(is_tc_passed, request)


def L_UpdateCtrl_MarkGood_0004(target, request, legato, init_UpdateCrtl):
    """Verify that le_updateCtrl_MarkGood(False) returns LE_BUSY if someone.

    holds a probation lock.

    Initial Condition:
        1. le_updateCtrl_LockProbation() is verified
        current system is under probation

    Test Procedures:
        1. Install the app that invokes le_updateCtrl_LockProbation()
        first and  le_updateCtrl_MarkGood(False)
        second onto the target device.
        2. During the probation period, run the app
        3. Check "return LE_BUSY: Someone holds
        a probation lock" is shown from system log
        4. Check the system is under probation

    (Notes: the current system index, the current system state
    and the current system status can be verified by
    the command line "legato status")

    Args:
        target: fixture to communicate with the target
        request: object to access data
        legato: fixture to call useful functions regarding legato
        init_UpdateCrtl: initial and build app for testing
    """
    swilog.step("Test L_UpdateCtrl_MarkGood_0004")
    old_sys_index = 0
    new_sys_index = 0
    is_lebusy_return = False
    is_tc_passed = False

    old_sys_index = init_UpdateCrtl

    # Set the parameter of the testUpdateCtrl app
    # to "markGood" "4" to run this testcase
    target.run(
        "config set apps/%s/procs/%s/args/1 markGood" % (APP_NAME_01, APP_NAME_01)
    )
    target.run("config set apps/%s/procs/%s/args/2 4" % (APP_NAME_01, APP_NAME_01))

    rsp = target.run("app start %s" % APP_NAME_01, withexitstatus=True)
    swilog.info(rsp)

    # Now, the current system has a probation lock
    # store the current system index after after le_updateCtrl_MarkGood(False)
    # is called when there is a probation lock for verification
    new_sys_index = legato.get_current_system_index()

    # Store the current system status after le_updateCtrl_MarkGood(False)
    # is called when there is a probation lock for verification
    system_status = legato.get_current_system_status()

    # Capture "return LE_BUSY: Someone holds a probation lock"
    # from the system log after le_updateCtrl_MarkGood(False) is called when
    # there is a probation lock for verification
    if legato.find_in_target_log("return LE_BUSY:" " Someone holds a probation lock"):
        is_lebusy_return = True

    # After le_updateCtrl_MarkGood(False) is called when there is a probation
    # lock, if the current system status is not under probation;
    # "return LE_BUSY: Someone holds a probation lock" is not appeared
    # in the system log; the current system
    # index is not greater than the system index before running
    # this test case by 1,
    # Mark this test case "failed"
    if is_lebusy_return is False:
        swilog.error(
            "[FAILED] MarkGood(False) doesn't return LE_BUSY when"
            " the system is under probation "
            "and there is a probation lock"
        )
    elif system_status[0:5] != "tried":
        swilog.error(
            "[FAILED] MarkGood(False) ends the probation period when"
            " the system is under probation and"
            " there is a probation lock"
        )
    elif (new_sys_index - old_sys_index) != 1:
        swilog.error(
            "[FAILED] MarkGood(False) modifies the system"
            " index when the system is under probation and"
            " there is a probation lock"
        )
    else:
        swilog.info(
            "[PASSED] MarkGood(False) only returns LE_BUSY when the "
            "system is under probation and there is a probation lock"
        )
        is_tc_passed = True

    # After StartTC, the current system is marked as "good' and
    # the current system holds a probation lock reboot the system to clear
    # the probation lock before performing the clean up on the target
    target.reboot()
    end_test(is_tc_passed, request)


def L_UpdateCtrl_MarkGood_0005(target, request, legato, init_UpdateCrtl):
    """Verify that le_updateCtrl_MarkGood(True) returns LE_DUPLICATE when the.

    system is already marked as "good".

    Initial Conditions:
        1. Current system state is marked as "good"
        2. Probation period is 10ms

    Test Procedures:
        1. Install the app that invokes le_updateCtrl_MarkGood(True)
        onto the target device
        2. After the probation period, run the app
        3. Check "return LE_DUPLICATE : Probation has expired:
        the system has already been marked" is shown from system log

    (Notes: the current system index, the current system state and
    the current system status can be verified by
    the command line "legato status")

    Args:
        target: fixture to communicate with the target
        request: object to access data
        legato: fixture to call useful functions regarding legato
        init_UpdateCrtl: initial and build app for testing
    """
    swilog.step("Test L_UpdateCtrl_MarkGood_0005")
    old_sys_index = 0
    new_sys_index = 0
    is_leduplicate_return = False
    is_tc_passed = False
    swilog.debug(init_UpdateCrtl)

    # Set the probation period to 1s to turn the system into "good" status
    legato.set_probation_timer(1)

    # Wait 3s to allow the probation period to pass
    time.sleep(3)

    # Set the parameter of the testUpdateCtrl app to "markGood"
    # "5" to run this test case
    target.run(
        "config set apps/%s/procs/%s/args/1 markGood" % (APP_NAME_01, APP_NAME_01)
    )
    target.run("config set apps/%s/procs/%s/args/2 5" % (APP_NAME_01, APP_NAME_01))

    # Store the current system index before le_updateCtrl_MarkGood(True)
    # is called for verification
    old_sys_index = legato.get_current_system_index()

    rsp = target.run("app start %s" % APP_NAME_01, withexitstatus=True)
    swilog.info(rsp)

    # Store the current system status after le_updateCtrl_MarkGood(True)
    # is called when the current status is 'good' for verification
    system_status = legato.get_current_system_status()

    # Store the current system index after le_updateCtrl_MarkGood(True)
    # is called when the current status is 'good' for verification
    new_sys_index = legato.get_current_system_index()

    # Capture "return LE_DUPLICATE: Probation has expired -
    # the system has already been marked Good"
    # from the system log after le_updateCtrl_MarkGood(True)
    # is called when the current status is 'good' for verification

    text_log = (
        "return LE_DUPLICATE: Probation has expired - the system"
        " has already been marked Good"
    )
    if legato.find_in_target_log(text_log):
        is_leduplicate_return = True

    # After le_updateCtrl_MarkGood(True) is called
    # when the current status is 'good',
    # if "return LE_DUPLICATE: Probation has expired -
    # the system has already been marked Good"
    # is not appeared in the system log;
    # the current system status is not marked as "good"; the
    # current system index is equal to the system index before
    # le_updateCtrl_MarkGood(True) is called,
    # mark this test case failed
    if is_leduplicate_return is False:
        swilog.error(
            "[FAILED] MarkGood(True) doesn't return LE_DUPLICATE"
            " when the current system is already marked as 'good'"
        )
    elif old_sys_index != new_sys_index:
        swilog.error(
            "[FAILED] MarkGood(True) modifies the system index when"
            " the current system is already marked as 'good'"
        )
    elif system_status != "good":
        swilog.error(
            "[FAILED] MarkGood(True) modifies the current"
            " system status when the current system is already"
            " marked as 'good'"
        )
    else:
        swilog.info(
            "[PASSED] MarkGood(True) only returns LE_DUPLICATE when"
            " the current system is already marked as 'good'"
        )
        is_tc_passed = True

    end_test(is_tc_passed, request)


def L_UpdateCtrl_MarkGood_0006(target, request, legato, init_UpdateCrtl):
    """Verify that  le_updateCtrl_MarkGood(False) returns LE_DUPLICATE when.

    the system is already marked as "good".

    Initial Conditions:
        1. Current system state is marked as "good"
        2. Probation period is 10ms

    Test Procedures:
        1. Install the app that invokes le_updateCtrl_MarkGood(False)
        onto the target device
        2. After the probation period, run the app
        3. Check the current system state is marked as "good"
        4. Check "return LE_DUPLICATE : Probation has expired:
        the system has already been marked" is shown from system log

    (Notes: the current system index, the current system state and the current
    system status can be verified by the command line "legato status")

    Args:
        target: fixture to communicate with the target
        request: object to access data
        legato: fixture to call useful functions regarding legato
        init_UpdateCrtl: initial and build app for testing
    """
    swilog.step("Test L_UpdateCtrl_MarkGood_0006")
    old_sys_index = 0
    new_sys_index = 0
    is_leduplicate_return = False
    is_tc_passed = False
    swilog.debug(init_UpdateCrtl)

    # Set the probation period to 1s to turn the system into "good" status
    legato.set_probation_timer(1)

    # Wait 3s to allow the probation period to pass
    time.sleep(3)

    # Set the parameter of the testUpdateCtrl app to "markGood"
    # "5" to run this test case
    target.run(
        "config set apps/%s/procs/%s/args/1 markGood" % (APP_NAME_01, APP_NAME_01)
    )
    target.run("config set apps/%s/procs/%s/args/2 6" % (APP_NAME_01, APP_NAME_01))

    # Store the current system index before le_updateCtrl_MarkGood(True)
    # is called for verification
    old_sys_index = legato.get_current_system_index()

    target.run("app start %s" % APP_NAME_01, withexitstatus=True)

    # Store the current system status after le_updateCtrl_MarkGood(False)
    # is called when the current status is 'good' for verification
    system_status = legato.get_current_system_status()

    # Store the current system index after le_updateCtrl_MarkGood(False)
    # is called when the current status is 'good' for verification
    new_sys_index = legato.get_current_system_index()

    # Capture "return LE_DUPLICATE: Probation has expired -
    # the system has already been marked Good"
    # from the system log after le_updateCtrl_MarkGood(False)
    # is called when the current status is 'good' for verification

    msg_log = (
        "return LE_DUPLICATE: Probation has expired - the system"
        " has already been marked Good"
    )
    if legato.find_in_target_log(msg_log):
        is_leduplicate_return = True

    # After le_updateCtrl_MarkGood(False) is called
    # when the current status is 'good',
    # if the "return LE_DUPLICATE: Probation has expired -
    # the system has already been marked Good"
    # keyword is not appeared in the system log;
    # the current system status is not marked as "good";
    # the current system index is equal to the system index
    # before le_updateCtrl_MarkGood(False) is called,
    # mark this test case failed
    if is_leduplicate_return is False:
        swilog.error(
            "[FAILED] MarkGood(False) doesn't return LE_DUPLICATE"
            " when the current system is already marked as 'good'"
        )
    elif old_sys_index != new_sys_index:
        swilog.error(
            "[FAILED] MarkGood(False) modifies the system index when"
            " the current system is already marked as 'good'"
        )
    elif system_status != "good":
        swilog.error(
            "[FAILED] MarkGood(False) modifies"
            " the current system status when "
            "the current system is already marked as 'good'"
        )
    else:
        swilog.info(
            "[PASSED] MarkGood(False) only returns LE_DUPLICATE when"
            " the current system is already marked as 'good'"
        )
        is_tc_passed = True

    end_test(is_tc_passed, request)
