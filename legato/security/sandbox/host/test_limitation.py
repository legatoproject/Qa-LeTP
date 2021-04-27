"""sandbox app limitation test.

Set of functions to test the sandbox app limitation.
"""
import os
import re
import time
import pytest
import pexpect
from pytest_letp.lib import swilog

__copyright__ = "Copyright (C) Sierra Wireless Inc."
# ====================================================================================
# Constants and Globals
# ====================================================================================
TEST_RESOURCES = os.path.join(os.path.abspath(os.path.dirname(__file__)), "resources")

APP_NAME_L_SandBox_0007 = "FileSizeTest"
APP_PATH_L_SandBox_0007 = os.path.join(TEST_RESOURCES, APP_NAME_L_SandBox_0007)
TEMPLATE_NAME_L_SandBox_0007 = "FST_tpl"
TEST_TITLE_L_SandBox_0007 = "MaxCreatedFileSize"

APP_NAME_L_SandBox_0010 = "NumSigQueuedTest"
APP_PATH_L_SandBox_0010 = os.path.join(TEST_RESOURCES, APP_NAME_L_SandBox_0010)
TEMPLATE_NAME_L_SandBox_0010 = "NSQT_tpl"
TEST_TITLE_L_SandBox_0010 = "RealTimeSignalQueueSize"

APP_NAME_L_SandBox_0012 = "MemLockSizeTest"
APP_PATH_L_SandBox_0012 = os.path.join(TEST_RESOURCES, APP_NAME_L_SandBox_0012)
TEMPLATE_NAME_L_SandBox_0012 = "MLST_tpl"
TEST_TITLE_L_SandBox_0012 = "MemLockSize"

APP_NAME_L_SandBox_0018 = "FdTest"
APP_PATH_L_SandBox_0018 = os.path.join(TEST_RESOURCES, APP_NAME_L_SandBox_0018)
TEMPLATE_NAME_L_SandBox_0018 = "FD_tpl"
TEST_TITLE_L_SandBox_0018 = "NumberOfFileDescriptor"

TEST_TITLE_KEY_TBL = {
    "TEST_TITLE_PROC": "NumberOfProcesses",
    "TEST_TITLE_MSGQ": "PosixMsgQueueSize",
    "TEST_TITLE_SIGQ": "RealTimeSignalQueueSize",
    "TEST_TITLE_FS": "FileSystemSize",
    "TEST_TITLE_VM": "VirtualMemorySize",
    "TEST_TITLE_CORE": "CoreDumpFileSize",
    "TEST_TITLE_FILE": "MaxCreatedFileSize",
    "TEST_TITLE_MEML": "MemLockSize",
    "TEST_TITLE_FD": "NumberOfFileDescriptor",
}

CUR_LIM_LEADING_STR_TBL = {
    TEST_TITLE_KEY_TBL["TEST_TITLE_PROC"]: "NumProcs limit is:",
    TEST_TITLE_KEY_TBL["TEST_TITLE_MSGQ"]: "MessageQueueSize limit is:",
    TEST_TITLE_KEY_TBL["TEST_TITLE_SIGQ"]: "SigPending limit is:",
    TEST_TITLE_KEY_TBL["TEST_TITLE_FS"]: "FileSystemSize limit is:",
    TEST_TITLE_KEY_TBL["TEST_TITLE_VM"]: "VirMem limit is:",
    TEST_TITLE_KEY_TBL["TEST_TITLE_CORE"]: "CoreSize limit is:",
    TEST_TITLE_KEY_TBL["TEST_TITLE_FILE"]: "FileSize limit is:",
    TEST_TITLE_KEY_TBL["TEST_TITLE_MEML"]: "MemLockSize limit is:",
    TEST_TITLE_KEY_TBL["TEST_TITLE_FD"]: "Fd limit is:",
}

