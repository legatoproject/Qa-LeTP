"""kmod tools test.

Set of functions to test the Legato kmod tools
"""
import os
import time
import pytest
import pexpect
from pytest_letp.lib import swilog

__copyright__ = "Copyright (C) Sierra Wireless Inc."
# ======================================================================================
# Constants and Globals
# ======================================================================================
TEST_RESOURCES = os.path.join(os.path.abspath(os.path.dirname(__file__)), "resources")
RESULT_OK = 0
RESULT_FAULT = 1
RESULT_DUPLICATE = 2
RESULT_BUSY = 2
test_passed = True

is_first_execution = True


# ======================================================================================
# Functions
# ======================================================================================
def check_loading(target, module_name, expected_output_index):
    r"""Check the result of kmod load.

    :param target: fixture to communicate with the target
    :param module_name: name of kernel module (\*.ko)
    :param expected_output_index:
               | RESULT_OK         = 0 => Loading works fine
               | RESULT_FAULT      = 1 => Loading didn't work due to error
               | RESULT_DUPLICATE  = 2 => Loading didn't work due to duplicate

    :returns test_passed:
               True: loading result is as expected.
               False: loading result is not as expected.
    :returns found_expected: actual output index.
    """
    load_return_message = [
        ("Load of module %s.ko has been successful." % module_name),
        "LE_FAULT",
        "LE_DUPLICATE",
    ]

    try:
        target.sendline("kmod load %s.ko" % module_name)
        found_expected = target.expect(load_return_message)
        if found_expected == RESULT_OK:
            test_passed = found_expected == expected_output_index
        elif found_expected == RESULT_FAULT:
            test_passed = found_expected == expected_output_index
        elif found_expected == RESULT_DUPLICATE:
            test_passed = found_expected == expected_output_index
        else:
            test_passed = False
            assert False, "Error in test script, bad parameter in function"
    except pexpect.TIMEOUT:
        test_passed = False
        found_expected = -1
        print("None of the expected output has been found in log")

    return (test_passed, found_expected)


def check_unloading(target, module_name, expected_output_index):
    r"""Check the result of kmod unload.

    :param target: fixture to communicate with the target
    :param module_name: name of kernel module (\*.ko)
    :param expected_output_index:
               | RESULT_OK         = 0 => Unloading works fine
               | RESULT_FAULT      = 1 => Unloading didn't work
               | RESULT_BUSY       = 2 => Current module is busy

    :returns test_passed:
                True: unloading result is as expected.
                False: unloading result is not as expected
    :returns found_expected: actual output index
    """
    test_passed = ""
    found_expected = ""
    unload_return_message = [
        "Unload of module %s.ko has been successful." % module_name,
        "LE_FAULT",
        "LE_BUSY",
    ]

    try:
        target.sendline("kmod unload %s.ko" % module_name)
        found_expected = target.expect(unload_return_message)
        if found_expected == RESULT_OK:
            test_passed = found_expected == expected_output_index
        elif found_expected == RESULT_FAULT:
            test_passed = found_expected == expected_output_index
        elif found_expected == RESULT_BUSY:
            test_passed = found_expected == expected_output_index
        else:
            assert False, "Error in test script, bad parameter in function"
    except pexpect.TIMEOUT:
        print("None of the expected output has been found in log")

    return (test_passed, found_expected)


def check_presence(legato, module_name):
    r"""Check whether a module is loaded or not.

    :param target: fixture to communicate with the target
    :param legato: fixture to call useful functions regarding legato
    :param module_name: name of kernel module (\*.ko)

    :returns True: a module is loaded
    :returns False: a module is not loaded
    """
    exit_code = legato.ssh_to_target('/sbin/lsmod | grep -F "%s"' % module_name)
    return bool(exit_code == 0)


