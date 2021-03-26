"""Kernel Module Definition Files test.

Set of functions to test the Legato kernel module definition files.
"""
# pylint: disable=too-many-lines
import os
import time
import shutil
import fnmatch
import pexpect
import pytest
from pytest_letp.lib import swilog

__copyright__ = "Copyright (C) Sierra Wireless Inc."
# ====================================================================================
# Constants and Globals
# ====================================================================================
# Determine the resources folder (legato apps)
TEST_RESOURCES = os.path.join(os.path.abspath(os.path.dirname(__file__)), "resources")
ASCENDING_ORDER = 1
DESCENDING_ORDER = -1

is_first_execution = True
TARGET_BUNDLE_PATH = "/legato/systems/current/modules/files/"

test_temp_dir = ""
campaign_temp_dir = ""


# ====================================================================================
# Functions
# ====================================================================================
def initialize(target, legato, logread, tmpdir):
    """Check every environement variable are defined Define them otherwise.

    Args:
        target: fixture to communicate with the target
        legato: fixture to call useful functions regarding legato
        logread: fixture to check log on the target
        tmpdir: fixture to provide a temporary directory
             unique to the test invocation
    """
    global is_first_execution
    global test_temp_dir
    global campaign_temp_dir

    if is_first_execution:

        # Verify environment variables
        lower_case_string = target.target_name
        kernel_variable = lower_case_string.upper() + "_KERNELROOT"
        sysroot_variable = lower_case_string.upper() + "_SYSROOT"

        assert os.environ["LEGATO_ROOT"] is not None, "LEGATO_ROOT's not set."

        failed_msg = "SYSROOT variable does not exist."
        assert os.environ.get(sysroot_variable) is not None, failed_msg

        if os.environ.get(kernel_variable) is None:
            os.environ[kernel_variable] = os.path.join(
                os.environ.get(sysroot_variable), "usr/src/kernel"
            )

        # Create all temporary directories needed
        os.environ["TEMP_DIR"] = str(tmpdir)
        os.environ["TEST_RESOURCES"] = TEST_RESOURCES

        test_temp_dir = tmpdir.mkdir("test")
        campaign_temp_dir = tmpdir.mkdir("campaign")

        # Build default legato and save package
        swilog.info("Build default legato and save package...")
        os.chdir(str(campaign_temp_dir))
        legato.make_sys("default", os.environ.get("LEGATO_ROOT"), quiet=True)

        # Build prebuilt module and save them
        swilog.info("Build prebuilt module and save them...")
        prebuild_system(legato)

        # Set the marker for future executions
        is_first_execution = False

    # Make sure we are in the proper directory
    os.chdir(str(test_temp_dir))

    # Turn off the logread output in stdout
    logread.log_off()


def finalize(legato):
    """Compile the default sdef and update the target with it.

    It will reinitialise the modules on the target.

    Args:
        legato: fixture to call useful functions regarding legato
    """
    # Clean target by restore golden legato
    legato.restore_golden_legato()

    # Wait for the unloading to be performed
    # Then verify every modules have been unloaded
    failed_msg = (
        "Some modules have not been unloaded properly "
        "after default legato installation."
    )
    assert not check_presence(legato, "L_MDEF_"), failed_msg


def check_presence(legato, module_name):
    """Check whether a module is loaded or not.

    Args:
        legato: fixture to call useful functions regarding legato
        module_name: name of module

    Returns:
        True: module is loaded successfully
        False: module is not loaded properly
    """
    swilog.info("Check presence.")
    exit_code = legato.ssh_to_target('/sbin/lsmod | grep -F "%s "' % module_name)
    # To improve
    if exit_code == 0:
        return True
    else:
        time.sleep(20)
        swilog.info("Try to check presence again...")
        exit_code = legato.ssh_to_target('/sbin/lsmod | grep -F "%s "' % module_name)
        swilog.info(exit_code)
        return bool(exit_code == 0)


def check_file_presence(legato, folder_path, file_name):
    """Check whether a file exist or not.

    Args:
        legato: fixture to call useful functions regarding legato
        folder_path: path of folder
        file_name: name of file to check

    Returns:
        True: file exists
        False: file does not exist
    """
    exit_code = legato.ssh_to_target(
        'ls "%s" | grep -F "%s"' % (folder_path, file_name)
    )
    return bool(exit_code == 0)


def find_all_occurences_in_logread(legato, search_pattern):
    """Retrieve all entries in logread containing the search pattern.

    Args:
        legato: fixture to call useful functions regarding legato
        search_pattern: pattern for searching

    Returns:
        result: all entries in logread containing
        the search pattern
    """
    result = []

    # Retrieve content of logread an split by lines
    full_log = (legato.ssh_to_target("/sbin/logread | cut -d '|' -f 3-", True)).split(
        "\n"
    )

    # Search all lines
    for line in full_log:
        if line.find(search_pattern) != -1:
            result.append(line)
    return result


def display_errors():
    """Get the errors list.

    Returns:
        output: string of all errors in the test.
    """
    output = "\n"
    for err in swilog.get_error_list():
        output += err + "\n"
    return output


def check_order(logread, order, ordered_list):
    """Check order of appearance for strings contained.

    in ordered_list following order.

    Args:
        logread: fixture to check log on the target
        order: order type
               ASCENDING_ORDER = 1
               DESCENDING_ORDER = -1
        ordered_list: the list needs to be checked

    Returns:
        A tuple: (test_result, observed_list)
        test_result: the result of checking. True or False
        observed_list: the list after checked
    """
    list_checked = ordered_list
    test_result = True
    observed_list = ""

    # Process check
    if order is not DESCENDING_ORDER and order is not ASCENDING_ORDER:
        swilog.error("CheckOrder: Value of order parameter is out of bound")
        assert False, "Error in check_order Function"
    if order == DESCENDING_ORDER:
        list_checked = ordered_list[::-1]

    # Use the expect function to determine the order of appearance
    for i in range(0, len(list_checked)):
        try:
            index = logread.expect(list_checked)
            observed_list += "\n" + list_checked[index]
            if index != i:
                test_result = False
        except pexpect.EOF:
            swilog.error("check_order: Logread stopped unexpectedly")
            test_result = False
        except pexpect.TIMEOUT:
            swilog.error(
                "check_order: None of the expected output "
                "has been found. Expect timed out"
            )
            test_result = False
    return test_result, observed_list


def check_loading_order(logread, order, ordered_list):
    """Transform a list of module name into loading message in logread.

    Args:
        logread: fixture to check log on the target
        order: order type
               ASCENDING_ORDER = 1
               DESCENDING_ORDER = -1
        ordered_list: the list that needs to be checked

    Returns:
        The result of check_order function. \
        It is a tuple (test_result, observed_list)
    """
    list_checked = []
    for element in ordered_list:
        list_checked.append("New kernel module '%s.ko'" % element)
    return check_order(logread, order, list_checked)


def check_unloading_order(logread, order, ordered_list):
    """Transform a list of module name into unloading message in logread.

    Args:
        logread: fixture to check log on the target
        order: order type
             ASCENDING_ORDER = 1
             DESCENDING_ORDER = -1
        ordered_list: the list needs to be checked

    Returns:
        The result of check_order function. \
        It is a tuple (test_result, observed_list)
    """
    list_checked = []
    for e in ordered_list:
        list_checked.append("Removed kernel module '%s.ko'" % e)
    return check_order(logread, order, list_checked)


def install_system(legato, test_name):
    """Compile the provided sdef and update the target with it.

    Function called in each test. It's not part of kmod setup because it needs
    parameters to work.

    Args:
        legato: fixture to call useful functions regarding legato
        test_name: test case name
    """
    # Sdef file
    sdef_file = test_name + ".sdef"
    source_file_path = os.path.join(TEST_RESOURCES, sdef_file)
    assert os.path.exists(source_file_path), "Sdef file does not exist"

    # Compile and update target
    swilog.info("Compile and update target...")
    legato.make_install_sys(test_name, source_file_path, quiet=True)

    # Wait for the module to be loaded
    # TO IMPROVE
    time.sleep(60)


