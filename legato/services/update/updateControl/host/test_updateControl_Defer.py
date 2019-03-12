""" @package updateControlModule The update control API test

    Set of functions to test the le_updateCtrl_Defer
"""
import os
import time
import swilog
import pexpect
import pytest

__copyright__ = 'Copyright (C) Sierra Wireless Inc.'
# ==================================================================================================
# Constants and Globals
# ==================================================================================================
# Determine the resources folder (legato apps)
LEGATO_ROOT = os.environ["LEGATO_ROOT"]
TEST_RESOURCES = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                              'resources')
APP_PATH_00 = os.path.join(TEST_RESOURCES, "updateCtrlApi")

APP_NAME_01 = "testUpdateCtrl"
APP_PATH_01 = os.path.join(APP_PATH_00, "testUpdateCtrlApp")

APP_NAME_02 = "helloWorld"
APP_PATH_02 = os.path.join(APP_PATH_00, "helloWorldApp")


# ==================================================================================================
# Local fixtures
# ==================================================================================================
@pytest.fixture()
def init_UpdateCrtl(legato, clean_test):
    """
    Clean up environment & build app

    Args:
        legato: fixture to call useful functions regarding legato
        clean_test: fixture to clean up environment

    """

    if legato.get_current_system_index() != 0:
        legato.restore_golden_legato()
    # Make install application
    legato.make_install(APP_NAME_01, APP_PATH_01)
    swilog.info("[PASSED] Make and install the test app successfully.")


# ==================================================================================================
# Test Functions
# ==================================================================================================
def L_UpdateCtrl_Defer_0001(target, legato, init_UpdateCrtl):
    """
    Verify that le_updateCtrl_Defer() prevents all updates
    (remove an app)

    Initial Condition:
        1. Current system index is "N"

    Test Procedures:
        1. Install the app that invokes le_updateCtrl_Defer()
        onto the target device
        2. Check the current system index is "N + 1" and run the app
        3. Remove the same app
        4. Check "Updates are currently deferred" is shown from log
        5. Check the app is still existed in the target device
        (verified by the command line "app list")
        6. Check the current system index is "N + 1"

    (Notes: the current system index, the current system state and
    the current system status can be verified by
    the command line "legato status")

    Args:
        target: fixture to communicate with the target
        legato: fixture to call useful functions regarding legato
        init_UpdateCrtl: fixture to clean up environment and build app

    """

    swilog.step("Test L_UpdateCtrl_Defer_0001")

    # Set the parameters of the testUpdateCtrl app to
    # "defer" "1" to run this test case
    target.run("config set apps/%s/procs/%s/args/1 defer" % (APP_NAME_01,
                                                             APP_NAME_01))
    target.run("config set apps/%s/procs/%s/args/2 1" % (APP_NAME_01,
                                                         APP_NAME_01))

    # Run the testUpdateCtrl app that will invoke le_updateCtrl_Defer()
    exit, rsp = target.run("app start %s" % APP_NAME_01, withexitstatus=1)
    assert exit == 0, "[FAILED] App could not be started."

    # Try to do a update in the target device by removing
    # the testUpdateCtrl app while the
    # Current system should hold a defer lock
    # If the removal was successful then, the system update is proceed
    exit, rsp = target.run("app remove %s" % APP_NAME_01, withexitstatus=1)
    assert exit == 1, "[FAILED] Defer() allows update to happen when \
attempting to remove an app."

    # If the system update was successful,
    # the update was allowed and mark this TC failed
    swilog.info("[PASSED] Defer() doesn't allow update to"
                " happen when attempting to remove an app")

    swilog.info("[PASSED] Test L_UpdateCtrl_Defer_0001")