def install_system(target, legato, dir_path, test_name):
    """Compile the provided sdef and update the target with it.

    :param target: fixture to communicate with the target
    :param legato: fixture to call useful functions regarding legato
    :param dir_path: a temporary directory unique to the test invocation
    :param test_name: test case name
    """
    swilog.debug(dir_path)
    # Sdef file
    sdef_file = test_name + ".sdef"
    source_file_path = os.path.join(TEST_RESOURCES, sdef_file)
    assert os.path.exists(source_file_path), "sdef file does not exist"

    # Compile and update target
    swilog.info("Compilation in progress. Please wait...")
    make_install_sys_in_temporary_directory(
        legato, dir_path, test_name, source_file_path
    )

    # Waiting for legato to be ready
    time.sleep(5)
    wait_for_cm_info(target)
    time.sleep(5)


def wait_for_cm_info(target):
    """Check target is available.

    :param target: fixture to communicate with the target
    """
    swilog.info("Checking legato is operational...")
    timer = 30
    while timer >= 0:
        try:
            target.sendline("/legato/systems/current/bin/cm info")
            target.expect("Device:", 3)
            timer = -1
        except pexpect.TIMEOUT:
            swilog.debug("Unable to install system for now")
            timer -= 1
        except pexpect.EOF:
            swilog.debug("cm info returned unexpected value")
            timer -= 1
        time.sleep(1)


def wait_for_app_presence(legato, app_name):
    """Check application is listed.

    :param legato: fixture to call useful functions regarding legato
    :param app_name: name of an application want to check
    """
    swilog.info("Checking application is listed...")
    timer = 30
    while not legato.is_app_exist(app_name):
        timer = timer - 1
        if timer < 0:
            swilog.debug("Unable to found application in the list")
            break
        time.sleep(1)


def wait_for_app_running(legato, app_name):
    """Check application is running.

    :param legato: fixture to call useful functions regarding legato
    :param app_name: application name needs to be checked
    """
    swilog.info("Checking application is running...")
    timer = 30
    while not legato.is_app_running(app_name):
        timer = timer - 1
        if timer < 0:
            swilog.debug("The application is not running")
            break
        time.sleep(1)


def display_errors():
    """Display errors.

    :param output: errors
    """
    output = "\n"
    for err in swilog.get_error_list():
        output += err + "\n"
    return output


def make_sys_in_temporary_directory(
    legato, temp_dir_path, sys_name, definition_file_path
):
    """Compile the provided sdef and update the target.

    :param legato: fixture to call useful functions regarding legato
    :param temp_dir_path: a temporary directory unique to the test invocation
    :param sys_name: name of the system definition file
    :param definition_file_path: path of the  system definition file (.sdef)
    """
    old_path = os.getcwd()
    os.chdir(temp_dir_path)
    legato.make_sys(
        sys_name,
        sys_path=definition_file_path,
        option="--output-dir=%s" % temp_dir_path,
        quiet=True,
    )
    os.chdir(old_path)


def make_install_sys_in_temporary_directory(
    legato, temp_dir_path, sys_name, definition_file_path
):
    """Compile the provided sdef and update the target.

    :param legato: fixture to call useful functions regarding legato
    :param temp_dir_path: a temporary directory unique to the test invocation
    :param sys_name: name of the system definition file
    :param definition_file_path: path of the  system definition file (.sdef)
    """
    old_path = os.getcwd()
    os.chdir(temp_dir_path)
    legato.make_sys(
        sys_name,
        sys_path=definition_file_path,
        option="--output-dir=%s" % temp_dir_path,
        quiet=True,
    )
    legato.install_sys(sys_name, sys_path=temp_dir_path, quiet=True)
    os.chdir(old_path)


# =====================================================================================
# Local fixtures
# =====================================================================================
@pytest.fixture
def check_environment(target, legato, create_temp_workspace):
    """Check environment and clean up after each test.

    :param legato: fixture to call useful functions regarding legato
    :param target: fixture to communicate with the target
    :param create_temp_workspace: fixture to create a temporary folder
                            at the emplacement of the module file
    """
    # Clear target log
    swilog.info("Clearing target log...")
    legato.clear_target_log()

    # Launch test script
    yield

    # Waiting for legato to be ready
    wait_for_cm_info(target)

    # Clean target by uploading default legato
    swilog.info("Updating target with default legato...")
    legato.install_sys("default", sys_path=create_temp_workspace)

    # Waiting for legato to be ready
    wait_for_cm_info(target)

    # Rebooting target
    swilog.info("Rebooting target...")
    target.reboot(60)