def prebuild_system(legato):
    """Compile the provided sdef This script could be part of initialize.

    But it will make test execution longer.

    Args:
        legato: fixture to call useful functions regarding legato
    """
    # Sdef file
    sdef_file = "L_MDEF_preBuild.sdef"
    source_file_path = os.path.join(TEST_RESOURCES, sdef_file)
    assert os.path.exists(source_file_path), "Sdef file does not exist"

    # Compile and store only the .ko files
    swilog.info("Compile and store only the .ko files...")
    legato.make_sys("L_MDEF_prebuild", source_file_path, quiet=True)
    time.sleep(3)  # Wait for the module to be loaded

    matches = []
    for root, dirnames, filenames in os.walk(os.getcwd()):
        for filename in fnmatch.filter(filenames, "*.ko"):
            swilog.info(dirnames)
            matches.append(os.path.join(root, filename))
            shutil.copyfile(
                os.path.join(root, filename), os.path.join(os.getcwd(), filename)
            )


# ====================================================================================
# Local fixtures
# ====================================================================================
@pytest.fixture(autouse=True)
def mdef_setup(target, legato, logread, tmpdir):
    """Init and cleanup the test.

    Args:
        target: fixture to communicate with the target
        legato: fixture to call useful functions regarding legato
        logread: fixture to check log on the target
        tmpdir: fixture to provide a temporary directory
                unique to the test invocation
    """
    initialize(target, legato, logread, tmpdir)
    yield
    finalize(legato)


# ====================================================================================
# Test functions
# ====================================================================================
def L_MDEF_0001(legato):
    """Verify that mdef can be use to include kernel module to be built.

    This script will
        1. Create an update package (load: auto)
        2. Verify loading of the module
        3. Stop Legato. Check module is unloaded.
        4. Start Legato. Check module is loaded
        5. Compile the default package and update the target with it

    Args:
        legato: fixture to call useful functions regarding legato
    """
    # Verify existence of environment variables and files needed.
    # Prepare compilation
    test_name = "L_MDEF_0001"
    list_modules = [test_name]
    test_passed = True

    # Compile and update target
    install_system(legato, test_name)

    # Verify mod has been loaded
    swilog.step("Step 2: Verify mod has been loaded...")
    for module in list_modules:
        if not check_presence(legato, module):
            test_passed = False
            swilog.error(
                "Step 2: Kernel module %s has not been properly loaded" % module
            )
        else:
            swilog.step("Step 2: Kernel module %s has been properly loaded" % module)

    # Stop legato
    swilog.step("Step 3: Stopping legato...")
    legato.legato_stop()

    # Verify mod has been loaded
    swilog.step("Step 4: Verify mod has been unloaded...")
    for module in list_modules:
        if check_presence(legato, module):
            test_passed = False
            swilog.error(
                "Step 4: Kernel module %s has not been properly unloaded" % module
            )

    # Start legato
    swilog.step("Step 5: Starting legato...")
    legato.legato_start()

    # Verify mod has been loaded
    swilog.step("Step 6: Verify mod has been loaded...")
    for module in list_modules:
        if not check_presence(legato, module):
            test_passed = False
            swilog.error(
                "Step 6: Kernel module %s has not been properly loaded" % module
            )

    # End of script
    assert test_passed, display_errors()


def L_MDEF_0002(legato):
    """Verify that mdef can be use to include prebuilt kernel module.

    This script will
        1. Create an update package (load: auto)
        2. Verify loading of the module
        3. Stop Legato. Check module has been unloaded
        4. Start Legato. Check module has been loaded
        5. Compile the default package and update the target with it

    Args:
        legato: fixture to call useful functions regarding legato
    """
    # Verify existence of environment variables and files needed.
    # Prepare compilation
    test_name = "L_MDEF_0002"
    list_modules = ["L_MDEF_prebuilt_0"]
    test_passed = True

    # Compile and update target
    install_system(legato, test_name)

    # Verify mod has been loaded
    swilog.step("Step 2: Verify mod has been loaded...")
    for module in list_modules:
        if not check_presence(legato, module):
            test_passed = False
            swilog.error(
                "Step 2: Kernel module %s has not been properly loaded" % module
            )

    # Stop legato
    swilog.step("Step 3: Stopping legato...")
    legato.legato_stop()

    # Verify mod has been loaded
    swilog.step("Step 4: Verify mod has been unloaded...")
    for module in list_modules:
        if check_presence(legato, module):
            test_passed = False
            swilog.error(
                "Step 4: Kernel module %s has not been properly unloaded" % module
            )

    # Start legato
    swilog.step("Step 5: Starting legato...")
    legato.legato_start()

    # Verify mod has been loaded
    swilog.step("Step 6: Verify mod has been loaded...")
    for module in list_modules:
        if not check_presence(legato, module):
            test_passed = False
            swilog.error(
                "Step 6: Kernel module %s has not been properly loaded" % module
            )

    # End of script
    assert test_passed, display_errors()


def L_MDEF_0003(legato):
    """Check Mdef error case and system including prebuilt.

    And to be built kernel module.

    This script will
        1. Create an update package (load: auto) with both sources and
        prebuilt section in mdef file
        2. Check that error message is consistent
        5. Compile the default package and update the target with it

    Args:
        legato: fixture to call useful functions regarding legato
    """
    # Sdef file
    sdef_file = "L_MDEF_0003.sdef"
    source_file_path = os.path.join(TEST_RESOURCES, sdef_file)
    assert os.path.exists(source_file_path), "Sdef file does not exist"

    # Compile and update target
    returned_value = legato.make_sys(
        source_file_path, source_file_path, should_fail=True
    )
    err_msg = "error: Use either 'sources' or 'preBuilt' section."
    failed_msg = "Mksys didn't returned the expected sentence"
    assert returned_value.find(err_msg) != -1, failed_msg


def L_MDEF_0005(legato, logread):
    """Verify that mdef including kernel module built from source.

    are able to create multiple level dependencies.

    This script will
        1. Create an update package (load: auto)
        2. Verify modules are loaded
        3. Stop Legato
        4. Verify modules are unloaded
        5. Start Legato
        6. Verify modules are loaded
        7. Compile the default package and update the target with it

    Args:
        legato: fixture to call useful functions regarding legato
        logread: fixture to check log on the target
    """
    # Verify existence of environment variables and files needed.
    # Prepare compilation
    test_name = "L_MDEF_0005"
    test_passed = True

    # Warning: Has to be in the expected loading order
    list_modules = ["L_MDEF_0005_2", "L_MDEF_0005_1", "L_MDEF_0005_0"]

    # Compile and update target
    install_system(legato, test_name)

    # Verify mod has been loaded
    swilog.step("Step 2: Verify mod has been loaded...")
    for module in list_modules:
        if not check_presence(legato, module):
            test_passed = False
            swilog.error(
                "Step 2: Kernel module %s has not been properly loaded" % module
            )

    # Verify loading order
    (result, message) = check_loading_order(logread, ASCENDING_ORDER, list_modules)
    if not result:
        test_passed = False
        swilog.error(
            "Step 2: Kernel module aren't loaded "
            "in the expected order. Observed: %s" % message
        )

    # Stop legato
    swilog.step("Step 3: Stopping legato...")
    legato.legato_stop()

    # Verify mod has been unloaded
    swilog.step("Step 4: Verify mod has been unloaded...")
    for module in list_modules:
        if check_presence(legato, module):
            test_passed = False
            swilog.error(
                "Step 4: Kernel module %s has not been properly unloaded" % module
            )

    # Verify unloading order
    (result, message) = check_unloading_order(logread, DESCENDING_ORDER, list_modules)
    if not result:
        test_passed = False
        swilog.error(
            "Step 4: Kernel module aren't unloaded "
            "in the expected order. Observed: %s" % message
        )

    # Start legato
    swilog.step("Step 5: Starting legato...")
    legato.legato_start()

    # Verify mod has been loaded
    swilog.step("Step 6: Verify mod has been loaded...")
    for module in list_modules:
        if not check_presence(legato, module):
            test_passed = False
            swilog.error(
                "Step 6: Kernel module %s has not been properly loaded" % module
            )

    # Verify loading order
    (result, message) = check_loading_order(logread, ASCENDING_ORDER, list_modules)
    if not result:
        test_passed = False
        swilog.error(
            "Step 6: Kernel module aren't loaded "
            "in the expected order. Observed: %s" % message
        )

    # End of script
    assert test_passed, display_errors()


