from enum import Enum
import requests
import time
from http.client import responses
from threading import Timer


class CircuitBreakerStateEnum(Enum):
    CLOSE = 0
    HALF_OPEN = 1
    OPEN = 2


class CircuitBreakerStateStore:
    def __init__(self) -> None:
        self.state = CircuitBreakerStateEnum.CLOSE
        self.last_state_changed_date_utc = time.time_ns()
        self.last_exception = 0
        # for the live demo
        self.state_changed = False

    def trip(self, exception) -> None:
        self.last_exception = exception
        self.last_state_changed_date_utc = time.time_ns()
        self.state = CircuitBreakerStateEnum.OPEN
        # for the live demo
        self.state_changed = True

    def reset(self) -> None:
        self.state = CircuitBreakerStateEnum.CLOSE
        # for the live demo
        self.state_changed = True

    def half_open(self) -> None:
        self.state = CircuitBreakerStateEnum.HALF_OPEN
        # for the live demo
        self.state_changed = True

    def is_close(self) -> bool:
        return self.state == CircuitBreakerStateEnum.CLOSE

    def is_open(self) -> bool:
        return self.state == CircuitBreakerStateEnum.OPEN

    def is_half_open(self) -> None:
        return self.state == CircuitBreakerStateEnum.HALF_OPEN


class CircuitBreaker:
    def __init__(self) -> None:
        self.state_store = CircuitBreakerStateStore()
        self.open_to_half_open_wait_time = 5 * 10**9  # 5 seconds
        self.failure_counter = 0
        self.success_counter = 0
        self.failure_threshold = 5
        self.success_threshold = 5
        self.failure_interval = 10  # 10 seconds
        self.reset_timer = None
        self.start_failure_count_reset_timer()

    def start_failure_count_reset_timer(self):
        if self.reset_timer is not None:
            self.reset_timer.cancel()
        self.reset_timer = Timer(self.failure_interval, self.reset_failure_count)
        self.reset_timer.start()

    def reset_failure_count(self):
        self.failure_counter = 0
        self.start_failure_count_reset_timer()

    def is_close(self) -> bool:
        return self.state_store.is_close()

    def is_open(self) -> bool:
        return self.state_store.is_open()

    def is_half_open(self) -> bool:
        return self.state_store.is_half_open()

    def action(self) -> int:
        request = requests.get("http://127.0.0.1:5000")
        return request.status_code

    def execute_action(self):
        if self.is_open():
            if (
                self.state_store.last_state_changed_date_utc
                + self.open_to_half_open_wait_time
                < time.time_ns()
            ):
                self.state_store.half_open()
                print("Circuit Breaker has entered HALF-OPEN state")
                self.success_counter = 0
            else:
                raise Exception("Request not allowed (Circuit Breaker is Open).")
        if self.is_half_open():
            status = self.action()
            if status != 200:
                self.track_exception(status)
                raise Exception(f"Error: {status} {responses[status]}")
            else:
                self.success_counter += 1
                if self.success_counter == self.success_threshold:
                    self.failure_counter = 0
                    self.state_store.reset()
                    self.start_failure_count_reset_timer()
                return

        status = self.action()
        if status != 200:
            self.failure_counter += 1
            if self.failure_counter == self.failure_threshold:
                self.track_exception(status)
            raise Exception(f"Error: {status} {responses[status]}")
        # else:
        # self.failure_counter = 0

    def track_exception(self, status) -> None:
        self.state_store.trip(status)


if __name__ == "__main__":
    circuit_breaker = CircuitBreaker()
    while True:
        try:
            circuit_breaker.execute_action()
            print("Request successfully: 200 OK")
        except Exception as e:
            print(e)

        if circuit_breaker.state_store.state_changed:
            if circuit_breaker.is_close():
                print("Circuit Breaker has been reset to CLOSED state")
            elif circuit_breaker.is_open():
                print("Circuit Brealer has entered OPEN state")
            circuit_breaker.state_store.state_changed = False

        time.sleep(1)
