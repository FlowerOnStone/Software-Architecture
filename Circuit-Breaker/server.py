from flask import Flask, abort
import threading

app = Flask(__name__)

status = 200


def test():
    global status
    while True:
        try:
            e = input()
        except Exception:
            return

        if e == "504":  # gateway timeout
            status = 504
        elif e == "429":  # client sending too many requests
            status = 429
        elif e == "503":  # service temporarily unavailable
            status = 503
        elif e == "200":
            status = 200

        print(status)


@app.route("/")
def index():
    global status
    if status != 200:
        abort(status)
    return "Hello"


if __name__ == "__main__":
    p1 = threading.Thread(target=app.run)
    p1.start()
    p2 = threading.Thread(target=test)
    p2.start()
    # test()
