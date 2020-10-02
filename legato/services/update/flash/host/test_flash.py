r"""!The flash APIs test.

Set of functions to test flash APIs.

@package swUpdateFlashModule
@defgroup updateTests Update Tests

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
TEST_RESOURCES = os.path.join(os.path.abspath(os.path.dirname(__file__)), "resources")
APP_PATH = os.path.join(TEST_RESOURCES, "flashApp")
APP_NAME = "flashApp"
APP_COMPONENT_NAME = "flashApp"

PARTITIONS_MTDLIST = [
    ["tz_update", "tz_active", "tz_1", "tz_2"],
    ["rpm_update", "rpm_active", "rpm_1", "rpm_2"],
    ["modem_update", "modem_active", "modem_1", "modem_2"],
    ["aboot_update", "aboot_active", "aboot_1", "aboot_2"],
    ["boot_update", "boot_active", "boot_1", "boot_2"],
    ["system_update", "system_active", "system_1", "system_2"],
    ["lefwkro_update", "lefwkro_active", "lefwkro_1", "lefwkro_2"],
]

PARTITIONS_UBILIST = [
    ["system", "rootfs"],
    ["system", "rootfs_hs"],
    ["system", "rootfs_rhs"],
    ["system", "rootfs_srhs"],
    ["system", "rootfs_cert"],
    ["system2", "rootfs"],
    ["system2", "rootfs_hs"],
    ["system2", "rootfs_rhs"],
    ["system2", "rootfs_srhs"],
    ["system2", "rootfs_cert"],
    ["modem", "modem"],
    ["modem_2", "modem"],
    ["lefwkro", "legato_hs"],
    ["lefwkro", "legato_rhs"],
    ["lefwkro", "legato_srhs"],
    ["lefwkro", "legato_cert"],
    ["lefwkro_2", "legato_hs"],
    ["lefwkro_2", "legato_rhs"],
    ["lefwkro_2", "legato_srhs"],
    ["lefwkro_2", "legato_cert"],
]


# ======================================================================================
# Test functions
# ======================================================================================
@pytest.mark.usefixtures("app_leg")
def L_SwUpdate_Flash_UbiInfo_0001(target, legato):
    """!Get information from Ubi volume system/system 2.

    Check that can access ubi partitions and getting its info:
    system,rootfs...

    @param target: fixture to communicate with the target
    @param legato: fixture to call useful functions regarding legato
    @param app_leg: fixture to make, install and remove application
    """
    for i, value in enumerate(PARTITIONS_UBILIST):
        swilog.step("Test case %s Ubi INFO partition:" % str(i + 1))
        cmd = (
            "app runProc flashApp flashApp -- ubi-info "
            + PARTITIONS_UBILIST[i][0]
            + " "
            + PARTITIONS_UBILIST[i][1]
        )
        swilog.debug(value)
        pattern = "flashApp* has exited with exit code 0"
        target.run(cmd, withexitstatus=True)
        error_msg = (
            "[FAILED] Getting info from"
            + PARTITIONS_UBILIST[i][0]
            + ", "
            + PARTITIONS_UBILIST[i][1]
            + "failed !"
        )
        assert legato.find_in_target_log(pattern) is False, error_msg
        legato.clear_target_log()
        time.sleep(5)


@pytest.mark.usefixtures("app_leg")
def L_SwUpdate_Flash_MtdInfo_0009(target, legato):
    """!Get info from partition: tz,rpm aboot boot system lefwkro customer.

    Check that can access customer partitions:
        ssdata, lefwkro2 and a classic mtd partition lefwkro_2
        Getting info, dump the partition

    @param target: fixture to communicate with the target
    @param legato: fixture to call useful functions regarding legato
    @param app_leg: fixture to make, install and remove application
    """
    legato.ssh_to_target("app runProc flashApp flashApp -- info ssdata")
    pattern = "flashApp* has exited with exit code 0"
    error_msg = "[FAILED] Getting info from ssdata failed !"
    assert legato.find_in_target_log(pattern) is False, error_msg

    pattern = (
        "Bad Block ([0-9]*), Block ([0-9]*), "
        + "Erase Block Size ([0-9]*), Page Size ([0-9]*)"
    )
    partition_info = legato.get_from_target_log(pattern)
    if partition_info:
        swilog.info("partition Info are Bad Block: %s" % partition_info.group(1))
        swilog.info("partition Info are Block: %s" % partition_info.group(2))
        swilog.info("partition Info are Erase Block Size: %s" % partition_info.group(3))
        swilog.info("partition Info are Page Size:  %s " % partition_info.group(4))
        error_msg = "[FAILED] Getting detailed info from ssdata failed:\
         Page Size,Erase Block Size, Block,  Bad Block !"
    assert legato.find_in_target_log(pattern) is False, error_msg

    legato.clear_target_log()
    time.sleep(5)
    target.run("app runProc flashApp flashApp -- info lefwkro2", withexitstatus=True)
    pattern = "flashApp* has exited with exit code 0"
    error_msg = "[FAILED] Getting info from lefwkro2 failed !"
    assert legato.find_in_target_log(pattern) is False, error_msg

    # Check mtd info : with its name.
    legato.clear_target_log()
    time.sleep(5)
    target.run("app runProc flashApp flashApp -- info lefwkro_2", withexitstatus=True)
    pattern = "flashApp* has exited with exit code 0"
    error_msg = "[FAILED] Getting info from lefwkro_2 failed !"
    assert legato.find_in_target_log(pattern) is False, error_msg

    # Second part of the test : Dump ssdata partition.
    legato.clear_target_log()
    time.sleep(5)
    cmd = "app runProc flashApp flashApp -- dump ssdata  ssdataTest"
    target.run(cmd, withexitstatus=True)
    error_msg = "[FAILED] Dumping the ssdata  patittion failed !"
    assert legato.find_in_target_log(pattern) is False, error_msg