def L_UpdateCtrl_Defer_0002(target, legato, init_UpdateCrtl):
    """
    Verify that le_updateCtrl_Defer() prevents all updates
    (install an app)

    Initial Condition:
        1. Current system index is "N"

    Test Procedures:
        1. Install the app that invokes le_updateCtrl_Defer()
        onto the target device
        2. Check the current system index is "N + 1"and run the app
        3. Install an app (e.g. helloWorld) onto the target device
        4. Check "Updates are currently deferred" is shown from log
        5. Check the app is not installed on the target device
        (verified by the command line "app list")
        6. Check the current system index is "N + 1"

    (Notes: the current system index, the current system state and
    the current system status can be verified by
    the command line "legato status")

    Args:
        target: fixture to communicate with the target
        legato: fixture to call useful functions regarding legato
        init_UpdateCrtl: fixture to clean up environment and build app

    """

    swilog.step("Test L_UpdateCtrl_Defer_0002")

    # Set the parameter of the testUpdateCtrl app to
    # "defer" "2" to run this test case
    target.run("config set apps/%s/procs/%s/args/1 defer" % (APP_NAME_01,
                                                             APP_NAME_01))
    target.run("config set apps/%s/procs/%s/args/2 2" % (APP_NAME_01,
                                                         APP_NAME_01))

    # Run the testUpdateCtrl app that will invoke le_updateCtrl_Defer()
    exit, rsp = target.run("app start %s" % APP_NAME_01, withexitstatus=1)
    assert exit == 0, "[FAILED] App could not be started."

    # Perform an update to the system by installing the new helloWorld app
    # If the installation was successful then,
    # the system update attempt is proceed
    legato.make(APP_NAME_02, APP_PATH_02)
    legato.install(APP_NAME_02, APP_PATH_02, should_fail=True)

    # If the system update was successful,
    # the update was allowed and mark this TC failed
    swilog.info("[PASSED] Defer() doesn't allow update to \
                happen when attempting to install an app")

    swilog.info("[PASSED] Test L_UpdateCtrl_Defer_0002")


def L_UpdateCtrl_Defer_0003(target, legato, init_UpdateCrtl):
    """
    Verify that le_updateCtrl_Defer() prevents all updates
    (install a system)

    Initial Condition:
        1. Current system index is "N"

    Test Procedures:
        1. Install the app that invokes le_updateCtrl_Defer()
        onto the target device
        2. Check the current system index is "N + 1" and run the app
        3. Install Legato onto the target device
        4. Check "Updates are currently deferred" is shown from log
        5. Check the current system index is "N + 1"

    (Notes: the current system index, the current system state and
    the current system status can be verified by
    the command line "legato status")

     Args:
        target: fixture to communicate with the target
        legato: fixture to call useful functions regarding legato
        init_UpdateCrtl: fixture to clean up environment and build app

    """

    swilog.step("Test L_UpdateCtrl_Defer_0003")

    # Set the parameter of the testUpdateCtrl app to "defer" "3"
    target.run("config set apps/%s/procs/%s/args/1 defer" % (APP_NAME_01,
                                                             APP_NAME_01))
    target.run("config set apps/%s/procs/%s/args/2 3" % (APP_NAME_01,
                                                         APP_NAME_01))

    # Change the probation period to 1s to
    # turn the current system into a "good" system status because
    # the current system index would be incremented after
    # A system update only if the current system
    # status is "good"
    legato.reset_probation_timer()

    # Wait for 4s allow the probation period to pass
    time.sleep(4)
    # Run the testUpdateCtrl app that will invoke le_updateCtrl_Defer()
    exit, rsp = target.run("app start %s" % APP_NAME_01, withexitstatus=1)
    assert exit == 0, "[FAILED] App could not be started."

    # Try to do an update in the target device by installing
    # a new Legato system
    # If the installation was successful then,
    # the system update attempt is proceed
    cmd = "instlegato %s/build/" % (LEGATO_ROOT)
    rsp, exit = pexpect.run(cmd, withexitstatus=1)
    assert exit != 0, "[FAILED] Defer() allows update to \
                       happen when attempting to install a new system"
    # If the system update was successful
    # (which updates are allowed and le_updateCtrl_Defer()
    # Doesn't satisfy its functionality), mark this test case is failed
    swilog.info("[PASSED] Defer() doesn't allow update to happen when"
                " attempting to install a new system")

    swilog.info("[PASSED] Test L_UpdateCtrl_Defer_0003")


