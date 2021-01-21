"""Fixtures for updateControl."""

import os

import pytest

__copyright__ = "Copyright (C) Sierra Wireless Inc."


@pytest.fixture()
def clean_test(legato, tmpdir):
    """Fixture to clean up legato after the test.

    :param target: fixture to communicate with the target
    :param legato: fixture to call useful functions regarding legato
    :param tmpdir: fixture to provide a temporary directory
                unique to the test invocation
    """
    os.chdir(str(tmpdir))
    yield True
    legato.restore_golden_legato()


@pytest.fixture()
def init_update(read_config):
    """Get values from upgrade.xml.

    :param target: fixture to communicate with the target
    :param read_config: fixture to get value from .xml file
    """
    update_cfg = {}

    fw_path = read_config.findtext("upgrade/current_firmware_path")
    fw_pkg = read_config.findtext("upgrade/current_firmware_package")
    yoc_path = read_config.findtext("upgrade/current_yocto_path")
    yoc_pkg = read_config.findtext("upgrade/current_yocto_package")
    legato_path = read_config.findtext("upgrade/current_legato_path")
    legato_pkg = read_config.findtext("upgrade/current_legato_package")

    # Current:
    update_cfg["CURRENT_FIRMWARE_PATH"] = fw_path
    update_cfg["CURRENT_FIRMWARE_PACKAGE"] = fw_pkg

    update_cfg["CURRENT_YOCTO_PATH"] = yoc_path
    update_cfg["CURRENT_YOCTO_PACKAGE"] = yoc_pkg

    update_cfg["CURRENT_LEGATO_PATH"] = legato_path
    update_cfg["CURRENT_LEGATO_PACKAGE"] = legato_pkg

    yield update_cfg
