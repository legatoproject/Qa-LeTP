r"""!kmod tools test.

Set of functions to test the Legato kmod tools

@package kmodToolsModule
@defgroup targetToolsTests Target Tools Tests

@file
\ingroup targetToolsTests
"""
import swilog

__copyright__ = "Copyright (C) Sierra Wireless Inc."


# ======================================================================================
# Test functions
# ======================================================================================
def L_Tools_Kmod_0002(target):
    """!Verify that invalid kmod command returns and error with help screen.

    1. Run the target tool through SSH <br>
    2. Check if expected messages appears in log

    @param target: fixture to communicate with the target
    """
    swilog.info("Execute command: kmod load")
    target.sendline("kmod load")

    swilog.info("Check if expected messages appears in log")
    target.expect("Wrong number of arguments")


def L_Tools_Kmod_0003(target):
    """!Verify kernel module kmod command returns and error with help screen.

    1. Run the target tool through SSH <br>
    2. Check if expected messages appears in log

    @param target: fixture to communicate with the target
    """
    swilog.info("Execute command: kmod load example.ko")
    target.sendline("kmod load example.ko")

    swilog.info("Check if expected messages appears in log")
    target.expect("Could not load the required module, example.ko.")


def L_Tools_Kmod_0017(target):
    """!Verify that in existence kernel module kmod cmd returns an error.

    1. Run the target tool through SSH <br>
    2. Check if expected messages appears in log

    @param target: fixture to communicate with the target
    """
    swilog.info("Execute command: kmod unload example.ko")
    target.sendline("kmod unload example.ko")

    swilog.info("Check if expected messages appears in log")
    target.expect("Could not unload the required module, example.ko.")


def L_Tools_Kmod_0018(target):
    """!Verify that in existence kernel module kmod cmd returns an error.

    1. Run the target tool through ssh <br>
    2. Check if expected messages appears in log

    @param target: fixture to communicate with the target
    """
    swilog.info("Execute command: kmod load example")
    target.sendline("kmod load example")

    swilog.info("Check if expected messages appears in log")
    target.expect("Could not load the required module, example.")


def L_Tools_Kmod_0019(target):
    """!Verify that in existence kernel module kmod cmd returns an error.

    1. Run the target tool through ssh <br>
    2. Check if expected messages appears in log

    @param target: fixture to communicate with the target
    """
    swilog.info("Execute command: kmod unload example")
    target.sendline("kmod unload example")

    swilog.info("Check if expected messages appears in log")
    target.expect("Could not unload the required module, example.")