@pytest.fixture
def environment_setting(target, legato, create_temp_workspace):
    """Check every environment variable are defined. Define them otherwise.

    :param legato: fixture to call useful functions regarding legato
    :param target: fixture to communicate with the target
    :param create_temp_workspace: fixture to create a temporary folder
                            at the emplacement of the module file
    """
    global is_first_execution

    if is_first_execution:
        is_first_execution = False

        # Check environment variables
        swilog.info("Check target specific environment variables...")
        kernel_variable = (target.target_name).upper() + "_KERNELROOT"
        sys_root_variable = (target.target_name).upper() + "_SYSROOT"
        assert (
            os.environ.get(sys_root_variable) is not None
        ), "\
        SYSROOT variable does not exist.\
        Please configure your legato environment"
        if os.environ.get(kernel_variable) is None:
            os.environ[kernel_variable] = os.path.join(
                os.environ.get(sys_root_variable), "usr/src/kernel"
            )

        # Build default legato and save package
        swilog.info("Compiling default legato...")
        make_sys_in_temporary_directory(
            legato, create_temp_workspace, "default", os.environ.get("LEGATO_ROOT")
        )

        # Clean target by uploading default legato
        swilog.info("Updating target with default legato...")
        legato.install_sys("default", sys_path=create_temp_workspace, quiet=True)

    # Launch test script
    yield


@pytest.fixture(scope="module")
def create_temp_workspace(tmpdir_factory):
    """Create a temporary folder at the emplacement of the module file.

    :param tmpdir_factory: a temporary directory unique to the test invocation
    """
    # Create temporary workspace. Convert to string
    temp_folder_path = str(tmpdir_factory.mktemp("output"))

    # Launch test scripts of the class
    yield temp_folder_path


# =====================================================================================
# Test functions
# =====================================================================================
@pytest.mark.usefixtures("check_environment", "environment_setting")
def L_Tools_Kmod_0004(target, legato, create_temp_workspace):
    """Verify that kmod command able to load and unload the kernel module.

        1. Create an update package (load: auto)
        2. Verify loading of the module
        3. Unload the module
        4. Load the module
        5. Compile the default package and update the target with it

    :param target: fixture to communicate with the target
    :param legato: fixture to call useful functions regarding legato
    :param create_temp_workspace: fixture to create a temporary folder
    """
    # Verify existence of environment variables and files needed.
    # Prepare compilation
    test_name = "L_Tools_Kmod_0004"
    test_passed = True

    # Compile and update target
    swilog.step("Step 1: Compiling...")
    install_system(target, legato, create_temp_workspace, test_name)

    swilog.step("Step 2: Verify mod has been loaded...")
    if not check_presence(legato, test_name):
        test_passed = False
        swilog.error("Step 2: Kernel module has not been properly loaded")

    swilog.step("Step 3: Unloading...")
    (returned_value, returned_index) = check_unloading(target, test_name, RESULT_OK)
    if not returned_value:
        test_passed = False
        swilog.error("Step 3: Kernel module has not been properly unloaded")

    swilog.step("Step 5: Loading...")
    (returned_value, returned_index) = check_loading(target, test_name, RESULT_OK)
    if not returned_value:
        test_passed = False
        swilog.error("Step 5: Kernel module has not been properly loaded")
    swilog.debug(returned_index)
    # End of script: Build the default package to reinitialise the target
    # And clean the LEGATO_ROOT directory
    assert test_passed, display_errors()


