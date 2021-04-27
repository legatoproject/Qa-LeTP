"""sandbox basic app test.

Set of functions to test the sandboxbasic app.
"""
import os
import re

import pexpect
import pytest

from pytest_letp.lib import swilog

__copyright__ = "Copyright (C) Sierra Wireless Inc."
# ====================================================================================
# Constants and Globals
# ====================================================================================
TEST_RESOURCES = os.path.join(os.path.abspath(os.path.dirname(__file__)), "resources")
APP_NAME = "testSandBoxBasic"
APP_PATH = os.path.join(TEST_RESOURCES, APP_NAME)
ROOT_DIR = "/"
SANDBOX_HOME_DIR = "/"
LEGATO_DIR = "/legato"
LEGATO_CONFIG_TREE_DIR = "/legato/systems/current/config"


# ====================================================================================
# Functions
# ====================================================================================
def sandbox_basic(target, act_name, param2="", param3="", timeout=30):
    """Run the test app with options.

    :param target: fixture to communicate with the target
    :param act_name: action name (changdir, getdir, createdir, getpid, killpid)
    :param param2: directory name/path in case changedir/createdir
    :param param3: loop number/new dir name in case changedir/createdir
    :param timeout: timeout for the command
    """
    proc_name = "test_ctrl"
    cmd = "app runProc %s --exe=%s -- %s %s %s" % (
        APP_NAME,
        proc_name,
        act_name,
        param2,
        param3,
    )
    exit_status, rsp = target.run(cmd, timeout=timeout, withexitstatus=True)
    swilog.debug(rsp)
    assert exit_status == 0, "[FAILED] Run proc failed."


def check_message_in_log(logread, msg_1, msg_2):
    """Check directory message in logread.

    :param logread: fixture to check logread on the target
    :param msg_1: first message displays on the target
    :param msg_2: second message displays on the target
    """
    assert logread.expect([pexpect.TIMEOUT, msg_1], 30) == 1, (
        "[FAILED] Cannot find out: %s" % msg_1
    )
    assert logread.expect([pexpect.TIMEOUT, msg_2], 30) == 1, (
        "[FAILED] Cannot find out: %s" % msg_2
    )


def get_pid_from_log(reg_expression, log_msg):
    """Get pid form log message.

    :param reg_expression: regular expression to get to correct pid in the message
    :param log_msg: log message that contains pid

    :returns pid: process id
    """
    pid = ""
    pid_obj = re.search(reg_expression, log_msg, re.M)

    if pid_obj:
        pid = pid_obj.group(2)
        swilog.info("PID is: %s" % pid)
    else:
        swilog.info("Cannot get PID")
    return pid


# ====================================================================================
# Test functions
# ====================================================================================
@pytest.mark.usefixtures("app_leg")
def L_SandBox_0001(target, logread):
    """Sandbox app is sandboxed.

    1) Run SB_10_20_30() from the sandbox app "sandbox.c"
    2) Verify if correct home directory has been set for \
    sandbox app (/home/sandbox)
    3) Move to root level of sandbox (/)
    4) Move beyond root level
    5) Move to legato directory (/opt/legato/)
    6) Move to legato config tree (/tmp/LegatoConfigTree)

    :param target: fixture to communicate with the target
    :param logread: fixture to check the logread on the target
    :param app_leg: fixture regarding to build, install and remove app
    """
    # NEED TO: since home dir is no longer "/home/appAPPNAME",
    # This section is kinda moot.
    # Try to move to top level of sandbox -> "/"
    # It does not go beyond. The current dir is still ROOT_DIR of sandbox
    act_name = "changedir"
    dir_change = "../.."
    loop = "1"
    sandbox_basic(target, act_name, dir_change, loop)

    dir_msg = "Change the directory to \\[%s\\]" % dir_change
    cur_dir_msg = ">> The current dir is: \\[%s\\]." % ROOT_DIR
    check_message_in_log(logread, dir_msg, cur_dir_msg)

    # Try to move beyond
    # It does not go beyond. The current dir is still ROOT_DIR of sandbox
    dir_change = ".."
    sandbox_basic(target, act_name, dir_change, loop)

    dir_msg = "Change the directory to \\[%s\\]" % dir_change
    check_message_in_log(logread, dir_msg, cur_dir_msg)

    # Try to move to LEGATO_DIR
    # It does not go beyond. The current dir is still ROOT_DIR of sandbox
    dir_change = LEGATO_DIR
    sandbox_basic(target, act_name, dir_change, loop)

    dir_msg = "Change the directory to \\[%s\\]" % dir_change
    check_message_in_log(logread, dir_msg, cur_dir_msg)

    # Try to move to LEGATO_CONFIG_TREE_DIR
    # It does not go beyond. The current dir is still ROOT_DIR of sandbox
    dir_change = LEGATO_CONFIG_TREE_DIR
    sandbox_basic(target, act_name, dir_change, loop)

    dir_msg = "Change the directory to \\[%s\\]" % dir_change
    check_message_in_log(logread, dir_msg, cur_dir_msg)