RT_VERI_STR_TBL = {
    TEST_TITLE_KEY_TBL["TEST_TITLE_PROC"]: "Number of processes limit test PASSED.",
    TEST_TITLE_KEY_TBL["TEST_TITLE_MSGQ"]: "POSIX message queue limit test PASSED.",
    TEST_TITLE_KEY_TBL["TEST_TITLE_SIGQ"]: "Signal queue limit test PASSED.",
    TEST_TITLE_KEY_TBL["TEST_TITLE_FS"]: "File system size limit test PASSED.",
    TEST_TITLE_KEY_TBL["TEST_TITLE_VM"]: "Virtual memory size limit test PASSED.",
    TEST_TITLE_KEY_TBL["TEST_TITLE_CORE"]: "Core dump file limit test PASSED.",
    TEST_TITLE_KEY_TBL["TEST_TITLE_FILE"]: "File size limit test PASSED.",
    TEST_TITLE_KEY_TBL["TEST_TITLE_MEML"]: "Memory lock size limit test PASSED.",
    TEST_TITLE_KEY_TBL["TEST_TITLE_FD"]: "File descriptor limit test PASSED.",
}

# source: resourceLimits.c.  Could this be extracted programmatically?
DEFAULT_VALUE_STR_TBL = {
    TEST_TITLE_KEY_TBL["TEST_TITLE_PROC"]: "20",
    TEST_TITLE_KEY_TBL["TEST_TITLE_MSGQ"]: "512",
    TEST_TITLE_KEY_TBL["TEST_TITLE_SIGQ"]: "100",
    TEST_TITLE_KEY_TBL["TEST_TITLE_FS"]: "131072",
    TEST_TITLE_KEY_TBL["TEST_TITLE_VM"]: "16777216",
    TEST_TITLE_KEY_TBL["TEST_TITLE_CORE"]: "8192",
    TEST_TITLE_KEY_TBL["TEST_TITLE_FILE"]: "90112",
    TEST_TITLE_KEY_TBL["TEST_TITLE_MEML"]: "8192",
    TEST_TITLE_KEY_TBL["TEST_TITLE_FD"]: "256",
}


