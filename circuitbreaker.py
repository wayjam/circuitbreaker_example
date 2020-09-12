#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from enum import Enum
from time import time


class State(Enum):
    OPEN = 'open'
    CLOSED = 'closed'
    HALF_OPEN = 'halfopen'


class CircuitBreakerOptions:
    Timeout = 0
    Open_Timeout = 0
    HalfOpen_Timeout = 0

    Failure_To_Open = 0
    HalfOpen_Max_Failure = 0

    def __init__(self, **kwargs):
        self.Timeout = kwargs.get('timeout', 0)
        self.Open_Timeout = kwargs.get("open_timeout", 0)
        self.HalfOpen_Timeout = kwargs.get("halfopen_timeout", 0)
        self.Failure_To_Open = kwargs.get("failure_to_open", 0)
        self.HalfOpen_Max_Failure = kwargs.get("halfopen_max_failure", 0)


class CircuitBreaker:
    state = None

    def __init__(self, name, options):
        self.name = name
        self.options = options
        self.initialize()

    @staticmethod
    def now():
        return int(time())

    def set_name(self, name):
        self.name = name

    def initialize(self):
        self.count = 0
        self.update = self.now()

    def inc(self):
        if self.is_expired:
            self.transition(State.CLOSED)
        self.count += 1

    def get_state(self):
        return self.state

    def transition(self, to):
        switch = {
            State.OPEN: Open,
            State.CLOSED: Closed,
            State.HALF_OPEN: HalfOpen,
        }
        self.__class__ = switch[to]
        self.initialize()

    @property
    def is_expired(self):
        if (self.now() - self.update) > self.get_duration_map()[self.state]:
            return True
        return False

    def get_duration_map(self):
        return {
            State.OPEN: (self.options.Timeout + self.options.HalfOpen_Timeout +
                         self.options.Open_Timeout),
            State.HALF_OPEN:
            (self.options.HalfOpen_Timeout + self.options.Timeout),
            State.CLOSED:
            self.options.Timeout,
        }


class Closed(CircuitBreaker):
    state = State.CLOSED

    def __init__(self, name, options):
        super().__init__(name, options)

    def inc(self):
        super().inc()
        if self.count > self.options.Failure_To_Open:
            self.transition(State.OPEN)


class Open(CircuitBreaker):
    state = State.OPEN

    def __init__(self, name, options):
        super().__init__(name, options)

    def inc(self):
        self.pre_check()
        self.count += 1

        if self.count > self.options.HalfOpen_Max_Failure:
            self.transition(State.OPEN)

    def get_state(self):
        self.pre_check()
        return self.state

    def pre_check(self):
        diff = self.now() - self.update
        if (diff > self.options.HalfOpen_Timeout + self.options.Timeout):
            self.transition(State.CLOSED)
        elif (self.now() - self.update) > self.options.Open_Timeout:
            self.transition(State.HALF_OPEN)
        else:
            pass


class HalfOpen(CircuitBreaker):
    state = State.HALF_OPEN

    def __init__(self, name, options):
        super().__init__(name, options)

    def inc(self):
        super().inc()
        if self.count > self.options.Failure_To_Open:
            self.transition(State.OPEN)

    def get_state(self):
        if (self.now() - self.update) > self.options.HalfOpen_Timeout:
            self.transition(State.CLOSED)
        return self.state