@pytest.mark.usefixtures("app_leg")
def L_SandBox_0005(target, logread):
    """BreakOut1.

    1) Run BreakOut1() from sandbox app which will follow some ways \
    of breaking out of sandbox suggested by the internet
    2) Go to home directory of sandbox app
    3) Create temp directory (foo)
    4) chroot temp directory
    5) cd ..

    :param target: fixture to communicate with the target
    :param logread: fixture to check the logread on the target
    :param app_leg: fixture regarding to build, install and remove app
    """
    # Create new directory
    act_name = "createdir"
    path = "./"
    new_dir_name = "foo"
    sandbox_basic(target, act_name, path, new_dir_name)

    create_dir_msg = "Creating directory \\[%s%s\\] in the sandbox" % (
        path,
        new_dir_name,
    )
    chroot_msg = "attempting to chroot \\[%s%s\\]." % (path, new_dir_name)
    check_message_in_log(logread, create_dir_msg, chroot_msg)

    # Check failed message does not display
    create_dir_msg_fail = "Failed to create directory"
    assert logread.expect([pexpect.TIMEOUT, create_dir_msg_fail], 5) == 0, (
        "[FAILED] Find out: %s" % create_dir_msg_fail
    )


@pytest.mark.usefixtures("app_leg")
def L_SandBox_0006(target, logread):
    """BreakOut2.

    1) Run BreakOut2() from sandbox app which will follow some ways \
    of breaking out of sandbox suggested by the internet
    2) Go to home directory of sandbox app
    3) chdir many many times (10000x)

    :param target: fixture to communicate with the target
    :param logread: fixture to check logread on the target
    :param app_leg: fixture regarding to build, install and remove app
    """
    # Try to move to top level of sandbox -> "/"
    # It does not go beyond. The current dir is still ROOT_DIR of sandbox
    act_name = "changedir"
    dir_change = SANDBOX_HOME_DIR
    loop = "1"
    sandbox_basic(target, act_name, dir_change, loop)

    dir_msg = "Change the directory to \\[%s\\]" % dir_change
    cur_dir_msg = ">> The current dir is: \\[%s\\]." % ROOT_DIR
    check_message_in_log(logread, dir_msg, cur_dir_msg)

    # Change dir ".." 10000 times
    # It does not go beyond. The current dir is still ROOT_DIR of sandbox
    dir_change = ".."
    loop = "10000"
    sandbox_basic(target, act_name, dir_change, loop)

    dir_msg = "Change the directory to \\[%s\\]" % dir_change
    cur_dir_msg_loop = ">> The current dir is: \\[%s\\]. Loop: \\[%s\\]" % (
        ROOT_DIR,
        loop,
    )
    check_message_in_log(logread, dir_msg, cur_dir_msg_loop)


@pytest.mark.usefixtures("app_leg")
def L_SandBox_0004(target, legato, logread):
    """Signaling other sandboxed apps.

    1) Run SB_110() from sandbox app \
    which will send SIG_KILL signals to running processes.
    2) Kill parent process
    3) Kill arbitrary pids since we have no knowledge of existing pids
    4) Kill itself

    :param target: fixture to communicate with the target
    :param legato: fixture to call useful functions regarding legato
    :param logread: fixture to check logread on the target
    :param app_leg: fixture regarding to build, install and remove app
    """
    # Set the parameter of the testSandBoxBasic app to "getpid"
    # Get current PID and parent PID of the application
    act_name = "getpid"
    sandbox_basic(target, act_name)
    cur_pid_msg = "Current PID: \\["
    parrent_pid_msg = "Parent PID: \\["

    # Check message get PID from sandbox app
    check_message_in_log(logread, cur_pid_msg, parrent_pid_msg)

    cur_rsp = legato.ssh_to_target(
        '/sbin/logread | grep \\"%s\\"' % cur_pid_msg, output=True
    )
    parent_rsp = legato.ssh_to_target(
        '/sbin/logread | grep \\"%s\\"' % parrent_pid_msg, output=True
    )

    # Get current PID from log read
    cur_exp = r"(.*)Current PID: \[(.*)\](.*)"
    cur_pid = get_pid_from_log(cur_exp, cur_rsp)
    assert cur_pid != "", "[FAILED] Current PID is empty."

    # Get parent PID from log read
    parent_exp = r"(.*)Parent PID: \[(.*)\](.*)"
    parent_pid = get_pid_from_log(parent_exp, parent_rsp)
    assert parent_pid != "", "[FAILED] Parent PID is empty."

    # Unable to kill parent PID
    act_name = "killpid"
    sandbox_basic(target, act_name, parent_pid)
    kill_parent_msg = (
        ">> trying to kill pid \\[%s\\], error "
        "\\[Operation not permitted\\]" % parent_pid
    )
    assert logread.expect([pexpect.TIMEOUT, kill_parent_msg], 5) == 1, (
        "[FAILED] Find out: %s" % kill_parent_msg
    )

    # Attempting to kill PID up to 100000, except for current PID
    sandbox_basic(target, act_name, "loop", "100000", timeout=60)
    kill_a_pid_msg = ">> trying to kill pid \\[100000\\], error "

    assert logread.expect([pexpect.TIMEOUT, kill_a_pid_msg], 60) == 1, (
        "[FAILED] Find out: %s" % kill_a_pid_msg
    )