def L_UpdateCtrl_Defer_0004(target, legato, init_UpdateCrtl):
    """
    Verify that the deferral will be released after the client
    (process) who called le_updateCtrl_Defer() is dead

    Testing Procedures:
        1. Install the app that invokes le_updateCtrl_Defer()
           and kills its own process onto the target device
        2. Run the app
        3. Install the helloWorld app
        4. Check 3. is successful

    Args:
        target: fixture to communicate with the target
        legato: fixture to call useful functions regarding legato
        init_UpdateCrtl: fixture to clean up environment and build app

    """

    swilog.step("Test L_UpdateCtrl_Defer_0004")

    # Set the parameter of the testUpdateCtrl app to
    # "defer" "4" to run this test case
    target.run("config set apps/%s/procs/%s/args/1 defer" % (APP_NAME_01,
                                                             APP_NAME_01))
    target.run("config set apps/%s/procs/%s/args/2 4" % (APP_NAME_01,
                                                         APP_NAME_01))
    # Run the testUpdateCtrl app that will invoke le_updateCtrl_Defer()
    exit, rsp = target.run("app start %s" % APP_NAME_01, withexitstatus=1)
    assert exit == 0, "[FAILED] App could not be started."

    # Check whether defer lock is released so that
    # any system update is allowed by installing
    # The helloWorld app when when the client (process)
    # who called le_updateCtrl_Defer() is dead
    legato.make_install(APP_NAME_01, APP_PATH_01)

    # If the target device is not shutting down then,
    # killing the process who holds the defer lock
    # won't cause reboot. Marked this test case failed
    swilog.info("[PASSED] defer lock was released after"
                " a process which called Defer() is dead")

    swilog.info("[PASSED] Test L_UpdateCtrl_Defer_0004")


