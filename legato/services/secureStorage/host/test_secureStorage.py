r"""!secured storage test.

Set of functions to test the secured storage.

@package SecureStorageModule
@defgroup secureStorageTests Secure Storage Tests

@file
\ingroup secureStorageTests
"""
import os
import time
import pytest
from pytest_letp.lib import swilog

__copyright__ = "Copyright (C) Sierra Wireless Inc."
# ====================================================================================
# Constants and Globals
# ====================================================================================
TEST_RESOURCES = os.path.join(os.path.abspath(os.path.dirname(__file__)), "resources")
TEST_TOOLS = os.path.join(os.path.abspath(os.path.dirname(__file__)), "tools")
APP_NAME = "SecureStorageTest"
APP_PATH = TEST_RESOURCES
TEST_APP_A = "appA"
TEST_APP_B = "appB"


# ====================================================================================
# Functions
# ====================================================================================
def set_test_app_test_type(target, test_type):
    """!Set test type for test app.

    @param target: fixture to communicate with the target
    @param test_type: type of test is set in config tree
            (read, write, delete, writeread, writedeleteread...)
    """
    cmd = 'config set "/apps/%s/procs/%s/args/1" %s' % (APP_NAME, APP_NAME, test_type)
    exit_status, rsp = target.run(cmd, withexitstatus=True)
    swilog.debug(rsp)
    assert exit_status == 0


def set_test_app_repeat_cycle(target, test_cycle):
    """!Set test cycle for test app.

    @param target: fixture to communicate with the target
    @param test_cycle: cycle of test is set in config tree
    """
    cmd = 'config set "/apps/%s/procs/%s/args/2" %s' % (APP_NAME, APP_NAME, test_cycle)
    exit_status, rsp = target.run(cmd, withexitstatus=True)
    swilog.debug(rsp)
    assert exit_status == 0


def check_log(legato, test_title):
    """!Check log for test app.

    @param legato: fixture to call useful functions regarding legato
    @param test_title: title of test

    @return 1: Failed to check log
    @return 2: Passed to check log
    """
    # Need to ensure app has started running and is active
    retry_count = 0
    retry_max = 5

    cmd = r"/sbin/logread | grep -c '\- Round \['"
    last_round_count = legato.ssh_to_target(cmd, output=True)

    while last_round_count == 0 and retry_count <= retry_max:
        time.sleep(1)
        last_round_count = legato.ssh_to_target(cmd, output=True)
        retry_count += 1

    err_msg = (
        "[FAILED] %s. Not one round of test has started. "
        "Or App takes a long time to start a round of test. "
        "Or timeout is too short." % test_title
    )
    assert retry_count <= retry_max, err_msg

    # NOTE: if each "round" of test takes a long time (e.g. from
    # when "_lastRoundCount" is initialized to when "_newRoundCount"
    # is updated, or if it's longer than the while loop sleep time),
    # then the test may falsely fail. The assumption made is that
    # each "round" of test is "quick",
    new_round_count = 0
    # Retry every 10 sec up to 60 times
    retry_count = 0

    # Retry_max * sleep time define the timeout.
    retry_max = 60
    while retry_count <= retry_max:

        # If app has stopped, there is already a definite result; exit loop.
        if legato.is_app_running(APP_NAME):
            new_round_count = legato.ssh_to_target(cmd, output=True)
            if new_round_count == last_round_count:
                break

            last_round_count = new_round_count
        else:
            break

        # Sleep time must be longer than 1 cycle of any test.
        time.sleep(10)
        retry_count += 1

    if legato.find_in_target_log("Secure Storage Test Passed"):
        swilog.info("[PASSED] %s" % test_title)
        return 0

    else:
        swilog.error("[FAILED] %s" % test_title)
        if retry_count > retry_max:
            swilog.info(
                "This test has too many cycles than the defined "
                "timeout would allow. Or the test fails with an "
                "unforeseen reason. | "
            )
        if legato.is_app_running(APP_NAME):
            swilog.info("App is still running.")
        return 1