# ====================================================================================
# Functions
# ====================================================================================
def sandbox_verification(val_under_test, expected_val, temp_output_file, test_title):
    """Verification sandbox limitation test.

    :param val_under_test: value under test
    :param expected_val: expected value from the test
    :param temp_output_file: temporary output file
    :param test_title: title of the test

    :returns exit_code: return value for verification sandbox
                    0: passed
                    1: failed
                    2: error
    """
    exit_code = 0
    current_limit_leading_str = ""
    runtime_verification_str = ""
    default_value_str = ""

    # Get values depend on the test title.
    for test_value in TEST_TITLE_KEY_TBL.values():
        if test_title == test_value:
            current_limit_leading_str = CUR_LIM_LEADING_STR_TBL[test_value]
            runtime_verification_str = RT_VERI_STR_TBL[test_value]
            default_value_str = DEFAULT_VALUE_STR_TBL[test_value]
            break

    # Print value after got
    swilog.info(current_limit_leading_str)
    swilog.info(runtime_verification_str)
    swilog.info(default_value_str)

    # Table lookup failed. Test title might be invalid. Do not proceed.
    if (
        current_limit_leading_str == ""
        or runtime_verification_str == ""
        or default_value_str == ""
    ):
        swilog.info(
            "[FAILED] Test title [%s] might be invalid. "
            "Exiting the verification script." % test_title
        )
        return 2

    # NEED TO: use SED to get actual value, and trim leading/trailing spaces
    cmd = "grep '%s' '%s'" % (current_limit_leading_str, temp_output_file)
    swilog.info("Grep command: %s" % cmd)
    rsp = pexpect.run(cmd, encoding="utf-8")
    swilog.info(rsp)

    # Search value in grep response.
    match_obj = re.search(r"(.*)%s (\d+)" % current_limit_leading_str, rsp, re.M)
    actual_value = ""
    if match_obj:
        actual_value = match_obj.group(2)
        swilog.info("Object is not null.")

    swilog.info("Actual value: %s" % actual_value)
    if actual_value == "":
        swilog.info(
            "[FAILED] Cannot grep actual limit value from the log. The"
            " app might not be running. Exiting the verification."
        )
        return 2

    # if expected value is "invalid", then actual value should be the default
    if expected_val == "invalid":
        if str(actual_value) != str(default_value_str):
            exit_code = 1
            swilog.info(
                "[FAILED] Attempting to set an invalid value of <%s> "
                "DOES NOT result in the default of <%s>. Actual Value"
                " is: <%s>" % (val_under_test, default_value_str, actual_value)
            )
            return exit_code

        swilog.info(
            "Attempting to set an invalid value of <%s> results in"
            " the default of <%s>" % (val_under_test, default_value_str)
        )

    else:
        if expected_val.startswith(">="):
            min_val = int(expected_val[2:])
            if int(actual_value) < min_val:
                swilog.info(
                    "[FAILED] limit is not successfully set to the at least"
                    "value of <%s>. Actual Value is: <%s>." % (min_val, actual_value)
                )

        elif int(actual_value) == int(expected_val):
            swilog.info(
                "PASSED limit is successfully set to the expected "
                "value of <%s>" % expected_val
            )
        else:
            exit_code = 1
            swilog.info(
                "[FAILED] limit is not successfully set to the "
                "expected value of <%s>. Actual Value is: <%s>."
                % (expected_val, actual_value)
            )
            return exit_code

    rsp, exit_status = pexpect.run(
        "grep '%s' '%s'" % (runtime_verification_str, temp_output_file),
        withexitstatus=True,
        encoding="utf-8",
    )
    swilog.debug(rsp)
    swilog.debug(exit_status)

    if exit_status != 0:
        exit_code = 1
        swilog.info("[FAILED] Test of %s" % test_title)
        return exit_code

    swilog.info("[PASSED] Test of %s" % test_title)
    return exit_code


def make_install_sandbox_app(legato, tmpdir, app_name, app_path, expect_tst):
    """Build and install sandbox test app.

    :param legato: fixture to call useful functions regarding legato
    :param tmpdir: fixture to provide a temporary directory
                 unique to the test invocation
    :param app_name: name of the app
    :param app_path: path to the adef file
    :param expect_tst: expected value
    """
    rsp = pexpect.run("cat %s/%s.adef" % (app_path, app_name), encoding="utf-8")
    swilog.info(rsp)
    make_should_fail = False

    # Go to temp directory
    os.chdir(str(tmpdir))
    try:
        legato.clean(app_name)
    except:
        swilog.info("Failed to clean the app.")
    try:
        legato.make(app_name, app_path, make_should_fail)
        legato.clear_target_log()
        legato.install(app_name)
        legato.start(app_name)
        time.sleep(5)
    except:
        assert expect_tst == "invalid", (
            "Test failed during " "make/install/start but was " "not marked as invalid"
        )
    else:
        assert expect_tst != "invalid Test should be invalid but was passed"

    return expect_tst


