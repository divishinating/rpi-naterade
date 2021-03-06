from datetime import timedelta
from flask import Flask
from flask import render_template

from glucodyn import GlucoDynEventHistory
import pump

app = Flask(__name__, static_url_path='')


@app.route("/")
def glucodyn():
    """Renders a GlucoDyn prediction graph from the current pump settings and recent history"""
    bginitial, pump_datetime = pump.glucose_level_at_datetime(pump.clock_datetime())

    # Glucodyn template data
    settings = {
        "pump_time_string": pump_datetime.strftime('%I:%M:%S %p'),
        "cratio": pump.carb_ratio_at_time(pump_datetime.time()),
        "sensf": pump.insulin_sensitivity_at_time(pump_datetime.time()),
        "idur": pump.insulin_action_curve(),
        "bginitial": bginitial,
        "stats": 1,
        "inputeffect": 1
    }

    max_carb_absorption = 4
    settings["simlength"] = max(settings["idur"], max_carb_absorption)
    history_start_datetime = pump_datetime - timedelta(hours=settings["simlength"])

    history = GlucoDynEventHistory(
        pump.history_in_range(
            history_start_datetime,
            pump_datetime
        ),
        pump.basal_schedule(),
        zero_datetime=pump_datetime,
        sim_hours=settings["simlength"]
    )

    return render_template(
        'glucodyn.html',
        userdata=settings,
        cache_info=pump.cache_info(),
        history=history
    )

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')
