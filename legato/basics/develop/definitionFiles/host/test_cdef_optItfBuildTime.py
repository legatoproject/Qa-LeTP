"""Component Definition Files test.

Set of functions to test the Legato component definition files.
"""
import os

import pytest

from pytest_letp.lib import swilog

__copyright__ = "Copyright (C) Sierra Wireless Inc."
# ====================================================================================
# Constants and Globals
# ====================================================================================
# Determine the resources folder (legato apps)
TEST_RESOURCES = os.path.join(os.path.abspath(os.path.dirname(__file__)), "resources")


# ====================================================================================
# Functions
# ====================================================================================
def verify_when_build_successful(
    ipc_type_str, interface_opts_str, build_cmd_str, is_binded_str, api_type_str
):
    """Verify if the building is successful.

    Args:
        ipc_type_str: ipc type
                   client-side IPC
                   server-side IPC
        interface_opts_str: interface optionals
                         [optional]
                         [optional] [manual-start]
                         [optional] [types-only]
        build_cmd_str: build command
                     mkapp: command to make application
                     mksys: command to make system
        is_binded_str: binding string
                     bound
                     not bound
        api_type_str: directory name of API type
                   legato API
                   customized API
    """
    if ipc_type_str in "client-side IPC":
        if (interface_opts_str in "[optional]") or (
            interface_opts_str in "[optional] [manual-start]"
        ):
            # Build succesful when client-side IPC
            # With interface options [optional]/[optional] [manual-start]
            swilog.info(
                "%s doesn't complain when the %s API is %s to %s "
                "with the interface options: %s"
                % (
                    build_cmd_str,
                    ipc_type_str,
                    is_binded_str,
                    api_type_str,
                    interface_opts_str,
                )
            )
        else:
            # Build successful when client-side IPC
            # With interface options [optional] [types-only]
            swilog.error(
                "%s doesn't complain when the %s API is %s to %s "
                "with the interface options: %s"
                % (
                    build_cmd_str,
                    ipc_type_str,
                    is_binded_str,
                    api_type_str,
                    interface_opts_str,
                )
            )
    else:
        # Build successful when server-side IPC
        # With interface options that contain optional
        swilog.error(
            "%s doesn't complain when the %s provides %s "
            "with interface options: %s"
            % (build_cmd_str, ipc_type_str, api_type_str, interface_opts_str)
        )


def verify_when_build_fail(
    ipc_type_str, interface_opts_str, build_cmd_str, is_binded_str, api_type_str
):
    """Verify if the building is failed.

    Args:
        ipc_type_str: ipc type
                   client-side IPC
                   server-side IPC
        interface_opts_str: interface optionals
                         [optional]
                         [optional] [manual-start]
                         [optional] [types-only]
        build_cmd_str: build command
                     mkapp: command to make application
                     mksys: command to make system
        is_binded_str: binding string
                     bound
                     not bound
        api_type_str: directory name of API type
                     legato API
                     customized API
    """
    if ipc_type_str == "client-side IPC":
        if interface_opts_str == "[optional] [types-only]":
            # Build unsuccessful when client-side IPC
            # With interface options [optional] [types-only]
            swilog.info(
                "%s complains when the %s is %s to %s "
                "with the interface options: %s"
                % (
                    build_cmd_str,
                    ipc_type_str,
                    is_binded_str,
                    api_type_str,
                    interface_opts_str,
                )
            )
        else:
            # Build unsuccessful when client-side IPC
            # With interface options [optional]/[optional] [manual-start]
            swilog.error(
                "%s complains when the %s API is %s to %s "
                "with the interface options: %s"
                % (
                    build_cmd_str,
                    ipc_type_str,
                    is_binded_str,
                    api_type_str,
                    interface_opts_str,
                )
            )
    else:
        # Build unsuccessful when server-side IPC
        # With interface options that contain optional
        swilog.info(
            "%s complains when the %s provides %s "
            "with interface options: %s"
            % (build_cmd_str, ipc_type_str, api_type_str, interface_opts_str)
        )