def sandbox(target, legato, tmpdir, tpl_val, expect_tst, failed_reason, init_sandbox):
    """General function for all test cases.

    This function will:
        1. Update, build and install app
        2. Test is passed if verification OK

    :param target: fixture to communicate with the target
    :param legato: fixture to call useful functions regarding legato
    :param tmpdir: fixture to provide a temporary directory
                  unique to the test invocation
    :param tpl_val: testing value
    :param expect_tst: expected value
    :param failed_reason: failed reason
    :param init_sandbox: fixture to initation and cleanup the environment
    """
    # list_obj[0] app_name
    # list_obj[1] app_path
    # list_obj[2] template_name
    # list_obj[3] test_title
    list_obj = init_sandbox

    swilog.info("test val %s, expect test %s" % (tpl_val, expect_tst))
    rsp = os.system(
        r'sed "s/TEMPLATE_VALUE_1/%s/g" "%s/%s.adef" > %s/%s.adef\
        '
        % (tpl_val, list_obj[1], list_obj[2], list_obj[1], list_obj[0])
    )
    swilog.info(rsp)

    expect_tst = make_install_sandbox_app(
        legato, tmpdir, list_obj[0], list_obj[1], expect_tst
    )

    if expect_tst != "invalid":
        logread = target.run("/sbin/logread")
        with open("temp.out", "w") as f:
            f.write(logread.replace("\r", ""))

        status = sandbox_verification(tpl_val, expect_tst, "temp.out", list_obj[3])

        # Test is passed if verification OK
        # Or if status != 0 but there is a reason to fail.
        # If the reason is a JIRA ticket, the test is FAILED
        operator1 = status != 0 and failed_reason != ""
        operator2 = operator1 and "LE-" not in failed_reason

        err_msg = "Verification failed for %s. value %s, expected value : %s" % (
            list_obj[3],
            tpl_val,
            expect_tst,
        )
        assert status == 0 or operator2, err_msg


# ====================================================================================
# Local fixtures
# ====================================================================================
@pytest.fixture()
def init_sandbox(request, legato):
    """Init and cleanup environment.

    :param request: object to access data
    :param legato: fixture to call useful functions regarding legato
    """
    app_name = getattr(request.module, "APP_NAME_%s" % request.node.name.split("[")[0])
    app_path = getattr(request.module, "APP_PATH_%s" % request.node.name.split("[")[0])
    template_name = getattr(
        request.module, "TEMPLATE_NAME_%s" % request.node.name.split("[")[0]
    )
    test_title = getattr(
        request.module, "TEST_TITLE_%s" % request.node.name.split("[")[0]
    )

    yield (app_name, app_path, template_name, test_title)

    if legato.is_app_exist(app_name):
        legato.clean(app_name)
    pexpect.run("rm %s/%s.adef" % (app_path, app_name), encoding="utf-8")


# ====================================================================================
# Test functions
# ====================================================================================
@pytest.mark.parametrize(
    ("tpl_val", "expect_tst", "failed_reason"),
    [
        ("0", "0", ""),
        ("1", "1", ""),
        ("-1", "invalid", ""),
        ("-2", "invalid", ""),
        ("asdf", "invalid", ""),
        ("1000", "1000", ""),
        ("40000", "40000", "fails because soft kill timeout expires"),
    ],
)
def L_SandBox_0007(
    target, legato, tmpdir, tpl_val, expect_tst, failed_reason, init_sandbox
):
    """Max File Size.

    The FileSizeTest? app writes to a file until the configured fd limit,
    and also at limit+1.

    The scripts configures the config tree for various conditions
    (0, min, max, invalid value, etc.), and re-runs the FileSizeTest? legato.

    It also processes the output to determine pass/fail.

    :param target: fixture to communicate with the target
    :param legato: fixture to call useful functions regarding legato
    :param tmpdir: fixture to provide a temporary directory
                  unique to the test invocation
    :param init_sandbox: fixture to initation and cleanup the environment
    :param tpl_val: testing value
    :param expect_tst: expected value
    :param failed_reason: failed reason
    """
    sandbox(target, legato, tmpdir, tpl_val, expect_tst, failed_reason, init_sandbox)