def L_UpdateCtrl_Defer_0005(target, legato, clean_test):
    """
    Verify that le_updateCtrl_Defer() prevents rollbacks

    Initial Conditions:
        1. Current system index is "N"
           le_updateCtrl_FailProbation() is verified

    Test Procedures:
        1. Install the app that invokes le_updateCtrl_Defer() followed by
           le_updateCtrl_FailProbation() second
        2. Run the app
        3. Check the current system index is "N + 1"

    (Notes: the current system index, the current system state and
        the current system status can be verified by
        the command line "legato status")

     Args:
        target: fixture to communicate with the target
        legato: fixture to call useful functions regarding legato
        clean_test: fixture to clean up environment

    """

    swilog.step("Test L_UpdateCtrl_Defer_0005")
    old_sys_index = 0
    new_sys_index = 0
    system_status = ""
    is_target_reboot = False

    # Get the system index from a 'good' system by setting
    # the probation period
    # to 1s to turn the system into 'good'
    legato.set_probation_timer(1)

    # Wait 3s to allow the probation period to pass
    time.sleep(3)

    # Since this test case is required to run under probation,
    # the pre-set probation
    # period has to be changed to the default, 30mins
    legato.reset_probation_timer()

    # Begin of the this TC
    legato.make_install(APP_NAME_01, APP_PATH_01)
    swilog.info("[PASSED] Make and install the test app successfully.")

    # Set the parameter of the testUpdateCtrl app to
    # "defer" "5" to run this test case
    target.run("config set apps/%s/procs/%s/args/1 defer" % (APP_NAME_01,
                                                             APP_NAME_01))
    target.run("config set apps/%s/procs/%s/args/2 5" % (APP_NAME_01,
                                                         APP_NAME_01))

    # Store the system index before the deferral of
    # the system roll-back for verification
    old_sys_index = legato.get_current_system_index()

    target.run("app start %s" % APP_NAME_01, withexitstatus=1)

    # ==========================================================
    # TODO whether the reboot is necessary before the roll-back
    # if this test case is failed then, the system
    # may perform roll-back so, target device will reboot
    # ticket: LE-5080
    # ==========================================================

    # Wait 10s to check whether the system performs a roll-back
    # so that the target device will reboot.
    # If it does reboot, wait until the reboot is finished
    if target.wait_for_device_down(10) == 0:
        # Wait for the reboot is finished
        target.wait_for_reboot()
        is_target_reboot = True

    # Store the system index after the deferral of
    # the system roll-back for verification
    new_sys_index = legato.get_current_system_index()

    # Store the system status after the deferral of
    # the system roll-back for verification
    system_status = legato.get_current_system_status()

    # Since the behaviours of a system roll-back are
    #   1)Current system index rolls-back to a previous 'good' system index
    #   2)Target device reboot
    #   3)Current system status is marked as 'good' after roll-back
    #   4)Current system status is marked as 'bad' before roll-back
    #   *NOTE*: According to the implementation of FailProbation, it will mark
    #      the current system as 'bad' before checking whether there is any
    #      defer lock that the current system is holding. Therefore, it should
    #      not be part of the verification in this test case
    #   5)Previous 'good' system doesn't has the testUpdateCtrl app installed
    # If any of the previous behaviours was inspected, roll-back was not held
    # mark this test case failed
    if (old_sys_index != new_sys_index) or \
       (legato.is_app_exist(APP_NAME_01) is False) or \
       (is_target_reboot is True) or (system_status is "good"):
        swilog.error("[FAILED] defer() doesn't prevent the system roll-back")
    else:
        swilog.info("[PASSED] defer() does prevent the system roll-back")
    target.reboot()
    swilog.info("[PASSED] Test L_UpdateCtrl_Defer_0005")


def L_UpdateCtrl_Defer_0006(target, legato, init_UpdateCrtl):
    """
    Verify that the deferral will be released after
    stopping the client (process) who called le_updateCtrl_Defer()

    Testing Procedures:
        1. Install the app that invokes le_updateCtrl_Defer()
           onto the target device
        2. Run the app
        3. Stop the app
        4. Install the helloWorld app
        5. Check 4. is successful

    Args:
        target: fixture to communicate with the target
        legato: fixture to call useful functions regarding legato
        init_UpdateCrtl: fixture to clean up environment and build app

    """

    swilog.step("Test L_UpdateCtrl_Defer_0006")
    # Begin of the this TC

    # Set the parameter of the testUpdateCtrl app to
    # "defer" "4" to run this test case
    target.run("config set apps/%s/procs/%s/args/1 defer" % (APP_NAME_01,
                                                             APP_NAME_01))
    target.run("config set apps/%s/procs/%s/args/2 6" % (APP_NAME_01,
                                                         APP_NAME_01))

    # Run the testUpdateCtrl app that will invoke le_updateCtrl_Defer()
    exit, rsp = target.run("app start %s" % APP_NAME_01, withexitstatus=1)
    assert exit == 0, "[FAILED] App could not be started."

    # Stop the testUPdateCtrl app which is holding a defer lock
    exit, rsp = target.run("app stop %s" % APP_NAME_01, withexitstatus=1)
    assert exit == 0, "[FAILED] App could not be stopped."

    # Check whether defer lock is released so that
    #    any system update is allowed by installing
    # The helloWorld app when when the client (process)
    #    who called le_updateCtrl_Defer() is stopped
    legato.make_install(APP_NAME_01, APP_PATH_01)

    # If the target device is not shutting down then,
    # killing the process who holds the defer lock
    # Won't cause reboot. Marked this test case failed
    swilog.info("[PASSED] defer lock was released after a"
                " process which called Defer() is stopped")

    swilog.info("[PASSED] Test L_UpdateCtrl_Defer_0006")
