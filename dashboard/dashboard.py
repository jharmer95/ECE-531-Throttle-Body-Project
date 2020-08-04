"""Flask app for viewing and interacting with the controller"""

__author__ = "Jackson Harmer"
__copyright__ = "Copyright (c) 2020 Jackson Harmer. All rights reserved."
__license__ = "MIT"
__version__ = "0.1"

from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import atexit, threading, os.path, signal, sys

# Add controller directory to import path
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.path.pardir, "controller")
    )
)
from controller import Controller
import simple_i2c as si2c

# Globals
CONTROLLER_OBJ: Controller = None
CONTROLLER_THREAD: threading.Thread = None


def app_cleanup(sig, frame):
    global CONTROLLER_OBJ
    global CONTROLLER_THREAD

    print("Closed by user!")
    if CONTROLLER_OBJ != None:
        CONTROLLER_OBJ.cleanup()
    if CONTROLLER_THREAD != None:
        CONTROLLER_THREAD.join()
    exit(0)


app = Flask(__name__)
app.config["SECRET_KEY"] = "kCUs9h7KhTCZK6kSmfEUL8Ao"
socketio = SocketIO(app)
signal.signal(signal.SIGINT, app_cleanup)


def busFunc():
    global CONTROLLER_OBJ

    si2c.init_bus(1)
    CONTROLLER_OBJ.simulate()
    si2c.close_bus()


@app.before_first_request
def activate_job():
    global CONTROLLER_OBJ
    global CONTROLLER_THREAD

    CONTROLLER_OBJ = Controller()
    CONTROLLER_THREAD = threading.Thread(target=busFunc)
    CONTROLLER_THREAD.start()


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("my event")
def hello_world():
    global CONTROLLER_OBJ

    data = {}
    data["cruise_on"] = CONTROLLER_OBJ.get_cruise_control_status()
    data["cruise_speed"] = 0
    if data["cruise_on"]:
        data["cruise_speed"] = CONTROLLER_OBJ.get_cruise_target_speed()
    data["vehicle_speed"] = CONTROLLER_OBJ.update_speed()
    data["accelerator"] = CONTROLLER_OBJ.get_accelerator_position() * 100.00
    data["throttle"] = CONTROLLER_OBJ.get_throttle_body() / 90.00 * 100.00
    data["maf"] = CONTROLLER_OBJ.get_maf_value()
    emit("my response", data)


@socketio.on("set data")
def set_data(mesg):
    global CONTROLLER_OBJ

    accel_val = float(mesg[0]["value"]) / 100.00
    cruise_enable = mesg[1]["value"] == "true"
    cruise_speed = int(mesg[2]["value"])

    if cruise_enable:
        CONTROLLER_OBJ.set_cruise_target_speed(cruise_speed)
        CONTROLLER_OBJ.set_cruise_control_status(True)
    else:
        CONTROLLER_OBJ.set_accelerator_position(accel_val)
        CONTROLLER_OBJ.set_cruise_control_status(False)


if __name__ == "__main__":
    socketio.run(app)
