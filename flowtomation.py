#!/usr/bin/python3

import sys
import os
import json
import subprocess
import shlex
from collections import OrderedDict
import time
import datetime
import enum
import utilities
import validate_time


class Direction(enum.Enum):
    INBOUND = "input"
    OUTBOUND = "output"


def verify_service_data_format(
        service,
        services,
        service_data,
        direction,
        logger
):
    """

    :param service:
    :param services:
    :param service_data:
    :param direction:
    :param logger:
    :return:
    """
    # get the data type
    data_type_configuration = services.get(service)\
        .get(direction)
    if not data_type_configuration:
        logger.error("service has data with no {0} configuration"
                     .format(direction))
        return False
    required_data_type = data_type_configuration.get("type")
    required_data_format = None
    # get the required format, if one exists
    if "format" in data_type_configuration:
        required_data_format = data_type_configuration.get("format")
    # verify a data type is configured and it is supported
    if not required_data_type:
        logger.warning("service: {0} - does not have an {1} data type configured"
                    .format(service, direction))
        return False
    elif required_data_type not in utilities.supported_data_types:
        logger.error("service: {0} - unsupported data type!"
                     .format(service, direction))
        return False

    # get the data payload
    try:
        json_message = json.loads(service_data.decode("utf-8"))
    except json.JSONDecodeError as e:
        logger.error("service: {0} - invalid JSON message provided!".format(service))
        return False

    # verify if the message contains the correct 'data' field
    data = json_message.get("data")
    if data is None:
        logger.error("service: {0} - JSON message does not contain the expected 'data' field"
                     .format(service))
        return False

    # we now have the service input/output data
    # the data type we have needs to be 'tested' against the configured data type
    if required_data_type != "time":
        result = isinstance(
            data,
            utilities.supported_data_types.get(required_data_type)
        )
        if not result:
            logger.error("{0} data type does not match required data type"
                         .format(direction))
    else:
        if not required_data_format:
            result = validate_time.convert_datetime_string_part2(data, logger)
        else:
            result = validate_time.convert_datetime_string_part2(data, logger, required_data_format)
    return result


def get_services(
        services,
        file_information,
        logger
):
    """

    :param services:
    :param file_information:
    :param logger:
    :return:
    """
    # search recursively for config.json files in 'services' directory
    result = ''
    get_failed = False
    for root, dirs, files in os.walk("services"):
        for file in files:
            if file == "config.json":
                # check if file information exists or the config has ben modified
                # service name is the parent directory name
                config_file_path = os.path.join(root, file)
                # if the file doesnt have any file information
                # it should be classed as 'new'
                # therefore we need to check if it is a duplicate name of an existing service
                new_file = True
                if file_information.get(config_file_path):
                    new_file = False
                if utilities.check_file_modified(
                    config_file_path,
                    file_information,
                    logger
                ):
                    # load the service
                    service_directory_name = os.path.basename(root)
                    log_line_prefix = "service in directory: {0} -".format(service_directory_name)
                    # verify if valid JSON via 'load_service'
                    service = utilities.load_service(
                        # services,
                        # service_directory_name,
                        config_file_path,
                        logger
                    )
                    if service:
                        logger.debug("{0} passed JSON validation!".format(log_line_prefix))

                    else:
                        logger.error("{0} failed JSON validation!".format(log_line_prefix))
                        return False
                    # verify configuration
                    # configuration = services.get(service_directory_name)


                    if utilities.verify_configuration(
                            service,
                            utilities.required_keys.get("service_configuration"),
                            logger
                    ):
                        logger.debug("{0} passed configuration verification!".format(log_line_prefix))
                        service_name = service.get("name")
                        # verify the directory name and service name match
                        if service_name != service_directory_name:
                            logger.error("directory name and service name for service {0} do not match"
                                         .format(service_directory_name))
                            get_failed = True
                            continue
                        # load the service into running configuration
                        if new_file and service_name not in services:
                            services[service_name] = service
                        elif not new_file and service_name in services:
                            # update (replace) the service
                            del services[service_name]
                            services[service_name] = service
                        else:
                            logger.error("service with the same name exists in the running configuration")
                            get_failed = True

                    else:
                        logger.error("{0} failed configuration verification".format(log_line_prefix))
                        # remove the service from running configuration
                        # remove the service if it is already installed

                        service_name = service.get("name")
                        if service_name in services:
                            del services[service_name]
                        else:
                            logger.debug("service name retrieval failed - unable to check if service"
                                         " exists in running-configuration")
                        get_failed = True

        continue
    if get_failed:
        return False
    return True


def get_command_line(
        service,
        services,
        file_information,
        service_output
):
    """

    :param service:
    :param services:
    :param file_information:
    :param service_output:
    :return:
    """
    program = services.get(service).get("program")
    parameters = services.get(service).get("parameters")
    # check for special symbol '$$' in parameters
    if parameters and "$$" in parameters:
        parameters = parameters.replace(
            "$$",
            json.loads(service_output.decode("utf-8")).get("data")
        )
    # check if the service uses a custom python script
    path = ''
    for key in file_information.keys():
        if service in key:
            file_path = os.path.dirname(key)
    if "./" in program:
        program = program[2:]
        path = "%s/" % (
            # escape any spaces so shlex doesnt split the directory name
            # get the file path
            " ".join(["%s\\" % line for line in file_path.split()])
        )

    if parameters:
        command_line = shlex.split(
                    '%s%s %s' % (
                        path,
                        program,
                        parameters
                    ),
                )
    else:
        command_line = shlex.split(
            '%s%s' % (
                path,
                program,
            ),
        )
    return command_line


