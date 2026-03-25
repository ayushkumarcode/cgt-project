"""Mock engine for local testing without Docker."""
import gc
import numpy as np


class MockFollower:
    def response(self, date, u_L):
        raise NotImplementedError


class LinearFollower(MockFollower):
    def __init__(self, a=2.21, b=0.74, noise=0.55, seed=42):
        self.a, self.b, self.noise = a, b, noise
        self.rng = np.random.RandomState(seed)

    def response(self, date, u_L):
        return self.a + self.b * u_L + self.rng.normal(0, self.noise)


class TrendFollower(MockFollower):
    def __init__(self, a=1.69, b=0.80, trend=0.029, noise=0.26, seed=42):
        self.a, self.b, self.trend, self.noise = a, b, trend, noise
        self.rng = np.random.RandomState(seed)

    def response(self, date, u_L):
        return self.a + self.b * u_L + self.trend * date + self.rng.normal(0, self.noise)


class SqrtFollower(MockFollower):
    def __init__(self, a=0.44, b=0.69, noise=0.50, seed=42):
        self.a, self.b, self.noise = a, b, noise
        self.rng = np.random.RandomState(seed)

    def response(self, date, u_L):
        return self.a + self.b * np.sqrt(max(u_L, 0.01)) + self.rng.normal(0, self.noise)


class MockEngine:
    """Simulates the game engine for local testing."""

    def __init__(self, follower, hist_leader_prices=None):
        self.follower = follower
        self.prices = {}
        rng = np.random.RandomState(0)
        for t in range(1, 101):
            uL = 1.72 + rng.random() * 0.18 if hist_leader_prices is None else hist_leader_prices[t - 1]
            uF = follower.response(t, uL)
            self.prices[t] = (uL, uF)

    def exposed_get_price(self, date):
        return self.prices.get(date, (0.0, 0.0))