def L_MDEF_0006(legato, logread):
    """Verify that mdef including prebuilt kernel module.

    are able to create multiple level dependencies.

    This script will
        1. Create an update package (load: auto)
        2. Verify modules are loaded
        3. Stop Legato
        4. Verify modules are unloaded
        5. Start Legato
        6. Verify modules are loaded
        7. Compile the default package and update the target with it

    Args:
        legato: fixture to call useful functions regarding legato
        logread: fixture to check log on the target
    """
    # Verify existence of environment variables and files needed.
    # Prepare compilation
    test_name = "L_MDEF_0006"
    test_passed = True

    # Warning: Has to be in the expected loading order
    list_modules = ["L_MDEF_prebuilt_2", "L_MDEF_prebuilt_1", "L_MDEF_prebuilt_0"]

    # Compile and update target
    install_system(legato, test_name)

    # Verify mod has been loaded
    swilog.step("Step 2: Verify mod has been loaded...")
    for module in list_modules:
        if not check_presence(legato, module):
            test_passed = False
            swilog.error(
                "Step 2: Kernel module %s has not been properly loaded" % module
            )

    # Verify loading order
    (result, message) = check_loading_order(logread, ASCENDING_ORDER, list_modules)
    if not result:
        test_passed = False
        swilog.error(
            "Step 2: Kernel module aren't loaded in "
            "the expected order. Observed: %s" % message
        )

    # Stop legato
    swilog.step("Step 3: Stopping legato...")
    legato.legato_stop()

    # Verify mod has been unloaded
    swilog.step("Step 4: Verify mod has been unloaded...")
    for module in list_modules:
        if check_presence(legato, module):
            test_passed = False
            swilog.error(
                "Step 4: Kernel module %s has not been properly unloaded" % module
            )

    # Verify unloading order
    (result, message) = check_unloading_order(logread, DESCENDING_ORDER, list_modules)
    if not result:
        test_passed = False
        swilog.error(
            "Step 4: Kernel module aren't unloaded in "
            "the expected order. Observed: %s" % message
        )

    # Start legato
    swilog.step("Step 5: Starting legato...")
    legato.legato_start()

    # Verify mod has been loaded
    swilog.step("Step 6: Verify mod has been loaded...")
    for module in list_modules:
        if not check_presence(legato, module):
            test_passed = False
            swilog.error(
                "Step 6: Kernel module %s has not been properly loaded" % module
            )

    # Verify loading order
    (result, message) = check_loading_order(logread, ASCENDING_ORDER, list_modules)
    if not result:
        test_passed = False
        swilog.error(
            "Step 6: Kernel module aren't loaded in "
            "the expected order. Observed: %s" % message
        )

    # End of script
    assert test_passed, display_errors()


def L_MDEF_0009(legato):
    """Verify that mdef able to take more than two sources using {}.

    This script will
        1. Create an update package (load: auto)
        2. Verify loading of the module
        3. Stop Legato
        4. Start Legato
        5. Compile the default package and update the target with it

    Args:
        legato: fixture to call useful functions regarding legato
    """
    # Verify existence of environment variables and files needed.
    # Prepare compilation
    test_name = "L_MDEF_0009"
    test_passed = True

    # Warning: Has to be in the expected loading order
    list_modules = [test_name]

    # Compile and update target
    install_system(legato, test_name)

    # Verify mod has been loaded
    swilog.step("Step 2: Verify mod has been loaded...")
    for module in list_modules:
        if not check_presence(legato, module):
            test_passed = False
            swilog.error(
                "Step 2: Kernel module %s has not been properly loaded" % module
            )

    # Stop legato
    swilog.step("Step 3: Starting legato...")
    legato.legato_stop()

    # Verify mod has been loaded
    swilog.step("Step 4: Verify mod has been unloaded...")
    for module in list_modules:
        if check_presence(legato, module):
            test_passed = False
            swilog.error(
                "Step 4: Kernel module %s has not been properly unloaded" % module
            )

    # Start legato
    swilog.step("Step 5: Starting legato...")
    legato.legato_start()

    # Verify mod has been loaded
    swilog.step("Step 6: Verify mod has been loaded...")
    for module in list_modules:
        if not check_presence(legato, module):
            test_passed = False
            swilog.error(
                "Step 6: Kernel module %s has not been properly loaded" % module
            )

    # End of script
    assert test_passed, display_errors()


def L_MDEF_0010(legato):
    """Verify mksys is able to handle empty kernel modules section.

    This script will
        1. Create an update package (load: auto)
        2. Verify loading of the module
        3. Stop Legato
        4. Start Legato
        5. Compile the default package and update the target with it

    Args:
        legato: fixture to call useful functions regarding legato
    """
    # Verify existence of environment variables and files needed.
    # Prepare compilation
    test_name = "L_MDEF_0010"
    test_passed = True

    # Warning: Has to be in the expected loading order
    list_modules = [test_name]

    # Compile and update target
    install_system(legato, test_name)

    # Verify mod has been loaded
    swilog.step("Step 2: Verify mod has been loaded...")
    for module in list_modules:
        if check_presence(legato, module):
            test_passed = False
            swilog.error(
                "Step 2: Kernel module %s has been unexpectedly loaded" % module
            )

    # Stop legato
    swilog.step("Step 3: Stopping legato...")
    legato.legato_stop()

    # Start legato
    swilog.step("Step 4: Starting legato...")
    legato.legato_start()

    # Verify mod has been loaded
    swilog.step("Step 5: Verify mod has been loaded...")
    for module in list_modules:
        if check_presence(legato, module):
            test_passed = False
            swilog.error(
                "Step 5: Kernel module %s has not been properly loaded" % module
            )

    # End of script
    assert test_passed, display_errors()


def L_MDEF_0011(legato):
    """Verify mdef is not loaded when load is set to manual.

    This script will
        1. Create an update package (load: manual)
        2. Verify loading of the module
        3. Stop Legato
        4. Start Legato
        5. Compile the default package and update the target with it

    Args:
        legato: fixture to call useful functions regarding legato
    """
    # Verify existence of environment variables and files needed.
    # Prepare compilation
    test_name = "L_MDEF_0011"
    test_passed = True

    # Warning: Has to be in the expected loading order
    list_modules = [test_name]

    # Compile and update target
    install_system(legato, test_name)

    # Verify mod has been loaded
    swilog.step("Step 2: Verify mod has not been loaded...")
    for module in list_modules:
        if check_presence(legato, module):
            test_passed = False
            swilog.error(
                "Step 2: Kernel module %s has been unexpectedly loaded" % module
            )

    folder_path = "/legato/systems/current/modules"
    if not check_file_presence(legato, folder_path, test_name):
        test_passed = False
        swilog.error("Step 3: Kernel module %s is not present in folder" % module)

    # Stop legato
    swilog.step("Step 4: Stopping legato...")
    legato.legato_stop()

    # Start legato
    swilog.step("Step 5: Starting legato...")
    legato.legato_start()

    # Verify mod has been loaded
    swilog.step("Step 6: Verify mod has not been loaded...")
    for module in list_modules:
        if check_presence(legato, module):
            test_passed = False
            swilog.error(
                "Step 6: Kernel module %s has been unexpectedly loaded" % module
            )

    if not check_file_presence(legato, folder_path, module):
        test_passed = False
        swilog.error("Step 7: Kernel module %s is not present in folder" % module)

    # End of script
    assert test_passed, display_errors()


def L_MDEF_0012(legato):
    """Verify mksys is able to handle kernel module with same name.

    This script will
        1. Create an update package (load: auto)
        2. Try to compile a module with error in pathing

    Args:
        legato: fixture to call useful functions regarding legato
    """
    # Verify existence of environment variables and files needed.
    # Prepare compilation
    test_name = "L_MDEF_0012"

    # Sdef file
    sdef_file = test_name + ".sdef"
    source_file_path = os.path.join(TEST_RESOURCES, sdef_file)
    assert os.path.exists(source_file_path), "Sdef file does not exist"

    # Compile and update target

    returned_value = legato.make_sys(
        source_file_path, source_file_path, should_fail=True
    )

    err_msg = "error: Module '%s' added to the system more than once." % test_name
    failed_msg = "Mksys didn't returned the expected sentence"
    assert returned_value.find(err_msg) != -1, failed_msg


