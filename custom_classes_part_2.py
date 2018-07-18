import sys
import os
import datetime


content_root = "/".join(os.path.dirname(os.path.realpath(__file__))
                        .split("/")[:-1])
sys.path.insert(
    0,
    content_root
)
python_path = sys.path
import validate_time
import json


class AppService:
    result = ''
    status = 0

    # the AppService needs to do the following when intitialised
    # -initialise dictionaries to store:
    # --output
    # --input
    app_service_input = {}
    app_service_output = {}

    def convert_output_to_json_bytes(self):
        return json.dumps(self.app_service_output).encode(sys.stdout.encoding)

    def get_results(self):
        return self.status,\
               self.convert_output_to_json_bytes()


class TimeOfDayService(AppService):
    def __init__(self, input_time):
        input_time = json.loads(
            input_time
        ).get("data")

        # the program has already validated the time
        # so all we need is the datetime object
        self.validated_time = validate_time.convert_datetime_string(
            input_time,
        )

        self.process_time(self.validated_time)

        self.result_bytes = self.result.encode(sys.stdout.encoding)

    def process_time(self, validated_time):
        pass


class Morning(TimeOfDayService):
    def process_time(self, validated_time):
        if validated_time.hour < 12:
            self.app_service_output["data"] = True
        else:
            self.app_service_output["data"] = False


class Afternoon(TimeOfDayService):
    def process_time(self, validated_time):
        if 12 <= validated_time.hour < 18:
            self.app_service_output["data"] = True
        else:
            self.app_service_output["data"] = False


class Evening(TimeOfDayService):
    def process_time(self, validated_time):
        if 18 <= validated_time.hour < 24:
            self.app_service_output["data"] = True
        else:
            self.app_service_output["data"] = False


class CustomSchedule(TimeOfDayService):

    def check_schedule(self, time_unit):
        if self.time_unit % self.schedule == 0:
            return True
        else:
            return False

    def minute_option(self):
        if self.validated_time.second == 0:
            self.time_unit = self.validated_time.minute
        else:
            return False

    def __init__(self, schedule, time_option, input_time):
        # self.current_time = datetime.datetime.now()
        self.schedule = schedule
        self.time_option = time_option
        self.time_unit = 0

        self.time_options = {
            # 'H': self.current_time.hour,
            'M': self.minute_option,
            # 'S': self.current_time.second
        }
        super().__init__(input_time)

    def process_time(self, validated_time):
        try:
            time_function = self.time_options.get(self.time_option)
            if not time_function() or not self.check_schedule():
                self.app_service_output = False
            else:
                self.app_service_output = True
            pass
        except KeyError as e:
            self.status = "Invalid schedule option!"


