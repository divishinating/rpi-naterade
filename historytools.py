from dateutil import parser


class HistoryCleanup(object):
    """
    Responsibilities:
    - Defines a single record type for temporary basals (instead of one each for rate and duration)
    - Adjusts temporary basal duration for cancelled basals
    - Converts square bolus records to temporary basal records
    - Deduplicates bolus wizard entries
    - Converts suspend and resume records to temporary basal records
    - Removes any records not in the start_datetime to end_datetime window
    """
    def __init__(self, pump_history, start_datetime=None, end_datetime=None):
        """Initializes a new instance of the Medtronic pump history cleanup parser

        :param pump_history: A list of pump history events, in reverse-chronological order
        :type pump_history: list(dict)
        :param start_datetime: The start time of history events. If not provided, the oldest record's timestamp is used
        :type start_datetime: datetime
        :param end_datetime: The end time of history events. If not provided, the latest record's timestamp is used
        :type end_datetime: datetime
        """
        self.clean_history = []

        if len(pump_history) > 0:
            if start_datetime is None:
                start_datetime = parser.parse(pump_history[-1]["timestamp"])

            if end_datetime is None:
                end_datetime = parser.parse(pump_history[0]["timestamp"])

        # Temporary parsing state
        self._boluswizard_events_by_body = defaultdict(list)
        self._resume_datetime = None
        self._temp_basal_duration = None
        self._last_temp_basal_event = None

        for event in pump_history:
            self.add_history_event(event)

        # The pump was suspended before the history window began
        if self._resume_datetime is not None:
            self.add_history_event({
                "_type": "PumpSuspend",
                "timestamp": start_datetime.isoformat()
            })

    def add_history_event(self, event):
        try:
            decoded = getattr(self, "_decode_{}".format(event["_type"].lower()))(event)
        except AttributeError:
            pass
        else:
            self.clean_history.extend(decoded or [])