@pytest.mark.usefixtures("check_environment", "environment_setting")
def L_Tools_Kmod_0005(target, legato, create_temp_workspace):
    """Verify that kmod command able to load.

    And unload the kernel module with manual load
        1. Create an update package (load: manual)
        2. Verify loading of the module has not been performed
        3. Load the module
        4. Unload the module
        5. Compile the default package and update the target with it

    :param target: fixture to communicate with the target
    :param legato: fixture to call useful functions regarding legato
    :param create_temp_workspace: fixture to create a temporary folder
    """
    # Verify existence of environment variables and files needed.
    # Prepare compilation
    test_name = "L_Tools_Kmod_0005"
    test_passed = True
    # Compile and update target
    swilog.step("Step 1: Compiling...")
    install_system(target, legato, create_temp_workspace, test_name)

    swilog.step("Step 2: Verify mod has not been loaded...")
    if check_presence(legato, test_name):
        test_passed = False
        swilog.error("Step 2: Kernel module has been unexpectedly loaded")

    swilog.step("Step 3: Loading...")
    (returned_value, returned_index) = check_loading(target, test_name, RESULT_OK)
    if not returned_value:
        test_passed = False
        swilog.error("Step 3: Kernel module has not been properly loaded")

    swilog.step("Step 5: Unloading...")
    (returned_value, returned_index) = check_unloading(target, test_name, RESULT_OK)
    if not returned_value:
        test_passed = False
        swilog.error("Step 5: Kernel module has not been properly unloaded")
    swilog.debug(returned_index)
    # End of script: Build the default package to reinitialise the target
    # And clean the LEGATO_ROOT directory
    assert test_passed, display_errors()


@pytest.mark.usefixtures("check_environment", "environment_setting")
def L_Tools_Kmod_0006(target, legato, create_temp_workspace):
    """Verify kmod cmd should not be able to load if it already loaded.

        1. Create an update package (Same modules as L_Tools_Kmod_0004)
        and update the target with it
        2. Verify loading of the module
        3. Try to load the module
        4. It must fail
        5. Compile the default package and update the target with it

    :param target: fixture to communicate with the target
    :param legato: fixture to call useful functions regarding legato
    :param create_temp_workspace: fixture to create a temporary folder
    """
    # Initialisation:
    # Verify existence of environment variables and files needed.
    # Prepare compilation
    test_name = "L_Tools_Kmod_0004"
    test_passed = True
    # Compile and update target
    swilog.step("Step 1: Compiling...")
    install_system(target, legato, create_temp_workspace, test_name)

    swilog.step("Step 2: Verify mod has been loaded...")
    if not check_presence(legato, test_name):
        test_passed = False
        swilog.error("Step 2: Kernel module has not been properly loaded")

    swilog.step("Step 5: Loading...")
    (returned_value, returned_index) = check_loading(
        target, test_name, RESULT_DUPLICATE
    )
    if not returned_value:
        test_passed = False
        swilog.error("Step 5: Loading should have been forbidden.")
    swilog.debug(returned_index)
    # End of script: Build the default package to reinitialise the target
    # And clean the LEGATO_ROOT directory
    assert test_passed, display_errors()


@pytest.mark.usefixtures("check_environment", "environment_setting")
def L_Tools_Kmod_0007(target, legato, create_temp_workspace):
    """Verify kmod cmd should not be able to unload kernel module.

        1. Create an update package with a dependence to
        an other module (load:auto) and update the target with it
        2. Verify loading of both modules
        3. Try to unload the required module: it must fail
        4. Try to unload the primary module: it must fail
        5. Compile the default package and update the target with it

    :param target: fixture to communicate with the target
    :param legato: fixture to call useful functions regarding legato
    :param create_temp_workspace: fixture to create a temporary folder
    """
    # Initialisation:
    # Verify existence of environment variables and files needed.
    # Prepare compilation
    test_name = "L_Tools_Kmod_0007"
    test_passed = True
    # Compile and update target
    swilog.step("Step 1: Compiling...")
    install_system(target, legato, create_temp_workspace, test_name)

    swilog.step("Step 2: Verify mods have been loaded...")
    check_presence_0004 = check_presence(legato, "L_Tools_Kmod_0004")
    check_presence_0007 = check_presence(legato, test_name)
    if (not check_presence_0007) or (not check_presence_0004):
        test_passed = False
        swilog.error("Step 2: Kernel module have not been properly loaded")

    # Unloading required module
    swilog.step("Step 3: Unloading required module...")
    (returned_value, returned_index) = check_unloading(
        target, "L_Tools_Kmod_0004", RESULT_BUSY
    )
    if not returned_value:
        test_passed = False
        swilog.error("Step 3: Unloading should have been forbidden.")

    # Unloading primary module
    swilog.step("Step 5: Unloading primary module...")
    (returned_value, returned_index) = check_unloading(target, test_name, RESULT_OK)
    if not returned_value:
        test_passed = False
        swilog.error("Step 5: Unloading should have been forbidden.")
    swilog.debug(returned_index)
    # End of script: Build the default package to reinitialise the target
    # And clean the LEGATO_ROOT directory
    assert test_passed, display_errors()


