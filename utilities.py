import datetime
import json
import logging
import logging.handlers
import numbers
import os
import time
from collections import OrderedDict

required_keys = {
        "program_configuration_1": [
            "services",
            "flows"
        ],
        "program_configuration_2": [
            "flows"
        ],
        "service_configuration": [
            "name",
            "description",
            "program"
        ]
    }

supported_data_types = {
    "number": numbers.Number,
    "string": str,
    "dictionary": dict,
    "array": list,
    "boolean": bool,
    "time": datetime.datetime
}


def setup_logger(
        name,
        log_level="INFO"
):
    """
    returns a logger object that will rotate the log files
    :param name:
    :param log_level:
    :return:
    """
    level = logging.getLevelName(log_level)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    log_file_name = "flowtomation.log"
    fh = logging.handlers.RotatingFileHandler(
        filename=log_file_name,
        maxBytes=100000,
        backupCount=3
    )
    fh.setLevel(level)
    formatter = logging.Formatter(
        '%(asctime)s: %(levelname)s: %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p'
    )
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger


def check_file_modified(
        file_name,
        file_information,
        logger
):
    """

    :param logger:
    :param file_name:
    :param file_information:
    :return:
    """

    result = ''

    file_info = os.stat(file_name)
    file_current_modified_time = file_info.st_mtime

    try:
        file_information.get(file_name)["file_last_modified"]

    except TypeError:
        file_information[file_name] = {}
        file_information.get(file_name)["file_last_modified"] = file_current_modified_time
        logger.debug("no modified information found for file {0}".format(file_name))
        logger.debug("last modified time created for file: {0}".format(file_name))
        file_information.get(file_name)["last seen"] = time.time()
        return True
    else:
        file_last_modified_time = file_information.get(file_name)["file_last_modified"]

    file_information.get(file_name)["last seen"] = time.time()

    if file_last_modified_time < file_current_modified_time:
        file_information.get(file_name)["file_last_modified"] = file_current_modified_time
        logger.debug("last modified time updated for file: {0}".format(file_name))
        return True
    else:
        logger.debug("no changes detected since last run for file: {0}".format(file_name))
        return False


def verify_configuration(
        configuration,
        required_keys,
        logger
):
    """

    :param configuration:
    :param required_keys:
    :param logger:
    :return:
    """
    verification_passed = True
    for key in required_keys:
        if key not in configuration:
            logger.error("missing mandatory field in configuration")
            verification_passed = False

    # check the configuration of the optional fields
    # - parameters: string
    # - input, output: have a type field, and one of the set values
    field = "parameters"
    if field in configuration:
        if not isinstance(
                configuration.get(field),
                str
        ):
            verification_passed = False
            logger.error("field: {0} - incorrect type".format(field))
    fields = [
        "input",
        "output"
    ]
    for field in fields:
        if field in configuration:
            # check if it has the 'type' key
            key = configuration.get(field)
            type_field = "type"
            if type_field in key:
                if not key.get(type_field) in supported_data_types:
                    verification_passed = False
                    logger.error("configured type is not supported for field {0}"
                                 .format(field))
            else:
                verification_passed = False
                logger.error("field: {0} - missing mandatory field"
                             .format(field))

    if verification_passed:
        return True
    return False


def load_service(
        # services,
        # service_name,
        config_file,
        logger
):
    """
    verify if the configuration is in valid JSON format
    :param config_file:
    :param logger:
    :return:
    """
    try:
        return json.load(
            open(
                config_file
            ),
            object_pairs_hook=OrderedDict
        )
        # services[service.get("name")] = service
    except json.JSONDecodeError as e:
        error_message = "Failed to load configuration - Invalid JSON detected on/near line: {0}".format(e.lineno - 1)
        logger.warning(error_message)
        # remove the service if it is already installed
        # if service_name in services:
        #     del services[service_name]
        return False


def flow_ready_to_run(
        services,
        flows,
        flow,
        logger
):
    """
    verify if all services configured in the flow have been loaded into running-configuration
    :param services:
    :param flows:
    :param flow:
    :param logger:
    :return:
    """
    flow_ready = True
    missing_services = []
    logger.info("checking availability of services configured in flow: {0}".format(flow))
    for service in flows.get(flow):
        if not services.get(service):
            logger.error("service: {0} - does not exist!".format(service))
            missing_services.append(service)
            flow_ready = False
    if not flow_ready:
        logger.warning("flow: {0} - will be skipped due to missing service(s):".format(flow))
        for m in missing_services:
            logger.info(" - {0}".format(m))
        return False
    else:
        logger.info("flow: {0} - is ready to run".format(flow))
        return True


def flow_start_time():
    """
    make the program wait until the next available minute
    :return:
    """
    time_to_start = False
    while not time_to_start:
        second = datetime.datetime.now().second
        if second != 0:
            time.sleep(1)
        else:
            time_to_start = True
    return True
