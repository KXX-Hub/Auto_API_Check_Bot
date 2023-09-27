import requests
import utilities as utils

config = utils.read_config()
token = config.get('line_notify_token')


def send_message(message):
    """Send a message via LINE Notify.
    :param str message: Message to send.
    :return: None
    """
    headers = {"Authorization": "Bearer " + token}
    data = {'message': message}
    requests.post("https://notify-api.line.me/api/notify",
                  headers=headers, data=data, timeout=5)