@pytest.mark.usefixtures("check_environment", "environment_setting")
def L_Tools_Kmod_0008(target, legato, create_temp_workspace):
    """Verify that kmod command is not able to.

        1. Create an update package with a dependence to
        an application (load:auto)and update the target with it
        2  Verify module is loaded and application is running
        3. Unload module
        4. Load back the module
        5. Compile the default package and update the target with it

    :param target: fixture to communicate with the target
    :param legato: fixture to call useful functions regarding legato
    :param create_temp_workspace: fixture to create a temporary folder
    """
    # Initialisation:
    # Verify existence of environment variables and files needed.
    # Prepare compilation
    test_name = "L_Tools_Kmod_0008"
    test_passed = True
    # Compile and update target
    swilog.step("Step 1: Compiling...")
    install_system(target, legato, create_temp_workspace, test_name)

    swilog.step("Step 2: Verify mod has been loaded and app is running...")
    if not check_presence(legato, test_name):
        test_passed = False
        swilog.error("Step 2: Kernel module has not been properly loaded")
    if not legato.is_app_running("LoopingHelloWorld"):
        test_passed = False
        swilog.error("Step 2: App is not running")

    swilog.step("Step 3: Unloading...")
    (returned_value, returned_index) = check_unloading(target, test_name, RESULT_OK)
    if not returned_value:
        test_passed = False
        swilog.error("Step 3: Kernel module has not been properly unloaded")

    swilog.step("Step 5: Loading...")
    (returned_value, returned_index) = check_loading(target, test_name, RESULT_OK)
    if not returned_value:
        test_passed = False
        swilog.error("Step 5: Kernel module has not been properly loaded")
    swilog.debug(returned_index)
    # End of script: Build the default package to reinitialise the target
    # And clean the LEGATO_ROOT directory
    assert test_passed, display_errors()


@pytest.mark.usefixtures("check_environment", "environment_setting")
def L_Tools_Kmod_0009(target, legato, create_temp_workspace):
    """Verify kmod cmd able to load/unload with manual start.

        1. Create an update package with a dependence to
        an application (load:manual) and update the target with it
        3. Verify module isn't loaded and application isn't running
        4. Load module
        5. Unload module
        6. Compile the default package and update the target with it

    :param target: fixture to communicate with the target
    :param legato: fixture to call useful functions regarding legato
    :param create_temp_workspace: fixture to create a temporary folder
    """
    # Initialization:
    # Verify existence of environment variables and files needed
    # Prepare compilation
    test_name = "L_Tools_Kmod_0009"
    test_passed = True
    # Compile and update target
    swilog.step("Step 1: Compiling...")
    install_system(target, legato, create_temp_workspace, test_name)

    swilog.step("Step 2: Verify mod has not been loaded and app is not running...")
    if check_presence(legato, test_name) or legato.is_app_running("LoopingHelloWorld"):
        test_passed = False
        swilog.error(
            "Step 2: Kernel module has been erroneously loaded or App is running"
        )

    swilog.step("Step 3: Loading...")
    (returned_value, returned_index) = check_loading(target, test_name, RESULT_OK)
    if not returned_value:
        test_passed = False
        swilog.error("Step 3: Kernel module has not been properly loaded")

    swilog.step("Step 5: Verify mod has been loaded...")
    if not check_presence(legato, test_name):
        test_passed = False
        swilog.error("Step 5: Kernel module has not been properly loaded")

    swilog.step("Step 6: Unloading...")
    (returned_value, returned_index) = check_unloading(target, test_name, RESULT_OK)
    if not returned_value:
        test_passed = False
        swilog.error("Step 6: Kernel module has not been properly unloaded")

    swilog.step("Step 8: Starting the application...")
    wait_for_app_presence(legato, "LoopingHelloWorld")
    legato.start("LoopingHelloWorld")
    wait_for_app_running(legato, "LoopingHelloWorld")

    swilog.step("Step 9: Verify mod has been loaded...")
    if not check_presence(legato, test_name):
        test_passed = False
        swilog.error("Step 9: Kernel module has not been properly loaded")

    swilog.step("Step 10: Unloading...")
    (returned_value, returned_index) = check_unloading(target, test_name, RESULT_BUSY)
    if not returned_value:
        test_passed = False
        swilog.error("Step 10: Unloading should have been forbidden.")

    swilog.step("Step 12: Stopping the application...")
    wait_for_app_running(legato, "LoopingHelloWorld")
    legato.stop("LoopingHelloWorld")

    swilog.step("Step 13: Verify mod has been unloaded...")
    if check_presence(legato, test_name):
        test_passed = False
        swilog.error("Step 13: Kernel module should have been unloaded")

    swilog.step("Step 14: Loading...")
    (returned_value, returned_index) = check_loading(target, test_name, RESULT_OK)
    if not returned_value:
        test_passed = False
        swilog.error("Step 14: Kernel module has not been properly loaded")
    swilog.debug(returned_index)
    # End of script: Build the default package to reinitialise the target
    # And clean the LEGATO_ROOT directory
    assert test_passed, display_errors()