def L_MDEF_0014(legato):
    """Verify relative path could be taken by specifying moduleSearch.

    This script will
        1. Create an update package (load: auto)
        2. Verify loading of the module
        3. Stop Legato
        4. Start Legato
        5. Compile the default package and update the target with it

    Args:
        legato: fixture to call useful functions regarding legato
    """
    # Verify existence of environment variables and files needed.
    # Prepare compilation

    test_name = "L_MDEF_0014"
    test_passed = True

    # Warning: Has to be in the expected loading order
    list_modules = [test_name]

    # Compile and update target
    install_system(legato, test_name)

    # Verify mod has been loaded
    swilog.step("Step 2: Verify mod has been loaded...")
    for module in list_modules:
        if not check_presence(legato, module):
            test_passed = False
            swilog.error(
                "Step 2: Kernel module %s has not been properly loaded" % module
            )

    # Stop legato
    swilog.step("Step 3: Stopping legato...")
    legato.legato_stop()

    # Verify mod has been loaded
    swilog.step("Step 4: Verify mod has been unloaded...")
    for module in list_modules:
        if check_presence(legato, module):
            test_passed = False
            swilog.error(
                "Step 4: Kernel module %s has not been properly unloaded" % module
            )

    # Start legato
    swilog.step("Step 5: Starting legato...")
    legato.legato_start()

    # Verify mod has been loaded
    swilog.step("Step 6: Verify mod has been loaded...")
    for module in list_modules:
        if not check_presence(legato, module):
            test_passed = False
            swilog.error(
                "Step 6: Kernel module %s has not been properly loaded" % module
            )

    # End of script
    assert test_passed, display_errors()


def L_MDEF_0015(legato):
    """Verify mksys should be able to handle non existence path and file.

    This script will
        1. Create an update package (load: auto)
        2. Try to compile a module with error in pathing

    Args:
        legato: fixture to call useful functions regarding legato
    """
    # Verify existence of environment variables and files needed.
    # Prepare compilation
    test_name = "L_MDEF_0015"

    # Sdef file
    sdef_file = test_name + ".sdef"
    source_file_path = os.path.join(TEST_RESOURCES, sdef_file)
    assert os.path.exists(source_file_path), "Sdef file does not exist"

    # Compile and update target
    returned_value = legato.make_sys(
        source_file_path, source_file_path, should_fail=True
    )

    err_msg = (
        "error: Can't find definition file (.mdef) for module "
        "specification 'L_MDEF_0015.mdef'."
    )
    failed_msg = "Mksys didn't returned the expected sentence"
    assert returned_value.find(err_msg) != -1, failed_msg


def L_MDEF_0016(legato):
    """Verify mksys should be able to handle non existence .c file.

    under source.

    This script will
        1. Create an update package (load: auto)
        2. Try to compile a module with error in pathing

    Args:
        legato: fixture to call useful functions regarding legato
    """
    # Verify existence of environment variables and files needed.
    # Prepare compilation
    test_name = "L_MDEF_0016"

    # Sdef file
    sdef_file = test_name + ".sdef"
    source_file_path = os.path.join(TEST_RESOURCES, sdef_file)
    assert os.path.exists(source_file_path), "Sdef file does not exist"

    # Compile and update target
    returned_value = legato.make_sys(
        source_file_path, source_file_path, should_fail=True
    )

    err_msg = "error: File 'missingSource.c' does not exist."
    failed_msg = "Mksys didn't returned the expected sentence"
    assert returned_value.find(err_msg) != -1, failed_msg


def L_MDEF_0017(legato):
    """Verify mksys should be able to handle both relative path.

    and absolute path.

    This script will
        1. Create an update package (load: auto)
        2. Verify loading of the module
        3. Stop Legato
        4. Start Legato
        5. Compile the default package and update the target with it

    Args:
        legato: fixture to call useful functions regarding legato
    """
    # Verify existence of environment variables and files needed.
    # Prepare compilation
    test_name = "L_MDEF_0017"
    test_passed = True

    # Warning: Has to be in the expected loading order
    list_modules = ["L_MDEF_0017_0", "L_MDEF_0017_1"]

    # Compile and update target
    install_system(legato, test_name)

    # Verify mod has been loaded
    swilog.step("Step 2: Verify mod has been loaded...")
    for module in list_modules:
        if not check_presence(legato, module):
            test_passed = False
            swilog.error(
                "Step 2: Kernel module %s has not been properly loaded" % module
            )

    # Stop legato
    swilog.step("Step 3: Stopping legato...")
    legato.legato_stop()

    # Verify mod has been loaded
    swilog.step("Step 4: Verify mod has been unloaded...")
    for module in list_modules:
        if check_presence(legato, module):
            test_passed = False
            swilog.error(
                "Step 4: Kernel module %s has not been properly unloaded" % module
            )

    # Start legato
    swilog.step("Step 5: Starting legato...")
    legato.legato_start()

    # Verify mod has been loaded
    swilog.step("Step 6: Verify mod has been loaded...")
    for module in list_modules:
        if not check_presence(legato, module):
            test_passed = False
            swilog.error(
                "Step 6: Kernel module %s has not been properly loaded" % module
            )

    # End of script
    assert test_passed, display_errors()


def L_MDEF_0018(legato):
    """Verify that files, bin and scripts directory is bundled.

    under system module directory.

    This script will
    1. Create an update package (load: auto)
    2. Verify loading of the module
    3. Verify presence of the module file
    4. Verify presence of the bundled files

    Args:
        legato: fixture to call useful functions regarding legato
    """
    # Verify existence of environment variables and files needed.
    # Prepare compilation
    test_name = "L_MDEF_0018"
    test_passed = True

    # Warning: Has to be in the expected loading order
    list_modules = ["L_MDEF_0018_0"]

    # Compile and update target
    install_system(legato, test_name)

    # Verify mod has been loaded
    swilog.step("Step 2: Verify mod has been loaded...")
    for module in list_modules:
        if not check_presence(legato, module):
            test_passed = False
            swilog.error(
                "Step 2: Kernel module %s has not been properly loaded" % module
            )

    swilog.step("Step 3: Verify module file is present...")
    folder_path = "/legato/systems/current/modules"
    if not check_file_presence(legato, folder_path, test_name):
        test_passed = False
        swilog.error("Step 3: Module file isn't present")

    swilog.step("Step 4: Verify bundled files are present...")
    files = ["text.txt", "dir", "scripts"]
    folder_path = "/legato/systems/current/modules/files/L_MDEF_0018_0"
    for file_name in files:
        if not check_file_presence(legato, folder_path, file_name):
            test_passed = False
            swilog.error("Step 3: File or directory %s isn't present" % file_name)

    files = ["install.sh", "remove.sh"]
    folder_path = "/legato/systems/current/modules/files/L_MDEF_0018_0/scripts"
    for file_name in files:
        if not check_file_presence(legato, folder_path, file_name):
            test_passed = False
            swilog.error(
                "Step 3: File or directory scripts/%s isn't present" % file_name
            )

    files = ["dir.txt"]
    folder_path = "/legato/systems/current/modules/files/L_MDEF_0018_0/dir"
    for file_name in files:
        if not check_file_presence(legato, folder_path, file_name):
            test_passed = False
            swilog.error("Step 3: File dir/%s isn't present" % file_name)

    # End of script
    assert test_passed, display_errors()


def L_MDEF_0019(legato):
    """Invalid path in  bundles section.

    This script will
        1. Create an update package (load: auto)
        2. Try to compile a module with error

    Args:
        legato: fixture to call useful functions regarding legato
    """
    # Verify existence of environment variables and files needed.
    # Prepare compilation
    test_name = "L_MDEF_0019"

    # Sdef file
    sdef_file = test_name + ".sdef"
    source_file_path = os.path.join(TEST_RESOURCES, sdef_file)
    assert os.path.exists(source_file_path), "Sdef file does not exist"

    # Compile and update target
    returned_value = legato.make_sys(
        source_file_path, source_file_path, should_fail=True
    )

    err_msg = "error: File not found: '/ErrorInPath/text.txt'."
    failed_msg = "Mksys didn't returned the expected sentence"
    assert returned_value.find(err_msg) != -1, failed_msg


def L_MDEF_0020(legato):
    """Test to load more than one kernelModule with scripts.

    This script will
        1. Create an update package (load: auto)
        2. Verify loading of the module

    Args:
        legato: fixture to call useful functions regarding legato
    """
    # Verify existence of environment variables and files needed.
    # Prepare compilation
    test_name = "L_MDEF_0020"
    test_passed = True

    # Warning: Has to be in the expected loading order
    list_modules = ["L_MDEF_0020_0", "L_MDEF_0020_1"]

    # Compile and update target
    install_system(legato, test_name)

    # Verify mod has been loaded
    swilog.step("Step 2: Verify mod has been loaded...")
    for module in list_modules:
        if not check_presence(legato, module):
            test_passed = False
            swilog.error(
                "Step 2: Kernel module %s has not been properly loaded" % module
            )

    # End of script
    assert test_passed, display_errors()