def restart_syslog(target, legato):
    """!Restart syslog and try to re-mount the log socket.

    Since sandbox is persistent May 2016.

    @param target: fixture to communicate with the target
    @param legato: fixture to call useful functions regarding legato
    """
    # Restart syslogd to have a clean slate of logs
    legato.clear_target_log()

    # (May 2016) Since sandbox is now persistent,
    # the log socket has to be re-mounted.
    # If an app has already started, doing the above without re-mounting
    # the log socket will cause the app's logs not showing up in syslog.
    # Consider putting this in common.sh.
    # Another solution is, instead of restarting syslogd,
    # do "logread -f > logfile &" at the point where log needs to be captured
    # (typically before test app start), and kill that process
    # and grep logfile when test app finishes.  It's less convenient.
    test_app_log_socket = "/legato/systems/current/appsWriteable/%s/dev/log" % APP_NAME
    exit_status, rsp = target.run(
        "umount %s" % test_app_log_socket, withexitstatus=True
    )
    swilog.debug(rsp)
    assert exit_status == 0, "[FAILED] Unmount failed."

    exit_status, rsp = target.run(
        "mount --bind /dev/log %s" % test_app_log_socket, withexitstatus=True
    )
    swilog.debug(rsp)
    assert exit_status == 0, "[FAILED] Mount failed."


def secure_storage_test_post(target, legato, test_title, test_type, test_cycle):
    """!Secure storage test post.

    @param target: fixture to communicate with the target
    @param legato: fixture to call useful functions regarding legato
    @param test_title: title of test
    @param test_type: test type to be set in config tree
    @param test_cycle: test cycle to be set in config tree
    """
    time.sleep(5)
    assert test_title != "", "[FAILED] Test title is empty."
    restart_syslog(target, legato)
    set_test_app_test_type(target, test_type)
    set_test_app_repeat_cycle(target, test_cycle)
    legato.restart(APP_NAME)

    err_msg = "[FAILED] Secure Storage test post failed."
    assert check_log(legato, test_title) == 0, err_msg


# ====================================================================================
# Local fixtures
# ====================================================================================
@pytest.fixture(scope="function")
def test_app(legato, tmpdir):
    """!Fixture regarding to build, install and remove app.

    @param legato: fixture to call useful functions regarding legato
    @param tmpdir: fixture to provide a temporary directory
                  unique to the test invocation
    """
    # Remove the test app if it is already existing
    if legato.is_app_exist(TEST_APP_A):
        legato.remove(TEST_APP_A)
    if legato.is_app_exist(TEST_APP_B):
        legato.remove(TEST_APP_B)

    # Go to temp directory
    os.chdir(str(tmpdir))
    legato.make_install(TEST_APP_A, "%s/SecStoreAppIndependenceTest" % TEST_RESOURCES)
    legato.make_install(TEST_APP_B, "%s/SecStoreAppIndependenceTest" % TEST_RESOURCES)

    yield
    if legato.is_app_exist(TEST_APP_A):
        legato.remove(TEST_APP_A)
    if legato.is_app_exist(TEST_APP_B):
        legato.remove(TEST_APP_B)