@pytest.mark.usefixtures("check_environment", "environment_setting")
def L_Tools_Kmod_0010(target, legato, create_temp_workspace):
    """Verify kmod cmd able to load/unload after removing the app.

        1. Create an update package (Same as L_Tools_Kmod_0009)
        2. Update the target with it
        3. Verify module isn't loaded and application is running
        4. Start app
        5. Verify mod is loaded
        6. Remove app
        7. Verify mod is unloaded
        8. Load back the module
        9. Verify mod is loaded
        10. Compile the default package and update the target with it

    :param target: fixture to communicate with the target
    :param legato: fixture to call useful functions regarding legato
    :param create_temp_workspace: fixture to create a temporary folder
    """
    # Initialisation:
    # Verify existence of environment variables and files needed.
    # Prepare compilation
    test_name = "L_Tools_Kmod_0009"
    test_passed = True
    # Compile and update target
    swilog.step("Step 1: Compiling...")
    install_system(target, legato, create_temp_workspace, test_name)

    swilog.step("Step 2: Verify mod has not been loaded and app is not running...")
    if check_presence(legato, test_name):
        test_passed = False
        swilog.error("Step 2: Kernel module has been erroneously loaded")
    if legato.is_app_running("LoopingHelloWorld"):
        test_passed = False
        swilog.error("Step 2: App is running")

    print("\nStep 3: Start app...")
    target.sendline("/legato/systems/current/bin/app start LoopingHelloWorld")

    swilog.step("Step 4: Verify mod has been loaded and app is running...")
    if not check_presence(legato, test_name):
        test_passed = False
        swilog.error("Step 2: Kernel module has not been properly loaded")
    if not legato.is_app_running("LoopingHelloWorld"):
        test_passed = False
        swilog.error("Step 2: App is not running")

    swilog.step("Step 5: Removing the application...")
    wait_for_app_running(legato, "LoopingHelloWorld")
    legato.remove("LoopingHelloWorld")

    swilog.step("Step 6: Verify mod unloaded and app removed...")
    if check_presence(legato, test_name):
        test_passed = False
        swilog.error("Step 6: Kernel module has been erroneously loaded")
    if legato.is_app_exist("LoopingHelloWorld"):
        test_passed = False
        swilog.error("Step 6: App still exists")

    swilog.step("Step 7: Loading...")
    (returned_value, returned_index) = check_loading(target, test_name, RESULT_OK)
    if not returned_value:
        test_passed = False
        swilog.error("Step 3: Kernel module has not been properly loaded")
    time.sleep(5)  # Wait the module to be loaded

    swilog.step("Step 9: Verify mod has been loaded...")
    if not check_presence(legato, test_name):
        test_passed = False
        swilog.error("Step 9: Kernel module has not been properly loaded")
    swilog.debug(returned_index)
    # End of script: Build the default package to reinitialise the target
    # And clean the LEGATO_ROOT directory
    assert test_passed, display_errors()