def L_MDEF_0021(target, legato):
    """Load kernel module manual with script.

    This script will
        1. Create an update package (load: auto)
        2. Verify loading of the module
        3. Insert modules
        4. Remove modules
        5. Insert independant module

    Args:
        target: fixture to communicate with the target
        legato: fixture to call useful functions regarding legato
    """
    # Verify existence of environment variables and files needed.
    # Prepare compilation
    test_name = "L_MDEF_0021"
    test_passed = True

    # Warning: Has to be in the expected loading order
    list_modules = ["L_MDEF_0021_0", "L_MDEF_0021_1"]

    # Compile and update target
    install_system(legato, test_name)

    # Verify mod has been loaded
    swilog.step("Step 2: Verify auto loading mod has been loaded...")
    if not check_presence(legato, "L_MDEF_0021_0"):
        test_passed = False
        swilog.error("Step 2: Kernel module L_MDEF_0021_0 has not been properly loaded")

    # Insert manual mod
    swilog.step("Step 3: Insert manual mod...")
    cmd = "/sbin/insmod /legato/systems/current/modules/L_MDEF_0021_1.ko"
    exit_code, rsp = target.run(cmd, withexitstatus=True)
    swilog.debug(rsp)
    if exit_code != 0:
        test_passed = False
        swilog.error("Insertion of manual loading mod has failed")

    # Verify mod has been loaded
    swilog.step("Step 4: Verify mods have been loaded...")
    for module in list_modules:
        if not check_presence(legato, module):
            test_passed = False
            swilog.error(
                "Step 4: Kernel module %s has not been properly loaded" % module
            )

    # End of script
    assert test_passed, display_errors()


def L_MDEF_0022(legato):
    """Specify install and remove in your script section.

    This script will
        1. Create an update package (load: auto)
        2. Try to compile a module with error

    Args:
        legato: fixture to call useful functions regarding legato
    """
    # Verify existence of environment variables and files needed.
    # Prepare compilation
    test_name = "L_MDEF_0022"

    # Sdef file
    sdef_file = test_name + ".sdef"
    source_file_path = os.path.join(TEST_RESOURCES, sdef_file)
    assert os.path.exists(source_file_path), "Sdef file does not exist"

    # Compile and update target
    returned_value = legato.make_sys(
        source_file_path, source_file_path, should_fail=True
    )
    failed_msg = "Mksys didn't returned the expected sentence"
    assert returned_value.find("error: Unexpected character") != -1, failed_msg


def L_MDEF_0023(legato):
    """Relative path in script section of mdef.

    This script will
        1. Create an update package with relative pathing (load: auto)
        2. Verify loading of the module

    Args:
        legato: fixture to call useful functions regarding legato
    """
    # Verify existence of environment variables and files needed.
    # Prepare compilation
    test_name = "L_MDEF_0023"
    test_passed = True

    # Warning: Has to be in the expected loading order
    list_modules = [test_name]

    # Compile and update target
    swilog.step("Step 1: Compiling using relative path...")
    swilog.warning(
        "WARNING: Works only if you run the test script from qa/letp/ directory"
    )
    install_system(legato, test_name)

    # Verify mod has been loaded
    swilog.step("Step 2: Verify mod has been loaded...")
    for module in list_modules:
        if not check_presence(legato, module):
            test_passed = False
            swilog.error(
                "Step 2: Kernel module %s has not been properly loaded" % module
            )

    # End of script
    assert test_passed, display_errors()


def L_MDEF_0024(legato):
    """Put more than one scripts path in install.

    or remove section script section.

    This script will
        1. Create an update package (load: auto)
        2. Try to compile a module with error in mdef

    Args:
        legato: fixture to call useful functions regarding legato
    """
    # Verify existence of environment variables and files needed.
    # Prepare compilation
    test_name = "L_MDEF_0024"

    # Sdef file
    sdef_file = test_name + ".sdef"
    source_file_path = os.path.join(TEST_RESOURCES, sdef_file)
    assert os.path.exists(source_file_path), "Sdef file does not exist"

    # Compile and update target
    returned_value = legato.make_sys(
        source_file_path, source_file_path, should_fail=True
    )

    err_msg = "error: Internal error: Multiple install scripts not allowed."
    failed_msg = "Mksys didn't returned the expected sentence"
    assert returned_value.find(err_msg) != -1, failed_msg


def L_MDEF_0025(legato):
    """Put more than one scripts section in mdef file.

    This script will
        1. Create an update package (load: auto)
        2. Try to compile a module with error in mdef

    Args:
        legato: fixture to call useful functions regarding legato
    """
    # Verify existence of environment variables and files needed.
    # Prepare compilation
    test_name = "L_MDEF_0025"

    # Sdef file
    sdef_file = test_name + ".sdef"
    source_file_path = os.path.join(TEST_RESOURCES, sdef_file)
    assert os.path.exists(source_file_path), "Sdef file does not exist"

    # Compile and update target
    returned_value = legato.make_sys(
        source_file_path, source_file_path, should_fail=True
    )

    err_msg = "error: Internal error: Multiple install scripts not allowed."
    failed_msg = "Mksys didn't returned the expected sentence"
    assert returned_value.find(err_msg) != -1, failed_msg


def L_MDEF_0026(legato):
    """Invalid path in scripts section.

    This script will
        1. Create an update package (load: auto)
        2. Try to compile a module with error in pathing

    Args:
        legato: fixture to call useful functions regarding legato
    """
    # Verify existence of environment variables and files needed.
    # Prepare compilation
    test_name = "L_MDEF_0026"

    # Sdef file
    sdef_file = test_name + ".sdef"
    source_file_path = os.path.join(TEST_RESOURCES, sdef_file)
    assert os.path.exists(source_file_path), "Sdef file does not exist"

    # Compile and update target
    returned_value = legato.make_sys(
        source_file_path, source_file_path, should_fail=True
    )

    err_msg = "error: Script file '/WrongPath/install.sh' does not exist."
    failed_msg = "Mksys didn't returned the expected sentence"
    assert returned_value.find(err_msg) != -1, failed_msg


def L_MDEF_0029(legato, logread):
    """Verify that mdef can be use to include multiple prebuilt kernel module.

    This script will
        1. Create an update package (load: auto)
        2. Verify loading of the module
        3. Unload the module
        4. Load the module
        5. Compile the default package and update the target with it

    Args:
        legato: fixture to call useful functions regarding legato
        logread: fixture to check log on the target
    """
    # Verify existence of environment variables and files needed.
    # Prepare compilation
    test_name = "L_MDEF_0029"
    test_passed = True

    # Warning: Has to be in the expected loading order
    list_modules = ["L_MDEF_prebuilt_0", "L_MDEF_prebuilt_1"]

    # Compile and update target
    install_system(legato, test_name)

    # Verify mod has been loaded
    swilog.step("Step 2: Verify mod has been loaded...")
    for module in list_modules:
        if not check_presence(legato, module):
            test_passed = False
            swilog.error(
                "Step 2: Kernel module %s has not been properly loaded" % module
            )

    # Verify loading order
    (result, message) = check_loading_order(logread, ASCENDING_ORDER, list_modules)
    if not result:
        test_passed = False
        swilog.error(
            "Step 2: Kernel module aren't loaded in "
            "the expected order. Observed: %s" % message
        )

    # Stop legato
    swilog.step("Step 3: Stopping legato...")
    legato.legato_stop()

    # Verify mod has been loaded
    swilog.step("Step 4: Verify mod has been unloaded...")
    for module in list_modules:
        if check_presence(legato, module):
            test_passed = False
            swilog.error(
                "Step 4: Kernel module %s has not been properly unloaded" % module
            )

    # Verify unloading order
    (result, message) = check_unloading_order(logread, DESCENDING_ORDER, list_modules)
    if not result:
        test_passed = False
        swilog.error(
            "Step 4: Kernel module aren't unloaded in "
            "the expected order. Observed: %s" % message
        )

    # Start legato
    swilog.step("Step 5: Starting legato...")
    legato.legato_start()

    # Verify mod has been loaded
    swilog.step("Step 6: Verify mod has been loaded...")
    for module in list_modules:
        if not check_presence(legato, module):
            test_passed = False
            swilog.error(
                "Step 6: Kernel module %s has not been properly loaded" % module
            )

    # Verify loading order
    (result, message) = check_loading_order(logread, ASCENDING_ORDER, list_modules)
    if not result:
        test_passed = False
        swilog.error(
            "Step 6: Kernel module aren't loaded in "
            "the expected order. Observed: %s" % message
        )

    # End of script
    assert test_passed, display_errors()


