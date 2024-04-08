from flask import Flask, make_response
import threading
from http.client import responses

app = Flask(__name__)

status = 200
retry_after = 0


def test():
    global status
    global retry_after
    while True:
        numbers = [int(user_input) for user_input in input().split()]
        status = numbers[0]
        retry_after = numbers[1] if len(numbers) > 1 else 0

        # if e == "504":  # gateway timeout
        #     status = 504
        # elif e == "429":  # client sending too many requests
        #     status = 429
        # elif e == "503":  # service temporarily unavailable
        #     status = 503
        # elif e == "200":
        #     status = 200

        print(status, retry_after)


@app.route("/")
def index():
    global status
    if status != 200:
        response = make_response(responses[status], status)
        if retry_after > 0:
            response.headers["Retry-After"] = retry_after  # The value is in seconds
        return response
    return "Hello"


if __name__ == "__main__":
    p1 = threading.Thread(target=app.run)
    p1.start()
    p2 = threading.Thread(target=test)
    p2.start()
    # test()
