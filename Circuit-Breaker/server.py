from flask import Flask, abort, redirect, url_for
import threading

app = Flask(__name__)

status = 0


def test():
    global status
    while True:
        e = input()

        print(e)
        if e == "E":
            status = 500
        else:
            status = 200


@app.route("/")
def index():
    global status
    if status == 500:
        abort(500)
    return "Hello"


if __name__ == "__main__":
    p1 = threading.Thread(target=app.run)
    p1.start()
    p2 = threading.Thread(target=test)
    p2.start()
    # test()
