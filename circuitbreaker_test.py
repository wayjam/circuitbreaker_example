import unittest
import time

from circuitbreaker import Open, HalfOpen, Closed, CircuitBreaker, CircuitBreakerOptions, State


class TestCircuitBreaker(unittest.TestCase):
    def test_transition(self):
        # initial state: closed
        cb = Closed(
            "tester",
            CircuitBreakerOptions(
                timeout=1,
                halfopen_timeout=1,
                open_timeout=1,
                failure_to_open=10,
                halfopen_max_failure=5,
            ))

        self.assertEqual(cb.get_state(), State.CLOSED)

        for _ in range(10):
            cb.inc()

        self.assertEqual(cb.count, 10)
        self.assertEqual(cb.get_state(), State.CLOSED)
        cb.inc()

        # open
        self.assertEqual(cb.count, 0)
        self.assertEqual(cb.get_state(), State.OPEN)

        time.sleep(2)

        # halfopen
        self.assertEqual(cb.get_state(), State.HALF_OPEN)

        time.sleep(2)

        # return to closed
        self.assertEqual(cb.get_state(), State.CLOSED)


if __name__ == '__main__':
    unittest.main()