def build_sys(
    legato,
    api_type_dir_name,
    ipc_type_dir_name,
    build_cmd_dir_name,
    interface_opts,
    binding_str,
    build_status=False,
):
    """Build system and verify that it's built successfully or not.

    Args:
        legato: fixture to call useful functions regarding legato
        api_type_dir_name: directory name of API type
                        legatoAPI: legato API
                        customizedAPI: customized API
        ipc_type_dir_name: directory name of IPC type
                        clientIPC: client-side IPC
                        serverIPC: server-side IPC
        build_cmd_dir_name: building command (mksys)
        interface_opts: interface optionals
                     optional: [optional]
                     optional_manualStart: [optional] [manual-start]
                     optional_typesOnly: [optional] [types-only]
        binding_str: binding string
                  withBindings: bound
                  withoutBindings: not bound
        build_status: build status
                   False: it's built successfully (default value)
                   True: it's built failed
    """
    system_file_path = "%s/%s/%s" % (
        api_type_dir_name,
        ipc_type_dir_name,
        build_cmd_dir_name,
    )
    sdef_file_name = "%s_%s" % (interface_opts, binding_str)

    # The appropriate directory that contains the definition files
    sys_path = "%s/cdef/interfaceOptions/optional/%s" % (
        TEST_RESOURCES,
        system_file_path,
    )

    # Parse args to readable string
    if api_type_dir_name == "legatoAPI":
        api_type_dir_name = "legato API"
    elif api_type_dir_name == "customizedAPI":
        api_type_dir_name = "customized API"

    if ipc_type_dir_name == "clientIPC":
        ipc_type_dir_name = "client-side IPC"
    elif ipc_type_dir_name == "serverIPC":
        ipc_type_dir_name = "server-side IPC"

    if interface_opts == "optional":
        interface_opts = "[optional]"
    elif interface_opts == "optional_manualStart":
        interface_opts = "[optional] [manual-start]"
    elif interface_opts == "optional_typesOnly":
        interface_opts = "[optional] [types-only]"

    if binding_str == "withBindings":
        binding_str = "bound"
    elif binding_str == "withoutBindings":
        binding_str = "not bound"

    # Build the system based on the sdef file name
    legato.make_sys(sdef_file_name, sys_path, should_fail=build_status)
    if build_status is False:
        verify_when_build_successful(
            ipc_type_dir_name,
            interface_opts,
            build_cmd_dir_name,
            binding_str,
            api_type_dir_name,
        )
    else:
        verify_when_build_fail(
            ipc_type_dir_name,
            interface_opts,
            build_cmd_dir_name,
            binding_str,
            api_type_dir_name,
        )


def build_app(
    legato,
    api_type_dir_name,
    ipc_type_dir_name,
    build_cmd_dir_name,
    interface_opts,
    binding_str,
    build_status=False,
):
    """Build application and verify that it's built successfully or not.

    :param legato: fixture to call useful functions regarding legato
    :param api_type_dir_name: directory name of API type
                        legatoAPI: legato API
                        customizedAPI: customized API
    :param ipc_type_dir_name: directory name of IPC type
                          clientIPC: client-side IPC
                          serverIPC: server-side IPC
    :param build_cmd_dir_name: building command (mkapp)
    :param interface_opts: interface optionals
                        optional: [optional]
                        optional_manualStart: [optional] [manual-start]
                        optional_typesOnly: [optional] [types-only]
    :param binding_str: binding string
                     withBindings: bound
                     withoutBindings: not bound
    :param build_status: build status
                      False: it's built successfully (default value)
                      True: it's built failed
    """
    app_files_path = "%s/%s/%s" % (
        api_type_dir_name,
        ipc_type_dir_name,
        build_cmd_dir_name,
    )
    adef_file_name = "%s_%s" % (interface_opts, binding_str)

    # The appropriate directory that contains the definition files
    app_path = "%s/cdef/interfaceOptions/optional/%s" % (TEST_RESOURCES, app_files_path)
    # Parse args to readable string
    if api_type_dir_name == "legatoAPI":
        api_type_dir_name = "legato API"
    elif api_type_dir_name == "customizedAPI":
        api_type_dir_name = "customized API"

    if ipc_type_dir_name == "clientIPC":
        ipc_type_dir_name = "client-side IPC"
    elif ipc_type_dir_name == "serverIPC":
        ipc_type_dir_name = "server-side IPC"

    if interface_opts == "optional":
        interface_opts = "[optional]"
    elif interface_opts == "optional_manualStart":
        interface_opts = "[optional] [manual-start]"
    elif interface_opts == "optional_typesOnly":
        interface_opts = "[optional] [types-only]"

    if binding_str == "withBindings":
        binding_str = "bound"
    elif binding_str == "withoutBindings":
        binding_str = "not bound"

    # Build the app based on the adef file name
    legato.make(adef_file_name, app_path, should_fail=build_status)
    if build_status is False:
        verify_when_build_successful(
            ipc_type_dir_name,
            interface_opts,
            build_cmd_dir_name,
            binding_str,
            api_type_dir_name,
        )
    else:
        verify_when_build_fail(
            ipc_type_dir_name,
            interface_opts,
            build_cmd_dir_name,
            binding_str,
            api_type_dir_name,
        )


