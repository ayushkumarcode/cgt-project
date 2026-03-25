"""Stackelberg pricing game leaders."""
import numpy as np


class AdaptiveLeader(Leader):
    """Adaptive leader with exploration + RLS."""

    UPPER_BOUND = float('inf')

    def __init__(self, name, engine):
        super().__init__(name, engine)
        self.hist_uL = []
        self.hist_uF = []
        self.alpha = 0.0
        self.beta = 0.0
        self.sigma2 = 1.0
        self.P = np.eye(2) * 100.0
        self.lam = 0.97