@pytest.mark.usefixtures("check_environment", "environment_setting")
def L_Tools_Kmod_0011(target, legato, create_temp_workspace):
    """Verify that kmod command should not be able.

    to load kernel module with dependencies are not loaded
        1. Create an update package with a dependence to an \
        other module (load:auto) and update the target with it
        2. Verify both modules have not been loaded
        3. Try to load the required module: it should succeed
        4. Try to load the primary module: it should fail
        5. Compile the default package and update the target with it

    :param target: fixture to communicate with the target
    :param legato: fixture to call useful functions regarding legato
    :param create_temp_workspace: fixture to create a temporary folder
    """
    # Initialisation:
    # Verify existence of environment variables and files needed.
    # Prepare compilation
    test_name = "L_Tools_Kmod_0011"
    test_passed = True
    # Compile and update target
    swilog.step("Step 1: Compiling...")
    install_system(target, legato, create_temp_workspace, test_name)

    swilog.step("Step 2: Verify mods have not been loaded...")
    if check_presence(legato, test_name):
        test_passed = False
        swilog.error("Step 2: Primary kernel module has been unexpectedly loaded")
    if check_presence(legato, "L_Tools_Kmod_0005"):
        test_passed = False
        swilog.error("Step 2: Required kernel module has been unexpectedly loaded")

    swilog.step("Step 3: Loading primary module...")
    (returned_value, returned_index) = check_loading(target, test_name, RESULT_OK)
    if not returned_value:
        test_passed = False
        swilog.error("Step 3: Primary module has not been properly loaded.")

    swilog.step("Step 5: Trying to load the required module...")
    (returned_value, returned_index) = check_loading(
        target, "L_Tools_Kmod_0005", RESULT_DUPLICATE
    )
    if not returned_value:
        test_passed = False
        swilog.error(
            "Step 5: Required kernel module should have been properly forbidden"
        )

    swilog.step("Step 6: Unloading the primary module...")
    (returned_value, returned_index) = check_unloading(target, test_name, RESULT_OK)
    if not returned_value:
        test_passed = False
        swilog.error("Step 6: Kernel module has not been properly unloaded")

    swilog.step("Step 7: Verify mods have been unloaded...")
    if check_presence(legato, test_name):
        test_passed = False
        swilog.error("Step 7: Primary kernel module has not been unloaded")
    if check_presence(legato, "L_Tools_Kmod_0005"):
        test_passed = False
        swilog.error("Step 7: Required kernel module has not been unloaded")
    swilog.debug(returned_index)
    # End of script: Build the default package to reinitialise the target
    # And clean the LEGATO_ROOT directory
    assert test_passed, display_errors()