# ====================================================================================
# Local fixtures
# ====================================================================================
@pytest.fixture(autouse=True)
def init_test(tmpdir):
    """Init the test.

    Args:
        tmpdir: fixture to provide a temporary directory
             unique to the test invocation
    """
    # Go to temp directory
    os.chdir(str(tmpdir))


# ====================================================================================
# Test functions
# ====================================================================================
def L_CDEF_0006(legato):
    """Verify "mkapp" will not complain if there's no optional client-side.

    IPC API to be bound with customized server-side interfaces.

    Args:
        legato: fixture to call useful functions regarding legato
    """
    build_app(
        legato, "customizedAPI", "clientIPC", "mkapp", "optional", "withoutBindings"
    )

    failed_testcases_list = swilog.get_error_list()
    if failed_testcases_list != []:
        assert 0, "Some tests failed:\n%s" % "\n".join(failed_testcases_list)


def L_CDEF_0007(legato):
    """Verify "mkapp" will not complain if there's no optional client-side.

    IPC API to be bound with Legato's server-side interfaces.

    Args:
        legato: fixture to call useful functions regarding legato
    """
    build_app(legato, "legatoAPI", "clientIPC", "mkapp", "optional", "withoutBindings")

    failed_testcases_list = swilog.get_error_list()
    if failed_testcases_list != []:
        assert 0, "Some tests failed:\n%s" % "\n".join(failed_testcases_list)


def L_CDEF_0008(legato):
    """Verify that "mkapp" will be successful if optional client-side IPC API.

    is bound with Legato's server-side interfaces.

    Args:
        legato: fixture to call useful functions regarding legato
    """
    build_app(legato, "legatoAPI", "clientIPC", "mkapp", "optional", "withBindings")

    failed_testcases_list = swilog.get_error_list()
    if failed_testcases_list != []:
        assert 0, "Some tests failed:\n%s" % "\n".join(failed_testcases_list)


def L_CDEF_0009(legato):
    """Verify that "mkapp" will be successful if optional client-side IPC API.

    is bound with customized server-side interfaces.

    Args:
        legato: fixture to call useful functions regarding legato
    """
    build_app(legato, "customizedAPI", "clientIPC", "mkapp", "optional", "withBindings")

    failed_testcases_list = swilog.get_error_list()
    if failed_testcases_list != []:
        assert 0, "Some tests failed:\n%s" % "\n".join(failed_testcases_list)


def L_CDEF_0010(legato):
    """Verify that "mkapp" will be unsuccessful if client-side IPC API options.

    are types-only and optional and to require Legato API.

    Args:
        legato: fixture to call useful functions regarding legato
    """
    build_app(
        legato,
        "legatoAPI",
        "clientIPC",
        "mkapp",
        "optional_typesOnly",
        "withoutBindings",
        build_status=True,
    )

    failed_testcases_list = swilog.get_error_list()
    if failed_testcases_list != []:
        assert 0, "Some tests failed:\n%s" % "\n".join(failed_testcases_list)


def L_CDEF_0011(legato):
    """Verify that "mkapp" will be successful if client-side IPC API options.

    are optional and manual start and to require Legato API.

    Args:
        legato: fixture to call useful functions regarding legato
    """
    build_app(
        legato,
        "legatoAPI",
        "clientIPC",
        "mkapp",
        "optional_manualStart",
        "withoutBindings",
    )

    failed_testcases_list = swilog.get_error_list()
    if failed_testcases_list != []:
        assert 0, "Some tests failed:\n%s" % "\n".join(failed_testcases_list)


