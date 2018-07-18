import datetime


def convert_datetime_string(input_time):
    try:
        validated_time = datetime.datetime.strptime(
            input_time.rstrip(),
            "%d/%m/%Y %H:%M:%S"
        )
        return validated_time

    except ValueError:
        # exit with status code
        return False


def convert_datetime_string_part2(
        input_time,
        logger,
        time_format="%H:%M:%S"
):
    try:
        validated_time = datetime.datetime.strptime(
            input_time.rstrip(),
            time_format
        )
        return True

    except ValueError as e:
        # exit with status code
        logger.error(e)
        return False
