class SettingError(Exception):
    """
    An error occurred when sending a setting command to the climate chamber.
    """

    pass


class MonitorError(Exception):
    """
    An error occurred when sending a monitor command to the climate chamber.
    """

    pass