# ====================================================================================
# Test functions
# ====================================================================================
@pytest.mark.usefixtures("test_app")
def L_SecureStorage_0004(legato):
    """!Multiple apps have independent access to the secured storage.

    Verification:
        This test case will mark as "failed" when
            1. both apps can't read its independent written contents

    This script will
        1. In one Legato app, use the "write" API of the secure storage
           component to write data to the secured storage, with a particular
           storage item name.
        2. In a different Legato app, use the "write" API and the same storage
           item name as step 1, write different data from step 1 to the
           secured storage.
        3. Verify that the data in the two different apps are independently
           stored, by using the "read" API in both apps, and check that the
           data read are as per the originally written data in steps 1 and 2.

    @param legato: fixture to call useful functions regarding legato
    @param test_app: fixture regarding to build, install and remove app
    """
    swilog.step("Execute L_SecureStorage_0004")
    legato.clear_target_log()

    legato.runProc("%s" % TEST_APP_A, "--exe=%s" % TEST_APP_A, "write")
    legato.runProc("%s" % TEST_APP_B, "--exe=%s" % TEST_APP_B, "write")
    legato.runProc("%s" % TEST_APP_A, "--exe=%s" % TEST_APP_A, "read")
    legato.runProc("%s" % TEST_APP_B, "--exe=%s" % TEST_APP_B, "read")

    time.sleep(10)
    rsp1 = legato.find_in_target_log(
        "appA successfully read" " its own written content"
    )
    rsp2 = legato.find_in_target_log(
        "appB successfully read" " its own written content"
    )
    if not rsp1:
        swilog.error("%s doesn't read what it wrote" % TEST_APP_A)
    if not rsp2:
        swilog.error("%s doesn't read what it wrote" % TEST_APP_B)

    failed_testcases_list = swilog.get_error_list()
    if failed_testcases_list != []:
        assert 0, "Some tests failed:\n%s" % "\n".join(failed_testcases_list)
    else:
        swilog.info("[PASSED] L_SecureStorage_0004")


@pytest.mark.usefixtures("app_leg")
def L_SecureStorage_0006(target, legato):
    """!Secure Storage Read API can be repeatedly called many times reliably.

    This script will
        1. Use the "Write" API to write an item.
        2. Use the "Read" API to repeatedly read the written item.
        3. Verify that every read is successful and the data read
           is the same as the data written.

    @param target: fixture to communicate with the target
    @param legato: fixture to call useful functions regarding legato
    @param app_leg: fixture regarding to build, install and remove app
    """
    swilog.step("Execute L_SecureStorage_0006")
    test_title = r"Read\ Test"
    test_type = "read"
    test_cycle = "50"

    if not legato.is_app_running(APP_NAME):
        legato.start(APP_NAME)

    secure_storage_test_post(target, legato, test_title, test_type, test_cycle)

    swilog.info("[PASSED] L_SecureStorage_0006")


@pytest.mark.usefixtures("app_leg")
def L_SecureStorage_0007(target, legato):
    """!Secure Storage Write API can be repeatedly called many times reliably.

    This script will
        1. Use the "Write" API to repeatedly write an item.
        2. Verify that every write is successful.

    @param target: fixture to communicate with the target
    @param legato: fixture to call useful functions regarding legato
    @param app_leg: fixture regarding to build, install and remove app
    """
    swilog.step("Execute L_SecureStorage_0007")
    test_title = r"Write\ Test"
    test_type = "write"
    test_cycle = "50"

    if not legato.is_app_running(APP_NAME):
        legato.start(APP_NAME)

    secure_storage_test_post(target, legato, test_title, test_type, test_cycle)

    swilog.info("[PASSED] L_SecureStorage_0007")


@pytest.mark.usefixtures("app_leg")
def L_SecureStorage_0011(target, legato):
    """!Purpose: Verify that the Secure Storage Write and Read APIs.

    Can be repeatedly called many times reliably.

    This script will
        1. Use the "Write" API to write an item.
        2. Use the "Read" API to read the item.
        3. Repeat 1 and 2 many times.
        4. Verify that for all operations both write and read are
           successful and the data read is the same as the data written.

    @param target: fixture to communicate with the target
    @param legato: fixture to call useful functions regarding legato
    @param app_leg: fixture regarding to build, install and remove app
    """
    swilog.step("Execute L_SecureStorage_0011")
    test_title = r"Write\ Read\ Test"
    test_type = "writeread"
    test_cycle = "50"

    if not legato.is_app_running(APP_NAME):
        legato.start(APP_NAME)

    secure_storage_test_post(target, legato, test_title, test_type, test_cycle)

    swilog.info("[PASSED] L_SecureStorage_0011")
