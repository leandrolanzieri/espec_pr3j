class SettingError(Exception):
    """
    An error occurred when sending a setting command to the environmental chamber.
    """

    pass


class MonitorError(Exception):
    """
    An error occurred when sending a monitor command to the environmental chamber.
    """

    pass