def L_MDEF_0030(legato):
    """Check Mdef error case and system including prebuilt.

    and to be built kernel module.

    This script will
        1. Create an update package (load: auto)
        2. Try to compile a module with error in pathing

    Args:
        legato: fixture to call useful functions regarding legato
    """
    # Sdef file
    sdef_file = "L_MDEF_0030.sdef"
    source_file_path = os.path.join(TEST_RESOURCES, sdef_file)
    assert os.path.exists(source_file_path), "Sdef file does not exist"

    # Compile and update target
    returned_value = legato.make_sys(
        source_file_path, source_file_path, should_fail=True
    )

    err_msg = "Module file 'missingModule.ko' does not exist."
    failed_msg = "Mksys didn't returned the expected sentence"
    assert returned_value.find(err_msg) != -1, failed_msg


def L_MDEF_0031(legato):
    """Check Mdef error case and system including prebuilt.

    and to be built kernel module.

    This script will
        1. Create an update package (load: auto)
        2. Try to compile a module with error in pathing

    Args:
        legato: fixture to call useful functions regarding legato
    """
    # Sdef file
    sdef_file = "L_MDEF_0031.sdef"
    source_file_path = os.path.join(TEST_RESOURCES, sdef_file)
    assert os.path.exists(source_file_path), "Sdef file does not exist"

    # Compile and update target
    returned_value = legato.make_sys(
        source_file_path, source_file_path, should_fail=True
    )

    err_msg = "File 'missingSource.c' does not exist."
    failed_msg = "Mksys didn't returned the expected sentence"
    assert returned_value.find(err_msg) != -1, failed_msg


def L_MDEF_0032(legato):
    """Check Mdef error case and system including prebuilt.

    and to be built kernel module.

    This script will
        1. Create an update package (load: auto)
        2. Try to compile a module with error in pathing

    Args:
        legato: fixture to call useful functions regarding legato
    """
    # Sdef file
    sdef_file = "L_MDEF_0032.sdef"
    source_file_path = os.path.join(TEST_RESOURCES, sdef_file)
    assert os.path.exists(source_file_path), "Sdef file does not exist"

    # Compile and update target
    returned_value = legato.make_sys(
        source_file_path, source_file_path, should_fail=True
    )
    err_msg = (
        "error: Can't find definition file (.mdef) for module "
        "specification 'missingModule.mdef'."
    )
    failed_msg = "Mksys didn't returned the expected sentence"
    assert returned_value.find(err_msg) != -1, failed_msg


def L_MDEF_0033(legato):
    """Check Mdef error case and system including prebuilt.

    and to be built kernel module.

    This script will
        1. Create an update package (load: auto)
        2. Try to compile a module with error in pathing

    Args:
        legato: fixture to call useful functions regarding legato
    """
    # Sdef file
    sdef_file = "L_MDEF_0033.sdef"
    source_file_path = os.path.join(TEST_RESOURCES, sdef_file)
    assert os.path.exists(source_file_path), "Sdef file does not exist"

    # Compile and update target
    returned_value = legato.make_sys(
        source_file_path, source_file_path, should_fail=True
    )

    err_msg = "error: Module file 'missingPreBuiltModule.ko' does not exist."
    failed_msg = "Mksys didn't returned the expected sentence"
    assert returned_value.find(err_msg) != -1, failed_msg


def L_MDEF_0043(legato, logread):
    """Verify that mdef able to take more than two prebuilt using "{}" and ":".

    This script will
        1. Create an update package (load: auto)
        2. Verify loading of the module
        3. Stop Legato
        4. Start Legato
        5. Compile the default package and update the target with it

    Args:
        legato: fixture to call useful functions regarding legato
        logread: fixture to check log on the target
    """
    # Verify existence of environment variables and files needed.
    # Prepare compilation
    test_name = "L_MDEF_0043"
    test_passed = True

    # Warning: Has to be in the expected loading order
    list_modules = ["L_MDEF_prebuilt_0", "L_MDEF_prebuilt_1"]

    # Compile and update target
    install_system(legato, test_name)

    # Verify mod has been loaded
    swilog.step("Step 2: Verify mod has been loaded...")
    for module in list_modules:
        if not check_presence(legato, module):
            test_passed = False
            swilog.error(
                "Step 2: Kernel module %s has not been properly loaded" % module
            )

    # Verify loading order
    (result, message) = check_loading_order(logread, ASCENDING_ORDER, list_modules)
    if not result:
        test_passed = False
        swilog.error(
            "Step 2: Kernel module aren't loaded in "
            "the expected order. Observed: %s" % message
        )

    # Stop legato
    swilog.step("Step 3: Stopping legato...")
    legato.legato_stop()

    # Verify mod has been loaded
    swilog.step("Step 4: Verify mod has been unloaded...")
    for module in list_modules:
        if check_presence(legato, module):
            test_passed = False
            swilog.error(
                "Step 4: Kernel module %s has not been properly unloaded" % module
            )

    # Verify unloading order
    (result, message) = check_unloading_order(logread, DESCENDING_ORDER, list_modules)
    if not result:
        test_passed = False
        swilog.error(
            "Step 4: Kernel module aren't unloaded in "
            "the expected order. Observed: %s" % message
        )

    # Start legato
    swilog.step("Step 5: Starting legato...")
    legato.legato_start()

    # Verify mod has been loaded
    swilog.step("Step 6: Verify mod has been loaded...")
    for module in list_modules:
        if not check_presence(legato, module):
            test_passed = False
            swilog.error(
                "Step 6: Kernel module %s has not been properly loaded" % module
            )

    # Verify loading order
    (result, message) = check_loading_order(logread, ASCENDING_ORDER, list_modules)
    if not result:
        test_passed = False
        swilog.error(
            "Step 6: Kernel module aren't loaded in "
            "the expected order. Observed: %s" % message
        )

    # End of script
    assert test_passed, display_errors()


def L_MDEF_0046(legato, logread):
    """Verify relative path could be taken by specifying moduleSearch.

    This script will
        1. Create an update package (load: auto)
        2. Verify loading of the module
        3. Stop Legato
        4. Start Legato
        5. Compile the default package and update the target with it

    Args:
        legato: fixture to call useful functions regarding legato
        logread: fixture to check log on the target
    """
    # Verify existence of environment variables and files needed.
    # Prepare compilation
    test_name = "L_MDEF_0046"
    test_passed = True

    # Warning: Has to be in the expected loading order
    list_modules = ["L_MDEF_0046_0", "L_MDEF_0046_1"]

    # Compile and update target
    install_system(legato, test_name)

    # Verify mod has been loaded
    swilog.step("Step 2: Verify mod has been loaded...")
    for module in list_modules:
        if not check_presence(legato, module):
            test_passed = False
            swilog.error(
                "Step 2: Kernel module %s has not been properly loaded" % module
            )

    # Verify loading order
    (result, message) = check_loading_order(logread, ASCENDING_ORDER, list_modules)
    if not result:
        test_passed = False
        swilog.error(
            "Step 2: Kernel module aren't loaded in "
            "the expected order. Observed: %s" % message
        )

    # Stop legato
    swilog.step("Step 3: Stopping legato...")
    legato.legato_stop()

    # Verify mod has been loaded
    swilog.step("Step 4: Verify mod has been unloaded...")
    for module in list_modules:
        if check_presence(legato, module):
            test_passed = False
            swilog.error(
                "Step 4: Kernel module %s has not been properly unloaded" % module
            )

    # Verify unloading order
    (result, message) = check_unloading_order(logread, DESCENDING_ORDER, list_modules)
    if not result:
        test_passed = False
        swilog.error(
            "Step 4: Kernel module aren't unloaded in "
            "the expected order. Observed: %s" % message
        )

    # Start legato
    swilog.step("Step 5: Starting legato...")
    legato.legato_start()

    # Verify mod has been loaded
    swilog.step("Step 6: Verify mod has been loaded...")
    for module in list_modules:
        if not check_presence(legato, module):
            test_passed = False
            swilog.error(
                "Step 6: Kernel module %s has not been properly loaded" % module
            )

    # Verify loading order
    (result, message) = check_loading_order(logread, ASCENDING_ORDER, list_modules)
    if not result:
        test_passed = False
        swilog.error(
            "Step 6: Kernel module aren't loaded in "
            "the expected order. Observed: %s" % message
        )

    # End of script
    assert test_passed, display_errors()


