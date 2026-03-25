"""Mock engine for local testing without Docker."""
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
