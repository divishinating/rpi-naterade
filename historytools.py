from dateutil import parser


class HistoryCleanup(object):
    """
    Responsibilities:
    - Defines a single record type for temporary basals (instead of one each for rate and duration)
    - Adjusts temporary basal duration for cancelled basals
    - Converts square bolus records to temporary basal records
    - Deduplicates bolus wizard entries
    - Converts suspend and resume records to temporary basal records
    """
    def __init__(self, pump_history, start_datetime=None, end_datetime=None):
        self.clean_history = []

        if len(pump_history) > 0:
            if start_datetime is None:
                start_datetime = parser.parse(pump_history[-1]["timestamp"])

            if end_datetime is None:
                end_datetime = parser.parse(pump_history[0]["timestamp"])