@pytest.mark.usefixtures("check_environment", "environment_setting")
def L_Tools_Kmod_0020(target, legato, create_temp_workspace):
    """Verify that kmod command able to load and unload.

    a kernel module requiring at least 2 kernel modules
    both requiring the same third module
    (every module are loaded manually)

    1. Create an update package (load: manual)
    2. Verify loading of the module has not been performed
    3. Load the module
    4. Unload the module
    5. Compile the default package and update the target with it

    :param target: fixture to communicate with the target
    :param legato: fixture to call useful functions regarding legato
    :param create_temp_workspace: fixture to create a temporary folder
    """
    # Verify existence of environment variables and files needed.
    # Prepare compilation
    test_name = "L_Tools_Kmod_0020"
    module_list = [
        test_name,
        "L_Tools_Kmod_0020_1",
        "L_Tools_Kmod_0020_2",
        "L_Tools_Kmod_0020_3",
        "L_Tools_Kmod_0020_common",
    ]
    test_passed = True
    # Compile and update target
    swilog.step("Step 1: Compiling...")
    install_system(target, legato, create_temp_workspace, test_name)

    swilog.step("Step 2: Verify mods have not been loaded...")
    for m in module_list:
        if check_presence(legato, test_name):
            test_passed = False
            swilog.error("Step 2: Kernel module %s has been unexpectedly loaded" % m)

    swilog.step("Step 3: Loading...")
    (returned_value, returned_index) = check_loading(target, test_name, RESULT_OK)
    if not returned_value:
        test_passed = False
        swilog.error("Step 3: Kernel module has not been properly loaded")

    wait_for_cm_info(target)

    for m in module_list:
        if not check_presence(legato, m):
            test_passed = False
            swilog.error("Step 3: Kernel module %s should have been loaded" % m)

    swilog.step("Step 5: Unloading...")
    (returned_value, returned_index) = check_unloading(target, test_name, RESULT_OK)
    if not returned_value:
        test_passed = False
        swilog.error("Step 5: Kernel module has not been properly unloaded")

    wait_for_cm_info(target)

    for m in module_list:
        if check_presence(legato, m):
            test_passed = False
            swilog.error("Step 3: Kernel module %s should have been unloaded" % m)
    swilog.debug(returned_index)
    # End of script: Build the default package to reinitialise the target
    # And clean the LEGATO_ROOT directory
    assert test_passed, display_errors()


@pytest.mark.usefixtures("check_environment", "environment_setting")
def L_Tools_Kmod_0021(target, legato, create_temp_workspace):
    """Verify kmod cmd unable to load/unload with manual start.

        1. Create an update package (load: manual)
        2. Make sure kernel module has been loaded and app is not running
        3. Start app
        4. Unload the kernel module
        5. Load the module
        6. Stop the app
        7. Unload the module
        8. Load the module
        9. Compile the default package and update the target with it

    :param target: fixture to communicate with the target
    :param legato: fixture to call useful functions regarding legato
    :param create_temp_workspace: fixture to create a temporary folder
    """
    test_name = "L_Tools_Kmod_0021"
    test_passed = True

    # Compile and update target
    swilog.step("Step 1: Compiling...")
    install_system(target, legato, create_temp_workspace, test_name)

    swilog.step("Step 2: Verify mod has been loaded...")
    if not check_presence(legato, test_name):
        test_passed = False
        swilog.error("Step 2: Kernel module has not been properly loaded")

    rsp = legato.get_app_status("helloWorld")
    assert "stopped" in rsp
    swilog.info("App helloWorld is stopped")

    swilog.step("Step 3: Start app helloWorld")
    legato.start("helloWorld")
    # Unload the kernel module using "kmod unload L_Tools_Kmod_0021.ko
    swilog.step("Step 4: Unloading...")
    (returned_value, returned_index) = check_unloading(target, test_name, RESULT_OK)

    if check_presence(legato, test_name):
        test_passed = False
        swilog.error("Step 4:" "Kernel module %s should have been unloaded" % test_name)

    swilog.step("Step 5: Loading...")
    (returned_value, returned_index) = check_loading(target, test_name, RESULT_OK)
    if not returned_value:
        test_passed = False
        swilog.error("Step 5: Kernel module has not been properly loaded")

    # Stop the app
    swilog.step("Step 6: Stop app helloWorld")
    legato.stop("helloWorld")
    rsp = legato.get_app_status("helloWorld")
    assert "stopped" in rsp
    swilog.info("App helloWorld is stopped")

    # Unload the kernel module
    swilog.step("Step 7: Unloading...")
    (returned_value, returned_index) = check_unloading(target, test_name, RESULT_OK)

    if check_presence(legato, test_name):
        test_passed = False
        swilog.error("Step7:" "Kernel module %s should have been unloaded" % test_name)

    # Load the kernel module
    swilog.step("Step 8: Loading...")
    (returned_value, returned_index) = check_loading(target, test_name, RESULT_OK)
    if not returned_value:
        test_passed = False
        swilog.error("Step 8: Kernel module has not been properly loaded")
    swilog.debug(returned_index)
    # End of script: Build the default package to reinitialise the target
    # And clean the LEGATO_ROOT directory
    assert test_passed, display_errors()