def L_CDEF_0012(legato):
    """Verify that "mkapp" will complain "[optional]" is only for client-side.

    IPC option when the server app provides Legato API.

    Args:
        legato: fixture to call useful functions regarding legato
    """
    build_app(
        legato,
        "legatoAPI",
        "serverIPC",
        "mkapp",
        "optional",
        "withoutBindings",
        build_status=True,
    )

    failed_testcases_list = swilog.get_error_list()
    if failed_testcases_list != []:
        assert 0, "Some tests failed:\n%s" % "\n".join(failed_testcases_list)


def L_CDEF_0013(legato):
    """Verify "mksys" will not complain if there's no optional client-side.

    IPC API to be bound with Legato's server-side interfaces.

    Args:
        legato: fixture to call useful functions regarding legato
    """
    build_sys(legato, "legatoAPI", "clientIPC", "mksys", "optional", "withoutBindings")

    failed_testcases_list = swilog.get_error_list()
    if failed_testcases_list != []:
        assert 0, "Some tests failed:\n%s" % "\n".join(failed_testcases_list)


def L_CDEF_0014(legato):
    """Verify "mksys" will not complain if there's no optional client-side.

    IPC API to be bound with customized server-side interfaces.

    Args:
        legato: fixture to call useful functions regarding legato
    """
    build_sys(
        legato, "customizedAPI", "clientIPC", "mksys", "optional", "withoutBindings"
    )

    failed_testcases_list = swilog.get_error_list()
    if failed_testcases_list != []:
        assert 0, "Some tests failed:\n%s" % "\n".join(failed_testcases_list)


def L_CDEF_0015(legato):
    """Verify that "mksys" will be successful if optional client-side IPC API.

    is bound with Legato's server-side interfaces.

    Args:
        legato: fixture to call useful functions regarding legato
    """
    build_sys(legato, "legatoAPI", "clientIPC", "mksys", "optional", "withBindings")

    failed_testcases_list = swilog.get_error_list()
    if failed_testcases_list != []:
        assert 0, "Some tests failed:\n%s" % "\n".join(failed_testcases_list)


def L_CDEF_0016(legato):
    """Verify that "mksys" will be successful if optional client-side IPC API.

    is bound with customized server-side interfaces.

    Args:
        legato: fixture to call useful functions regarding legato
    """
    build_sys(legato, "customizedAPI", "clientIPC", "mksys", "optional", "withBindings")

    failed_testcases_list = swilog.get_error_list()
    if failed_testcases_list != []:
        assert 0, "Some tests failed:\n%s" % "\n".join(failed_testcases_list)


def L_CDEF_0017(legato):
    """Verify that "mksys" will be unsuccessful if client-side IPC API options.

    are types-only and optional and to require Legato API.

    Args:
        legato: fixture to call useful functions regarding legato
    """
    build_sys(
        legato,
        "legatoAPI",
        "clientIPC",
        "mksys",
        "optional_typesOnly",
        "withoutBindings",
        build_status=True,
    )

    failed_testcases_list = swilog.get_error_list()
    if failed_testcases_list != []:
        assert 0, "Some tests failed:\n%s" % "\n".join(failed_testcases_list)


def L_CDEF_0018(legato):
    """Verify that "mksys" will be successful if client-side IPC API options.

    are optional and manual start and to require Legato API.

    Args:
        legato: fixture to call useful functions regarding legato
    """
    build_sys(
        legato,
        "legatoAPI",
        "clientIPC",
        "mksys",
        "optional_manualStart",
        "withoutBindings",
    )

    failed_testcases_list = swilog.get_error_list()
    if failed_testcases_list != []:
        assert 0, "Some tests failed:\n%s" % "\n".join(failed_testcases_list)


def L_CDEF_0019(legato):
    """Verify that "mksys" will complain "[optional]" is only for client-side.

    IPC option when the server app provides Legato API.

    Args:
        legato: fixture to call useful functions regarding legato
    """
    build_sys(
        legato,
        "legatoAPI",
        "serverIPC",
        "mksys",
        "optional",
        "withoutBindings",
        build_status=True,
    )

    failed_testcases_list = swilog.get_error_list()
    if failed_testcases_list != []:
        assert 0, "Some tests failed:\n%s" % "\n".join(failed_testcases_list)