def L_MDEF_0047(legato, logread):
    """Verify relative path could be taken by specifying moduleSearch.

    This script will
        1. Create an update package (load: auto)
        2. Verify loading of the module
        3. Stop Legato
        4. Start Legato
        5. Compile the default package and update the target with it

    Args:
        legato: fixture to call useful functions regarding legato
        logread: fixture to check log on the target
    """
    # Verify existence of environment variables and files needed.
    # Prepare compilation
    test_name = "L_MDEF_0047"
    test_passed = True

    # Warning: Has to be in the expected loading order
    list_modules = ["L_MDEF_0047_1", "L_MDEF_0047_0"]

    # Compile and update target
    install_system(legato, test_name)

    # Verify mod has been loaded
    swilog.step("Step 2: Verify mod has been loaded...")
    for module in list_modules:
        if not check_presence(legato, module):
            test_passed = False
            swilog.error(
                "Step 2: Kernel module %s has not been properly loaded" % module
            )

    # Verify loading order
    (result, message) = check_loading_order(logread, ASCENDING_ORDER, list_modules)
    if not result:
        test_passed = False
        swilog.error(
            "Step 2: Kernel module aren't loaded in "
            "the expected order. Observed: %s" % message
        )

    # Stop legato
    swilog.step("Step 3: Stopping legato...")
    legato.legato_stop()

    # Verify mod has been loaded
    swilog.step("Step 4: Verify mod has been unloaded...")
    for module in list_modules:
        if check_presence(legato, module):
            test_passed = False
            swilog.error(
                "Step 4: Kernel module %s has not been properly unloaded" % module
            )

    # Verify unloading order
    (result, message) = check_unloading_order(logread, DESCENDING_ORDER, list_modules)
    if not result:
        test_passed = False
        swilog.error(
            "Step 4: Kernel module aren't unloaded in "
            "the expected order.\nObserved: %s" % message
        )

    # Start legato
    swilog.step("Step 5: Starting legato...")
    legato.legato_start()

    # Verify mod has been loaded
    swilog.step("Step 6: Verify mod has been loaded...")
    for module in list_modules:
        if not check_presence(legato, module):
            test_passed = False
            swilog.error(
                "Step 6: Kernel module %s has not been properly loaded" % module
            )

    # Verify loading order
    (result, message) = check_loading_order(logread, ASCENDING_ORDER, list_modules)
    if not result:
        test_passed = False
        swilog.error(
            "Step 6: Kernel module aren't loaded in "
            "the expected order. Observed: %s" % message
        )

    # End of script
    assert test_passed, display_errors()


def L_MDEF_0048(legato):
    """Verify mksys should be able to handle non existence path and file.

    This script will
        1. Create an update package (load: auto)
        2. Try to compile a module with error in pathing

    Args:
        legato: fixture to call useful functions regarding legato
    """
    # Sdef file management
    sdef_file = "L_MDEF_0048.sdef"
    source_file_path = os.path.join(TEST_RESOURCES, sdef_file)
    assert os.path.exists(source_file_path), "Sdef file does not exist"

    # Compile and update target
    returned_value = legato.make_sys(
        source_file_path, source_file_path, should_fail=True
    )
    err_msg = (
        "error: Can't find definition file (.mdef) for "
        "module specification 'nonExisting.mdef'."
    )
    failed_msg = "Mksys didn't returned the expected sentence"
    assert returned_value.find(err_msg) != -1, failed_msg


def L_MDEF_0049(legato):
    """Verify mksys should be able to handle non existence path and file.

    This script will
        1. Create an update package (load: auto)
        2. Try to compile a module with error in pathing

    Args:
        legato: fixture to call useful functions regarding legato
    """
    # Verify existence of environment variables and files needed.
    # Prepare compilation
    sdef_file = "L_MDEF_0049.sdef"
    source_file_path = os.path.join(TEST_RESOURCES, sdef_file)
    assert os.path.exists(source_file_path), "Sdef file does not exist"

    # Compile and update target
    returned_value = legato.make_sys(
        source_file_path, source_file_path, should_fail=True
    )

    err_msg = (
        "error: Can't find definition file (.mdef) for "
        "module specification 'nonExisting.mdef'."
    )
    failed_msg = "Mksys didn't returned the expected sentence"
    assert returned_value.find(err_msg) != -1, failed_msg


def L_MDEF_0050(legato):
    """Verify mksys should be able to handle non existence .ko.

    under preBuilt section.

    This script will
        1. Create an update package (load: auto)
        2. Try to compile a module with error in pathing

    Args:
        legato: fixture to call useful functions regarding legato
    """
    # Sdef file management
    sdef_file = "L_MDEF_0050.sdef"
    source_file_path = os.path.join(TEST_RESOURCES, sdef_file)
    assert os.path.exists(source_file_path), "Sdef file does not exist"

    # Compile and update target
    returned_value = legato.make_sys(
        source_file_path, source_file_path, should_fail=True
    )

    err_msg = "error: Module file 'missingPreBuilt.ko' does not exist."
    failed_msg = "Mksys didn't returned the expected sentence"
    assert returned_value.find(err_msg) != -1, failed_msg


def L_MDEF_0051(legato):
    """Invalid path in  bundles section.

    This script will
        1. Create an update package (load: auto)
        2. Try to compile a module with error in pathing

    Args:
        legato: fixture to call useful functions regarding legato
    """
    # Sdef file management
    sdef_file = "L_MDEF_0051.sdef"
    source_file_path = os.path.join(TEST_RESOURCES, sdef_file)
    assert os.path.exists(source_file_path), "Sdef file does not exist"

    # Compile and update target
    returned_value = legato.make_sys(
        source_file_path, source_file_path, should_fail=True
    )

    err_msg = "error: File not found: '/ErrorInPath/text.txt'."
    failed_msg = "Mksys didn't returned the expected sentence"
    assert returned_value.find(err_msg) != -1, failed_msg


def L_MDEF_0052(legato):
    """Test to load more than one kernelModule with scripts.

    This script will
        1. Create an update package with multiple prebuilt packages in it
        (load: auto)
        2. Verify loading of the module

    Args:
        legato: fixture to call useful functions regarding legato
    """
    # Verify existence of environment variables and files needed.
    # Prepare compilation
    test_name = "L_MDEF_0052"
    test_passed = True

    # Warning: Has to be in the expected loading order
    list_modules = ["L_MDEF_prebuilt_0", "L_MDEF_prebuilt_1"]

    # Compile and update target
    install_system(legato, test_name)

    # Verify mod has been loaded
    swilog.step("Step 2: Verify mod has been loaded...")
    for module in list_modules:
        if not check_presence(legato, module):
            test_passed = False
            swilog.error(
                "Step 2: Kernel module %s has not been properly loaded" % module
            )

    # End of script
    assert test_passed, display_errors()


def L_MDEF_0053(legato):
    """Test to load more than one kernelModule with scripts.

    This script will
        1. Create an update package with multiple prebuilt packages in it
        (load: auto)
        2. Verify loading of the module

    Args:
        legato: fixture to call useful functions regarding legato
    """
    # Verify existence of environment variables and files needed.
    # Prepare compilation
    test_name = "L_MDEF_0053"
    test_passed = True

    # Warning: Has to be in the expected loading order
    list_modules = ["L_MDEF_prebuilt_0", "L_MDEF_prebuilt_1"]

    # Compile and update target
    install_system(legato, test_name)

    # Verify mod has been loaded
    swilog.step("Step 2: Verify mods have been loaded...")
    for module in list_modules:
        if not check_presence(legato, module):
            test_passed = False
            swilog.error(
                "Step 2: Kernel module %s has not been properly loaded" % module
            )

    # End of script
    assert test_passed, display_errors()


def L_MDEF_0054(target, legato):
    """Load kernel module manual with script.

    This script will
        1. Create an update package (load: manual)
        2. Verify loading of the module
        3. Check insertion and removing of modules mechanism

    Args:
        target: fixture to communicate with the target
        legato: fixture to call useful functions regarding legato
    """
    # Verify existence of environment variables and files needed.
    # Prepare compilation
    test_name = "L_MDEF_0054"
    test_passed = True

    # Warning: Has to be in the expected loading order
    list_modules = ["L_MDEF_prebuilt_0", "L_MDEF_prebuilt_1"]

    # Compile and update target
    install_system(legato, test_name)

    # Verify mod has been loaded
    swilog.step("Step 2: Verify auto loading mod has been loaded...")
    if not check_presence(legato, "L_MDEF_prebuilt_0"):
        test_passed = False
        swilog.error(
            "Step 2: Kernel module L_MDEF_prebuilt_0 has not been properly loaded"
        )

    # Insert manual mod
    swilog.step("Step 3: Insert manual mod...")
    cmd = "/sbin/insmod /legato/systems/current/modules/L_MDEF_prebuilt_1.ko"
    exit_code, rsp = target.run(cmd, withexitstatus=True)
    swilog.debug(rsp)
    if exit_code != 0:
        test_passed = False
        swilog.error("Insertion of manual loading mod has failed")

    # Verify mod has been loaded
    swilog.step("Step 4: Verify mods have been loaded...")
    for module in list_modules:
        if not check_presence(legato, module):
            test_passed = False
            swilog.error(
                "Step 4: Kernel module %s has not been properly loaded" % module
            )

    # End of script
    assert test_passed, display_errors()


