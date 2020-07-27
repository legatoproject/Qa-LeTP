"""Fixtures for sampleApps."""

import os
import re
import time
import swilog
import pytest
import pexpect
import sim_lib

__copyright__ = "Copyright (C) Sierra Wireless Inc."


@pytest.fixture
def installapp_cleanup(target, legato, request, tmpdir):
    """Fixture to initialize (make, install application...).

    And cleanup the test.

    Args:
        target: fixture to communicate with the target
        legato: fixture to call useful functions regarding legato
        request: objiect to access the data
        tmpdir: fixture to provide a temporary directory
                unique to the test invocation
    """
    app_name = ["dataHub", "actuator", "sensor", "printServer", "printClient", ""]
    test_name = request.node.name.split("[")[0]
    os.chdir(str(tmpdir))
    legato.clear_target_log()
    app_path = getattr(request.module, "APP_PATH_%s" % test_name)

    if legato.get_current_system_index() != 0:
        legato.restore_golden_legato()

    if test_name == "L_SampleApps_DataHub_0001":

        legato.make_install(
            app_name[0], app_path=app_path, option=("-i %s/" % app_path)
        )
        legato.make_install(
            app_name[1], app_path="%s/test/" % app_path, option=("-i %s/" % app_path)
        )
        legato.make_install(
            app_name[2],
            app_path="%s/test/" % app_path,
            option=(
                "-i %s/ -i %s/components/periodicSensor/ "
                "-c %s/components/" % (app_path, app_path, app_path)
            ),
        )

        # Check apps are installed
        assert legato.is_app_exist(app_name[0])
        assert legato.is_app_exist(app_name[1])
        assert legato.is_app_exist(app_name[2])

        time.sleep(5)
        legato.restart(app_name[1])
        legato.restart(app_name[2])
    elif test_name == "L_SampleApps_HelloIpc_0001":
        legato.make_install(app_name[3], app_path)
        legato.make_install(app_name[4], app_path)

    else:
        app_name[5] = getattr(request.module, "APP_NAME_%s" % test_name)

        if test_name in ("L_SampleApps_HttpGet_0001", "L_SampleApps_Karaoke_0001"):
            legato.make_install(
                app_name[5], app_path=app_path, option=("-i %s/" % app_path)
            )

        elif test_name == ("L_SampleApps_HttpServer_0001"):
            cmd = "mkapp %s -t %s" % (
                os.path.join(app_path, app_name[5]) + ".adef",
                target.target_name,
            )
            swilog.info(cmd)

            # Need a long time to make app
            rsp, exit_status = pexpect.run(cmd, timeout=200, withexitstatus=True)
            swilog.debug(rsp)
            assert exit_status == 0, "[FAILED] Make app failed."
            legato.install(app_name[5])
        else:
            legato.make_install(app_name[5], app_path)

    phone_num = ""
    if test_name in ("L_SampleApps_Sms_0001", "L_SampleApps_ModemDemo_0001"):
        # Clear sms on the target
        target.run("cm sms clear", timeout=30, check=False)

        # Read the phone number in simdb.xml
        siminfo = sim_lib.get_sim_info(target)
        phone_num = siminfo.Tel
        # If the phone number is not set in xml
        if not phone_num:
            # Get Sim's phone number
            phone_num_rsp = target.run("cm sim number", withexitstatus=True)
            match_obj = re.search(
                r".*Phone Number: .* (.*)\r\n", phone_num_rsp[1], re.M
            )
            if match_obj:
                phone_num = match_obj.group(1)

        assert phone_num != "", "[FAILED] Please set the tel in simdb.xml"
        swilog.info("Phone number: %s" % phone_num)

    yield phone_num
    # Clean up target
    # In case the test is still in app runProc, terminate it
    target.sendcontrol("c")
    target.prompt()
    legato.restore_golden_legato()


@pytest.fixture()
def installsys_cleanup(target, legato, request, tmpdir):
    """Fixture to initialize (make, install system...) and cleanup the test.

    Args:
        target: fixture to communicate with the target
        legato: fixture to call useful functions regarding legato
        request: objiect to access the data
        tmpdir: fixture to provide a temporary directory
                unique to the test invocation
    """
    test_name = request.node.name.split("[")[0]

    sys_name = getattr(request.module, "SYS_NAME_%s" % test_name)
    sys_path = getattr(request.module, "SYS_PATH_%s" % test_name)

    os.chdir(str(tmpdir))

    if test_name == "L_SampleApps_Mqtt_0001":
        ret = os.system("/bin/ps -A |/bin/grep -w mosquitto")
        fail_mesg = (
            "[FAILED] Please install mosquitto " "and mosquitto-clients before test"
        )
        assert ret == 0, fail_mesg

        # Check mosquitto_pub is available
        ret = os.popen("/usr/bin/which mosquitto_pub").readlines()
        fail_mesg = "[FAILED] Please install mosquitto_pub before test"
        assert "/usr/bin/mosquitto_pub" in ret[0], fail_mesg

    # Build and instal system
    legato.make_install_sys(sys_name, sys_path=sys_path)
    # wait for system ready
    time.sleep(30)

    yield
    # Clean up target
    # In case the test is still in app runProc, terminate it
    target.sendcontrol("c")
    target.prompt()
    legato.restore_golden_legato()


@pytest.fixture()
def open_port(target):
    """Open the ports 8080 and 8443 for the HTTP server test.

    Args:
        target: fixture to communicate with the target
    """
    target.open_port(8080, "tcp")
    target.open_port(8443, "tcp")

    # NEED TO: this step should be removed
    # But opening only the ports does not seem to work. To investigate
    # Open all the ports
    target.run("iptables -I INPUT -j ACCEPT")