def process_flow(
        f,
        flows,
        services,
        file_information,
        logger
):
    """

    :param f:
    :param flows:
    :param services:
    :param file_information:
    :param logger:
    :return:
    """
    # store our service output to use as input for the next service
    service_output = ''

    # check if all services listed in the flow loaded successfully
    if not utilities.flow_ready_to_run(
            services,
            flows,
            f,
            logger
    ):
        return False

    for service in flows.get(f):
        # verify service input i.e. 'service_output'
        if service_output and not verify_service_data_format(
            service,
            services,
            service_output,
            Direction.INBOUND.value,
            logger
        ):
            logger.error("service: {0} - failed input data type verification"
                         .format(service))
            return False

        # handle a possible exception if the service exits with a non-zero exit code
        # -service file/command not found
        # -permission issue on service file
        logger.info("running service {0} ...".format(service))
        command_line = get_command_line(
                    service,
                    services,
                    file_information,
                    service_output
                )

        try:
            result = subprocess.run(
                command_line,
                input=service_output,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            status = result.returncode
            service_output = result.stdout
            if service_output and not verify_service_data_format(
                service,
                services,
                service_output,
                Direction.OUTBOUND.value,
                logger
            ):
                logger.error("service: {0} - failed output data type verification!"
                             .format(service))
                return False
        except (
                subprocess.CalledProcessError,
                FileNotFoundError,
                PermissionError
        ) as e:
            result = e
            if type(result) == FileNotFoundError:
                status = result.errno
                logger.error(result.strerror)
            if type(result) == PermissionError:
                status = result.errno
                logger.error(result.strerror)
            if type(result) == subprocess.CalledProcessError:
                status = result.returncode
                logger.info(result.stderr.decode("utf-8").rstrip())

        # exit flow on non-zero return code
        if status != 0:
            return False
        continue
    return True


def main():
    """

    :return:
    """
    configuration_file_supplied = True
    log_level = "INFO"
    if len(sys.argv) == 3:
        if sys.argv[2].upper() == "DEBUG":
            log_level = "DEBUG"

    elif len(sys.argv) == 2:
        if sys.argv[1].upper() == "DEBUG":
            configuration_file_supplied = False
            log_level = "DEBUG"
        else:
            configuration_file_supplied = True
    else:
        configuration_file_supplied = False

    # setup logging
    logger = utilities.setup_logger("CPT223 A2", log_level)

    if not configuration_file_supplied:
        logger.info("configuration file not supplied as argument - using default")
        flow_configuration_file = "flowtomation.json"
    else:
        flow_configuration_file = sys.argv[1]

    # get the program configuration
    # get the services
    services = {}
    file_information = {}

    # process the flows
    while True:
        program_run_start_time = time.time()
        uninstalled_services = []
        logger.info("waiting for next flow start time ...")
        if utilities.flow_start_time():
            logger.info("it's go time!")
            # update/check the flow configuration file modified time
            modified = utilities.check_file_modified(
                flow_configuration_file,
                file_information,
                logger
            )
            if modified:
                # load the flow configuration
                try:
                    configuration = json.load(
                        open(flow_configuration_file),
                        object_pairs_hook=OrderedDict
                    )
                    logger.info("configuration loaded!")
                except json.JSONDecodeError as e:
                    error_message = "Failed to load program configuration " \
                                    "- Invalid JSON detected on/near line: {0}"\
                        .format(e.lineno - 1)
                    logger.critical(error_message)
                    sys.exit(error_message)

                # verify the mandatory configuration fields
                if not utilities.verify_configuration(
                    configuration,
                    utilities.required_keys.get("program_configuration_2"),
                    logger
                ):
                    error_message = "Failed to load program configuration " \
                                    "- configuration file missing mandatory section"
                    logger.critical(error_message)
                    sys.exit(error_message)

                # get the flow configuration
                flows = configuration.get("flows")
                logger.info("got the flows!")
            # update/check the service configuration files modified time
            # and load any new/updated service configurations
            if get_services(
                services,
                file_information,
                logger
            ):
                logger.info("got the services!")
            else:
                logger.warning("Error encountered getting services - please review the service configurations")
                # sys.exit("Error encountered loading services - see log file for details")

            # cleanup running-configuration
            # remove services uninstalled since last run
            logger.info("running service cleanup!")
            for file, file_info in file_information.items():
                try:
                    last_seen = file_info["last seen"]
                    if last_seen < program_run_start_time:
                        # remove from file information and services
                        uninstalled_services.append(file)
                        service = file.split("/")[-2]
                        logger.debug("removing uninstalled service {0} from running-configuration"
                                     .format(service))
                        del services[service]
                except KeyError:
                    logger.debug("file: {0} - missing last seen information"
                                 .format(file))

            # remove the uninstalled services from running-configuration
            for uninstalled_service in uninstalled_services:
                del file_information[uninstalled_service]

            logger.info("starting flows")
            for flow, service_list in flows.items():
                logger.info("running flow: {0}".format(flow))
                flow_status = ""
                start_time = datetime.datetime.now()
                # check the status of the flow
                log_line_prefix = "flow: {0} status -".format(flow)
                if process_flow(
                        flow,
                        flows,
                        services,
                        file_information,
                        logger
                ):
                    flow_status = "successful!"
                    logger.info("{0} flow ran to completion!".format(log_line_prefix))
                else:
                    flow_status = "failed!"
                    logger.info("{0} flow incomplete!".format(log_line_prefix))
                time_taken = datetime.datetime.now() - start_time
                # we need to wait until at least one second has elapsed
                # so we dont run more than once if the flow run time
                # is < one second
                if time_taken.seconds < 1:
                    time.sleep(1)
                continue

    sys.exit()


if __name__ == "__main__":
    main()












