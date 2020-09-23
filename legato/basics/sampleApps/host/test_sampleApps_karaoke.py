"""@package sampleAppsModule Sample apps test.

Set of functions to test the Legato sample apps.
"""
import os

import pexpect
import pytest

import swilog

__copyright__ = "Copyright (C) Sierra Wireless Inc."
# ====================================================================================
# Constants and Globals
# ====================================================================================
# Determine the resources folder (legato apps)
LEGATO_ROOT = os.environ["LEGATO_ROOT"]

APP_NAME_L_SampleApps_Karaoke_0001 = "karaoke"
APP_PATH_L_SampleApps_Karaoke_0001 = "%s/apps/sample/karaoke/" % (LEGATO_ROOT)


# ====================================================================================
# Test functions
# ====================================================================================
@pytest.mark.usefixtures("installapp_cleanup")
def L_SampleApps_Karaoke_0001(target, legato):
    """Script will.

        1. Make and install the test app
        2. Run the test app
        3. Check if expected messages appears in log

    Args:
        target: fixture to communicate with the target
        legato: fixture to call useful functions regarding legato
        installapp_cleanup: fixture to make, install and remove application
    """
    assert legato.is_app_exist(APP_NAME_L_SampleApps_Karaoke_0001)

    cmd = (
        "/legato/systems/current/bin/app runProc %s selector -- fast\r"
        % APP_NAME_L_SampleApps_Karaoke_0001
    )

    target.send(cmd)
    assert target.expect_in_order(
        ["Danny Boy", "Jingle Bells", "Deck The Halls"], timeout=20
    )

    cmd = "0\n"
    target.send(cmd)
    assert target.expect([pexpect.TIMEOUT, "Disabling playback."], 20)

    cmd = "1\n"
    target.send(cmd)
    assert target.expect([pexpect.TIMEOUT, "'Danny Boy' selected.  Playing now."], 20)

    cmd = "2\n"
    target.send(cmd)
    assert target.expect(
        [pexpect.TIMEOUT, "'Jingle Bells' selected.  Playing now."], 20
    )

    cmd = "3\n"
    target.send(cmd)
    assert target.expect(
        [pexpect.TIMEOUT, "'Deck The Halls' selected.  Playing now."], 20
    )

    target.sendcontrol("c")

    swilog.info("[PASSED] L_SampleApps_Karaoke_0001")
