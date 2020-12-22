r"""!Component Definition Files test.

Set of functions to test the Legato component definition files.

@package cflagsAndcxxflagsComponentModule
@file
\ingroup definitionFileTests
"""
import os
import re
from pytest_letp.lib import swilog

__copyright__ = "Copyright (C) Sierra Wireless Inc."
# ====================================================================================
# Constants and Globals
# ====================================================================================
# Determine the resources folder (legato apps)
TEST_RESOURCES = os.path.join(os.path.abspath(os.path.dirname(__file__)), "resources")

APP_NAME1 = "cflags_cxxflags"
APP_NAME2 = "overrideC"
APP_NAME3 = "overrideCxx"


# ====================================================================================
# Local fixtures
# ====================================================================================
def init_test(legato, tmpdir):
    """!Init the test.

    @param legato: fixture to call useful functions regarding legato
    @param tmpdir: fixture to provide a temporary directory
                unique to the test invocation
    """
    legato.clear_target_log()
    # Go to temp directory
    os.chdir(str(tmpdir))
    yield
    # Clean up application if exist
    if legato.is_app_exist(APP_NAME1):
        legato.remove(APP_NAME1)


# ====================================================================================
# Test functions
# ====================================================================================
def L_CDEF_0002(legato):
    """!Verify the core functionality of the cflags.

    And cxxflags (c++) sections of cdef files.

    @param legato: fixture to call useful functions regarding legato
    """
    swilog.step("Test 1: Generic cflag/cppflag test")

    # Make and install
    app_path = "%s/cdef/cflags_cxxflags/functionalityTest" % TEST_RESOURCES
    legato.make_install(APP_NAME1, app_path)

    # Cflag/cxxflag Section:
    # Search log for the strings that are printed when the Macro is found
    if not legato.find_in_target_log("cflag: CTESTFLAG response"):
        swilog.error(
            "Did not cflag response: cflag was not successfully passed to compiler"
        )

    if not legato.find_in_target_log("cppflag: CPPTESTFLAG response"):
        swilog.error(
            "Did not cppflag response: "
            "cppflag was not successfully passed to compiler"
        )

    # Remove the apps from the target
    legato.clean(APP_NAME1)

    swilog.step("Test 2: Default build flag override")
    test_path2 = "%s/cdef/cflags_cxxflags/overrideTest/c" % TEST_RESOURCES
    rsp = legato.make(os.path.join(test_path2, APP_NAME2), should_fail=True)

    # Search for the build error that arises
    # If -fvisbility=hidden was overriden by -fvisibility=default
    if re.search(
        r"libComponent_overrideCompC.so: undefined reference to \`hiddenFunction'", rsp
    ):
        # Ensure that only hiddenFunction's error is found
        # Meaning that defaultFunction's visibility was successfully overriden
        if re.search(
            "libComponent_overrideCompC.so: undefined reference "
            r"to \`defaultFunction'",
            rsp,
        ):
            swilog.error("Built-in flag was not overriden (C)")
        else:
            swilog.info("Built-in flag successfully overriden; App failed to build (C)")
    else:
        swilog.error("hiddenFunction was not hidden properly (C)")

    # Clean
    os.system(r"rm -rf _build_overrideC")
    test_path3 = "%s/cdef/cflags_cxxflags/overrideTest/cxx" % TEST_RESOURCES
    rsp = legato.make(os.path.join(test_path3, APP_NAME3), should_fail=True)

    # Search for the build error that arises
    # If -fvisbility=hidden was overriden by -fvisibility=default
    if re.search(
        r"libComponent_overrideCompCxx.so: undefined reference to \`hiddenFunction", rsp
    ):
        # Ensure that only hiddenFunction's error is found
        # Meaning that defaultFunction's visibility was successfully overriden
        if re.search(
            "libComponent_overrideCompCxx.so: undefined reference "
            r"to \`defaultFunction",
            rsp,
        ):
            swilog.error("Built-in flag was not overriden (Cxx)")
        else:
            swilog.info(
                "Built-in flag successfully overriden; App failed to build (Cxx)"
            )
    else:
        swilog.error("hiddenFunction was not hidden properly (Cxx)")

    failed_testcases_list = swilog.get_error_list()
    if failed_testcases_list != []:
        assert 0, "Some tests failed:\n%s" % "\n".join(failed_testcases_list)
