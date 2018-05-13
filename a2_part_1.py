#!/usr/bin/python3

import sys
import json
import subprocess
import shlex
from collections import OrderedDict
import time
import datetime
import os
import enum
import utilities

# ------------------------------------------------------------------------------
# part 2
import numbers
import validate_time

supported_data_types = {
    "number": numbers.Number,
    "string": str,
    "dictionary": dict,
    "array": list,
    "boolean": bool,
    "time": datetime.datetime
}


class Direction(enum.Enum):
    INBOUND = "input"
    OUTBOUND = "output"


def verify_service_data_format(
        service,
        services,
        service_data,
        direction
):
    """
    -service input will be the output of the preceding service in the flow
    -input will be in the form of a JSON formatted string
    :return:
    """
    # get the data type
    data_type_configuration = services.get(service)\
        .get(direction)
    required_data_type = data_type_configuration.get("type")
    # verify a data type is configured and it is supported
    if not required_data_type or required_data_type not in supported_data_types:
        # TODO: provide feedback?
        return False
    # else:
    #     # get the required format, if one exists
    #     pass
    # get the data payload
    # TODO: move this check to the top?
    if service_data:
        # service_data = service_data.decode("utf-8")
        try:
            data = json.loads(service_data.decode("utf-8")).get("data")
        except json.JSONDecodeError as e:
            return False

        # we now have the service input/output data
        # the data type we have needs to be 'tested' against the configured data type
        if required_data_type != "time":
            result = isinstance(
                data,
                supported_data_types.get(required_data_type)
            )
        else:
            result = validate_time.convert_datetime_string_part2(data)
        return result

    return False


# def get_configuration_part_2(
#         service,
#         service
# ):
#     pass
#
def get_services_part_2():
    # search recursively for config.json files in 'services' directory
    result = ''
    services = {}
    for root, dirs, files in os.walk("services"):
        for file in files:
            if file == "config.json":
                result = "found!"
                service = json.load(
                    open(
                        os.path.join(root, file)
                    ),
                    object_pairs_hook=OrderedDict
                )
                services[service.get("name")] = service
        continue
    return services

# # ------------------------------------------------------------------------------
#
#
# def get_services_part_1():
#
#     return services


def get_configuration_part_1(
        service,
        services,
        service_output
):
    program = services.get(service)["program"]
    parameters = services.get(service)["parameters"]
    # check for special symbol '$$' in parameters
    if "$$" in parameters:
        parameters = parameters.replace("$$", service_output.decode("utf-8"))
    # part 2 only
    # check if the service uses a custom python script
    path = ''
    if "./" in program:
        program = program[2:]
        path = "%s/%s/" % (
            "services",
            # escape any spaces so shlex doesnt split the directory name
            " ".join(["%s\\" % line for line in service.split()])
        )

    command_line = shlex.split(
                    '%s%s %s' % (
                        path,
                        program,
                        parameters
                    ),
                )
    return command_line


def process_flow(f, flows, services):
    # TODO: docstring
    # store our service output to use as input for the next service
    service_output = ''
    for service in flows.get(f):
        # TODO: check for service_output here instead of 'verify_service_data_format'
        # part 2 only
        # verify service input i.e. 'service_output'
        # TODO: handle exception raised by 'verify_service_data_format'
        verify_service_data_format(
            service,
            services,
            service_output,
            Direction.INBOUND.value
        )

        # handle a possible exception if the service exits with a non-zero exit code
        try:
            result = subprocess.run(
                get_configuration_part_1(
                    service,
                    services,
                    service_output
                ),
                input=service_output,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            service_output = result.stdout
            if not verify_service_data_format(
                service,
                services,
                service_output,
                Direction.OUTBOUND.value
            ):
                return False
        except subprocess.CalledProcessError as e:
            result = e
            pass
        # return error code if stderr
        status = result.returncode

        # exit flow on non-zero return code
        if status != 0:
            return False
        continue
    return True


def main():
    # setup logging
    logger = utilities.setup_logger("CPT223 A2")

    # get the program configuration
    # TODO: handle invalid json etc per specs
    configuration = json.load(
        open("test.json"),
        object_pairs_hook=OrderedDict
    )
    logger.info("configuration loaded!")
    # get the flow configuration
    flows = configuration.get("flows")
    logger.info("got the flows!")

    # get the services
    # part 1
    # services = configuration.get("services")

    # part 2
    services = get_services_part_2()
    logger.info("got the services!")
    # process the flows
    while True:
        logger.info("starting flows")
        for flow, service_list in flows.items():
            logger.info("running flow: {0}".format(flow))
            flow_status = ""
            start_time = datetime.datetime.now()
            # check the status of the flow
            log_line_prefix = "flow {0} status:".format(flow)
            if process_flow(flow, flows, services):
                flow_status = "successful!"
                logger.info("{0} successful!".format(log_line_prefix))
            else:
                flow_status = "failed!"
                logger.info("{0} failed!".format(log_line_prefix))
            time_taken = datetime.datetime.now() - start_time
            continue
        time.sleep(1)

    sys.exit()


if __name__ == "__main__":
    main()