def L_MDEF_0055(legato):
    """Specify install and remove in your script section.

    This script will
        1. Create an update package (load: auto)
        2. Try to compile a module with error in mdef

    Args:
        legato: fixture to call useful functions regarding legato
    """
    # Sdef file management
    sdef_file = "L_MDEF_0055.sdef"
    source_file_path = os.path.join(TEST_RESOURCES, sdef_file)
    assert os.path.exists(source_file_path), "Sdef file does not exist"

    # Compile and update target
    returned_value = legato.make_sys(
        source_file_path, source_file_path, should_fail=True
    )
    failed_msg = "Mksys didn't returned the expected sentence"
    assert returned_value.find("error: Unexpected character") != -1, failed_msg


def L_MDEF_0056(legato):
    """Specify install and remove in your script section.

    This script will

    1. Create an update package (load: auto)
    2. Verify loading of the module
    3. Compile the default package and update the target with it

    Args:
        legato: fixture to call useful functions regarding legato
    """
    # Verify existence of environment variables and files needed.
    # Prepare compilation
    test_name = "L_MDEF_0056"
    test_passed = True

    # Warning: Has to be in the expected loading order
    list_modules = [test_name]

    # Compile and update target
    install_system(legato, test_name)

    # Verify mod has been loaded
    swilog.step("Step 2: Verify mod has been loaded...")
    for module in list_modules:
        if not check_presence(legato, module):
            test_passed = False
            swilog.error(
                "Step 2: Kernel module %s has not been properly loaded" % module
            )

    # End of script
    assert test_passed, display_errors()


def L_MDEF_0057(legato):
    """Specify install and remove in your script section.

    This script will

    1. Create an update package (load: auto)
    2. Verify loading of the module
    3. Compile the default package and update the target with it

    Args:
        legato: fixture to call useful functions regarding legato
    """
    # Verify existence of environment variables and files needed.
    # Prepare compilation
    test_name = "L_MDEF_0057"
    test_passed = True

    # Warning: Has to be in the expected loading order
    list_modules = ["L_MDEF_prebuilt_0"]

    # Compile and update target
    install_system(legato, test_name)

    # Verify mod has been loaded
    swilog.step("Step 2: Verify mod has been loaded...")
    for module in list_modules:
        if not check_presence(legato, module):
            test_passed = False
            swilog.error(
                "Step 2: Kernel module %s has not been properly loaded" % module
            )

    # End of script
    assert test_passed, display_errors()


def L_MDEF_0058(legato):
    """Relative path in script section of mdef.

    This script will

        1. Create an update package with relative path (load: auto)
        2. Verify loading of the module
        3. Compile the default package and update the target with it

    Args:
        legato: fixture to call useful functions regarding legato
    """
    # Verify existence of environment variables and files needed.
    # Prepare compilation
    test_name = "L_MDEF_0058"
    test_passed = True

    # Warning: Has to be in the expected loading order
    list_modules = ["L_MDEF_prebuilt_0"]

    # Compile and update target
    swilog.step("Step 1: Compiling using relative path...")
    swilog.warning(
        "WARNING: Works only if you run the test script from qa/letp/ directory"
    )
    install_system(legato, test_name)

    # Verify mod has been loaded
    swilog.step("Step 2: Verify mod has been loaded...")
    for module in list_modules:
        if not check_presence(legato, module):
            test_passed = False
            swilog.error(
                "Step 2: Kernel module %s has not been properly loaded" % module
            )

    # End of script
    assert test_passed, display_errors()


def L_MDEF_0059(legato):
    """Put more than one scripts path in install.

    or remove section script section.

    This script will
        1. Create an update package (load: auto)
        2. Try to compile a module with error in mdef

    Args:
        legato: fixture to call useful functions regarding legato
    """
    # Sdef file management
    sdef_file = "L_MDEF_0059.sdef"
    source_file_path = os.path.join(TEST_RESOURCES, sdef_file)
    assert os.path.exists(source_file_path), "Sdef file does not exist"

    # Compile and update target
    returned_value = legato.make_sys(
        source_file_path, source_file_path, should_fail=True
    )

    err_msg = "error: Internal error: Multiple install scripts not allowed."
    failed_msg = "Mksys didn't returned the expected sentence"
    assert returned_value.find(err_msg) != -1, failed_msg


def L_MDEF_0060(legato):
    """Put more than one scripts section in mdef file.

    This script will
        1. Create an update package (load: auto)
        2. Try to compile a module with error in mdef

    Args:
        legato: fixture to call useful functions regarding legato
    """
    # Verify existence of environment variables and files needed.
    # Prepare compilation
    sdef_file = "L_MDEF_0060.sdef"
    source_file_path = os.path.join(TEST_RESOURCES, sdef_file)
    assert os.path.exists(source_file_path), "Sdef file does not exist"

    # Compile and update target
    returned_value = legato.make_sys(
        source_file_path, source_file_path, should_fail=True
    )

    err_msg = "error: Internal error: Multiple install scripts not allowed."
    failed_msg = "Mksys didn't returned the expected sentence"
    assert returned_value.find(err_msg) != -1, failed_msg


def L_MDEF_0061(legato):
    """Invalid path in scripts section.

    This script will
        1. Create an update package (load: auto)
        2. Try to compile a module with error in pathing

    Args:
        legato: fixture to call useful functions regarding legato
    """
    # Verify existence of environment variables and files needed.
    # Prepare compilation
    sdef_file = "L_MDEF_0061.sdef"
    source_file_path = os.path.join(TEST_RESOURCES, sdef_file)
    assert os.path.exists(source_file_path), "Sdef file does not exist"

    # Compile and update target
    returned_value = legato.make_sys(
        source_file_path, source_file_path, should_fail=True
    )

    err_msg = "error: Script file '/WrongPath/install.sh' does not exist."
    failed_msg = "Mksys didn't returned the expected sentence"
    assert returned_value.find(err_msg) != -1, failed_msg


def L_MDEF_0062(legato):
    """Verify that files, bin and scripts directory is bundled.

    under system module directory.

    This script will

        1. Create an update package (load: auto)
        2. Verify loading of the module
        3. Verify presence of the module file
        4. Verify presence of the bundled files

    Args:
        legato: fixture to call useful functions regarding legato
    """
    # Verify existence of environment variables and files needed.
    # Prepare compilation
    test_name = "L_MDEF_0062"
    test_passed = True

    # Warning: Has to be in the expected loading order
    list_modules = ["L_MDEF_prebuilt_0"]

    # Compile and update target
    install_system(legato, test_name)

    # Verify mod has been loaded
    swilog.step("Step 2: Verify mod has been loaded...")
    for module in list_modules:
        if not check_presence(legato, module):
            test_passed = False
            swilog.error(
                "Step 2: Kernel module %s has not been properly loaded" % module
            )

    swilog.step("Step 3: Verify module file is present...")
    folder_path = "/legato/systems/current/modules"
    if not check_file_presence(legato, folder_path, "L_MDEF_prebuilt_0"):
        test_passed = False
        swilog.error("Step 3: Module file isn't present")

    swilog.step("Step 4: Verify bundled files are present...")
    files = ["text.txt", "dir", "scripts"]
    folder_path = "/legato/systems/current/modules/files/L_MDEF_prebuilt_0"
    for file_name in files:
        if not check_file_presence(legato, folder_path, file_name):
            test_passed = False
            swilog.error("Step 3: File or directory %s isn't present" % file_name)

    files = ["install.sh", "remove.sh"]
    folder_path = "/legato/systems/current/modules/files/L_MDEF_prebuilt_0/scripts"
    for file_name in files:
        if not check_file_presence(legato, folder_path, file_name):
            test_passed = False
            swilog.error(
                "Step 3: File or directory scripts/%s isn't present" % file_name
            )

    files = ["dir.txt"]
    folder_path = "/legato/systems/current/modules/files/L_MDEF_prebuilt_0/dir"
    for file_name in files:
        if not check_file_presence(legato, folder_path, file_name):
            test_passed = False
            swilog.error("Step 3: File dir/%s isn't present" % file_name)

    # End of script
    assert test_passed, display_errors()
