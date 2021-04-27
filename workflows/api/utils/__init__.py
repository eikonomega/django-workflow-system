from datetime import datetime
import pytz


def convert_to_utc_time(time, time_format):
    """
    This function is to translate a time submitted with an offset into
    the UTC representation of that time.

    Parameters
    ----------
    time: The time submitted from the mobile app
    time_format: The format to be used to translate
    """
    datetime_object = datetime.strptime(time, time_format)

    utc_time = datetime_object.astimezone(pytz.timezone("UTC"))

    return utc_time.strftime("%H:%M:%S")
