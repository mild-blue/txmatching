import datetime


def get_formatted_now() -> str:
    now = datetime.datetime.now()
    return now.strftime('%Y_%m_%d_%H_%M_%S')