@pytest.mark.parametrize(
    ("tpl_val", "expect_tst", "failed_reason"),
    [
        ("0", "0", ""),
        ("1", "1", ""),
        ("-1", "invalid", ""),
        ("-2", "invalid", ""),
        ("asdf", "invalid", ""),
        ("1000", "1000", ""),
        ("100000", ">=1000", ""),
        ("-1000000", "invalid", ""),
    ],
)
def L_SandBox_0010(
    target, legato, tmpdir, tpl_val, expect_tst, failed_reason, init_sandbox
):
    """Check the Number of Signals Queued.

    The NumSigQueuedTest app queues signals right at the configured
    limit, and then queues one more signal.

    The scripts configures the config tree for various conditions
    (0, min, max, invalid value, etc.), and re-runs
    the NumSigQueuedTest legato.

    It also processes the output to determine pass/fail.

    :param target: fixture to communicate with the target
    :param legato: fixture to call useful functions regarding legato
    :param tmpdir: fixture to provide a temporary directory
                  unique to the test invocation
    :param init_sandbox: fixture to initation and cleanup the environment
    :param tpl_val: testing value
    :param expect_tst: expected value
    :param failed_reason: failed reason
    """
    sandbox(target, legato, tmpdir, tpl_val, expect_tst, failed_reason, init_sandbox)


@pytest.mark.parametrize(
    ("tpl_val", "expect_tst", "failed_reason"),
    [
        ("0", "0", ""),
        ("1", "1", ""),
        ("-1", "invalid", ""),
        ("-2", "invalid", ""),
        ("asdf", "invalid", ""),
        ("4096", "4096", ""),
        ("8192", "8192", ""),
        ("8192000", ">=65536", ""),
        ("8192k", "invalid", ""),
        (
            "8192K",
            "8388608",
            "Ignored because it is trying to lock a size larger than\
      the available memory",
        ),
        (
            "1000000000",
            "1000000000",
            "Ignored because it is trying to lock a size larger than\
     the available memory",
        ),
        ("-1000000000", "invalid", ""),
    ],
)
def L_SandBox_0012(
    target, legato, tmpdir, tpl_val, expect_tst, failed_reason, init_sandbox
):
    """Mem Lock Size.

    The MemLockSizeTest app locks pages of memory right at the
    configured limit, and then attempts to lock one more page.

    The scripts configures the config tree for various conditions
    (0, min, max, invalid value, etc.),
    and re-runs the MemLockSizeTest legato.

    It also processes the output to determine pass/fail.

    :param target: fixture to communicate with the target
    :param legato: fixture to call useful functions regarding legato
    :param tmpdir: fixture to provide a temporary directory
                  unique to the test invocation
    :param init_sandbox: fixture to initation and cleanup the environment
    :param tpl_val: testing value
    :param expect_tst: expected value
    :param failed_reason: failed reason
    """
    sandbox(target, legato, tmpdir, tpl_val, expect_tst, failed_reason, init_sandbox)


@pytest.mark.parametrize(
    ("tpl_val", "expect_tst", "failed_reason"),
    [
        ("0", "invalid", ""),
        ("1", "1", "App cannot run - no available FD"),
        ("-1", "invalid", ""),
        ("-2", "invalid", ""),
        ("asdf", "invalid", ""),
        ("200", "200", ""),
        ("1024", "1024", ""),
        ("1025", "1024", ""),
        ("-100000000", "invalid", ""),
        ("100000000", "1024", ""),
    ],
)
def L_SandBox_0018(
    target, legato, tmpdir, tpl_val, expect_tst, failed_reason, init_sandbox
):
    """File Descriptor.

    The FdTest app creates different file types (file/dir/pipe/socket)
    at the configured fd limit, and also at limit+1.

    The scripts configures the config tree for various conditions
    (0, min, max, invalid value, etc.), and re-runs the FdTest legato.

    It also processes the output to determine pass/fail.

    :param target: fixture to communicate with the target
    :param legato: fixture to call useful functions regarding legato
    :param tmpdir: fixture to provide a temporary directory
                  unique to the test invocation
    :param init_sandbox: fixture to initation and cleanup the environment
    :param tpl_val: testing value
    :param expect_tst: expected value
    :param failed_reason: failed reason
    """
    sandbox(target, legato, tmpdir, tpl_val, expect_tst, failed_reason, init_sandbox)
