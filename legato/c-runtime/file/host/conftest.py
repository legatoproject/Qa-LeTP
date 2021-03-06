"""Fixture to test atomic files."""
import pytest
from pytest_letp.lib import swilog

__copyright__ = "Copyright (C) Sierra Wireless Inc."


# ======================================================================================
# Local fixtures
# ======================================================================================
@pytest.fixture()
def init_atomicFile(target):
    """Initialize and clean up environment.

    :param target: fixture to communicate with the target
    """
    test_file_path = "/tmp/testFile.txt"
    temp_file_extension = ".bak~~XXXXXX"
    lock_file_extension = ".lock~~XXXXXX"
    temp_file_path = test_file_path + temp_file_extension
    lock_file_path = test_file_path + lock_file_extension

    yield test_file_path

    swilog.info("cleanup")
    # Only for teardown
    target.run("rm -f %s &>/dev/null" % test_file_path)
    target.run("rm -f %s &>/dev/null" % temp_file_path)
    target.run("rm -f %s &>/dev/null" % lock_file_path)
    target.run("rm -rf /home/root/*File.txt*")
