from enum import Enum
import requests
import time

class CircuitBreakerStateEnum(Enum):
    CLOSE = 0
    HALF_OPEN = 1
    OPEN = 2


class CircuitBreakerStateStore:
    def __init__(self) -> None:
        self.state = CircuitBreakerStateEnum.CLOSE
        self.last_state_changed_date_utc = time.time_ns()
        self.last_exception = 0

    def trip(self, exception) -> None:
        self.last_exception = exception
        self.last_state_changed_date_utc = time.time_ns()
        self.state = CircuitBreakerStateEnum.OPEN

    def reset(self) -> None:
        self.state = CircuitBreakerStateEnum.CLOSE

    def half_open(self) -> None:
        self.state = CircuitBreakerStateEnum.HALF_OPEN

    def is_close(self) -> bool:
        return self.state == CircuitBreakerStateEnum.CLOSE

    def is_open(self) -> bool:
        return self.state == CircuitBreakerStateEnum.OPEN

    def is_half_open(self) -> None:
        return self.state == CircuitBreakerStateEnum.HALF_OPEN


class CircuitBreaker:
    def __init__(self) -> None:
        self.state_store = CircuitBreakerStateStore()
        self.open_to_half_open_wait_time = 20000
        self.failure_counter = 0
        self.success_counter = 0
        self.failure_threshold = 5
        self.success_threshold = 5

    def is_close(self) -> bool:
        return self.state_store.is_close()

    def is_open(self) -> bool:
        return self.state_store.is_open()

    def is_half_open(self) -> bool:
        return self.state_store.is_half_open()

    def action (self) -> int:
        request = requests.get("http://127.0.0.1:5000")
        return request.status_code

    def execute_action(self):
        if self.is_open():
            if self.state_store.last_state_changed_date_utc + self.open_to_half_open_wait_time < time.time_ns():
                self.state_store.half_open()
                self.success_counter = 0
            else:
                raise Exception("Error 404")
        if self.is_half_open():
            status = self.action()
            if status == 404:
                self.track_exception(status)
                raise Exception("Error 404")
            else:
                self.success_counter += 1
                if self.success_counter == self.success_threshold:
                    self.failure_counter = 0
                    self.state_store.reset()
                return
        status = self.action()
        if status == 404:
            self.failure_counter += 1
            if self.failure_counter == self.failure_threshold: 
                self.track_exception(status)
            raise Exception("Error 404")
        else:
            self.failure_counter = 0

    def track_exception(self, status) -> None:
        self.state_store.trip(status)

if __name__ == "__main__":
    circuit_breaker = CircuitBreaker()
    while True:
        try:
            circuit_breaker.execute_action()
        except Exception as e:
            print(e)
        print(circuit_breaker.state_store.state)
        time.sleep(1)
