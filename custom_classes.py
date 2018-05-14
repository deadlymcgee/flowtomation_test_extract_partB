import validate_time
from custom_classes_part_2 import AppService
import sys
import json


class TimeOfDayService(AppService):
    def __init__(self, input_time):
        # set result to False
        # self.result = ""
        # part 2
        # self.result = "False"
        # self.status = 0

        # part 1
        # we are validating the input within the service
        # self.input_time = input_time

        # part 2
        input_time = json.loads(
            input_time
        ).get("data")

        # part 1/2
        # part 2 - the program has already validated the time
        # so all we need is the datetime object
        self.validated_time = validate_time.convert_datetime_string(
            input_time,
        )

        # part 1
        # if not self.validated_time:
        #     # provide an error message to stderr,
        #     # return code will be 1, and
        #     # a CalledProcessError exception will be raised
        #     self.status = "Invalid time given!"
        # else:
        #     self.process_time(self.validated_time)

        # part 2
        self.process_time(self.validated_time)

        self.result_bytes = self.result.encode(sys.stdout.encoding)

    def process_time(self, validated_time):
        pass


class Morning(TimeOfDayService):
    def process_time(self, validated_time):
        if validated_time.hour < 12:
            # self.result = "True"
            # part 2
            self.app_service_output["data"] = True
        else:
            self.app_service_output["data"] = False


class Afternoon(TimeOfDayService):
    def process_time(self, validated_time):
        if 12 <= validated_time.hour < 18:
            # self.result = "True"
            # part 2
            self.app_service_output["data"] = True
        else:
            self.app_service_output["data"] = False


class Evening(TimeOfDayService):
    def process_time(self, validated_time):
        if 18 <= validated_time.hour < 24:
            # self.result = "True"
            # part 2
            self.app_service_output["data"] = True
        else:
            self.app_service_output["data"] = False