def L_CDEF_0020(legato):
    """Verify that requires section can't have duplicated API.

    (without interface option)

    Args:
        legato: fixture to call useful functions regarding legato
    """
    build_app(
        legato,
        "legatoAPI",
        "clientIPC",
        "mkapp",
        "optional_typesOnly",
        "withBindings",
        build_status=True,
    )

    failed_testcases_list = swilog.get_error_list()
    if failed_testcases_list != []:
        assert 0, "Some tests failed:\n%s" % "\n".join(failed_testcases_list)


def L_CDEF_0021(legato):
    """Verify that requires section can't have duplicated API.

    (with interface option)

    Args:
        legato: fixture to call useful functions regarding legato
    """
    build_app(
        legato,
        "customizedAPI",
        "clientIPC",
        "mkapp",
        "optional_typesOnly",
        "withBindings",
        build_status=True,
    )

    failed_testcases_list = swilog.get_error_list()
    if failed_testcases_list != []:
        assert 0, "Some tests failed:\n%s" % "\n".join(failed_testcases_list)


def L_CDEF_0022(legato):
    """Verify that "mkapp" will be successful if client-side IPC API options.

    are optional and manual start and to require customized API.

    Args:
        legato: fixture to call useful functions regarding legato
    """
    build_app(
        legato,
        "customizedAPI",
        "clientIPC",
        "mkapp",
        "optional_manualStart",
        "withoutBindings",
    )

    failed_testcases_list = swilog.get_error_list()
    if failed_testcases_list != []:
        assert 0, "Some tests failed:\n%s" % "\n".join(failed_testcases_list)


def L_CDEF_0023(legato):
    """Verify that "mkapp" will be unsuccessful if client-side IPC API options.

    are types-only and optional and to require customized API.

    Args:
        legato: fixture to call useful functions regarding legato
    """
    build_app(
        legato,
        "customizedAPI",
        "clientIPC",
        "mkapp",
        "optional_typesOnly",
        "withoutBindings",
        build_status=True,
    )

    failed_testcases_list = swilog.get_error_list()
    if failed_testcases_list != []:
        assert 0, "Some tests failed:\n%s" % "\n".join(failed_testcases_list)


def L_CDEF_0024(legato):
    """Verify that "mksys" will be successful if client-side IPC API options.

    are optional and manual start and to require customized API.

    Args:
        legato: fixture to call useful functions regarding legato
    """
    build_sys(
        legato,
        "customizedAPI",
        "clientIPC",
        "mksys",
        "optional_manualStart",
        "withoutBindings",
    )

    failed_testcases_list = swilog.get_error_list()
    if failed_testcases_list != []:
        assert 0, "Some tests failed:\n%s" % "\n".join(failed_testcases_list)


def L_CDEF_0025(legato):
    """Verify that "mksys" will be unsuccessful if client-side IPC API options.

    are types-only and optional and to require customized API.

    Args:
        legato: fixture to call useful functions regarding legato
    """
    build_sys(
        legato,
        "customizedAPI",
        "clientIPC",
        "mksys",
        "optional_typesOnly",
        "withoutBindings",
        build_status=True,
    )

    failed_testcases_list = swilog.get_error_list()
    if failed_testcases_list != []:
        assert 0, "Some tests failed:\n%s" % "\n".join(failed_testcases_list)


def L_CDEF_0026(legato):
    """Verify that "mkapp" will complain "[optional]" is only for client-side.

    IPC option when the server app provides customized API.

    Args:
        legato: fixture to call useful functions regarding legato
    """
    build_app(
        legato,
        "customizedAPI",
        "serverIPC",
        "mkapp",
        "optional",
        "withoutBindings",
        build_status=True,
    )

    failed_testcases_list = swilog.get_error_list()
    if failed_testcases_list != []:
        assert 0, "Some tests failed:\n%s" % "\n".join(failed_testcases_list)


def L_CDEF_0027(legato):
    """Verify that "mksys" will complain "[optional]" is only for client-side.

    IPC option when the server app provides customized API.

    Args:
        legato: fixture to call useful functions regarding legato
    """
    build_sys(
        legato,
        "customizedAPI",
        "serverIPC",
        "mksys",
        "optional",
        "withoutBindings",
        build_status=True,
    )

    failed_testcases_list = swilog.get_error_list()
    if failed_testcases_list != []:
        assert 0, "Some tests failed:\n%s" % "\n".join(failed_testcases_list)
