# Standard Library
import logging
import signal
from random import randrange
from typing import Dict

# Third Party Libraries
import flask
from waitress.server import create_server  # type: ignore # (no typing supported)

# Local
import sacn_handler
from pubsub import PubSub


def create_app():
    app = flask.Flask(__name__)
    app.secret_key = "im_a_secret"
    pubsub = PubSub()

    def sacn_callback(data: Dict[int, Dict[str, int]]):
        for fixture_id, fixture in data.items():
            hex = "#{:02x}{:02x}{:02x}".format(
                fixture["red"], fixture["green"], fixture["blue"]
            )
            pubsub.publish(hex, f"fixture:{fixture_id+1}")

    sacn_handler.set_callback(sacn_callback)
    sacn_handler.start()

    def event_stream(fixture):
        for message in pubsub.listen(f"fixture:{fixture}"):
            yield f"data: {message}\n\n"

    @app.route("/login", methods=["GET", "POST"])
    def route_login():
        if flask.request.method == "POST":
            flask.session["fixture"] = flask.request.form["fixture"]
            return flask.redirect("/")
        return flask.render_template(
            "login.html", fixture_id=flask.session.get("fixture", 1)
        )

    @app.route("/stream")
    def route_stream():
        return flask.Response(
            event_stream(flask.session["fixture"]), mimetype="text/event-stream"
        )

    @app.route("/test")
    def route_test():
        return flask.render_template("test.html")

    @app.route("/")
    def home():
        if "fixture" not in flask.session:
            return flask.redirect("/login")
        return flask.render_template("main.html")

    return app


if __name__ == "__main__":
    # signal handler, to do something before shutdown service
    def handle_sig(sig, frame):
        logging.warning(f"Got signal {sig}, now close worker...")
        sacn_handler.stop()
        server.close()

    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, handle_sig)

    server = create_server(create_app(), host="0.0.0.0", port=8080, threads=12)
    server.run()
