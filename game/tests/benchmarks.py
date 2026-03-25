"""Benchmark leaders for comparison against our AdaptiveLeader."""
import numpy as np


class NaiveLeader(Leader):
    """Uses historical mean u_F, computes Stackelberg optimal. No exploration."""
    def __init__(self, name, engine):
        super().__init__(name, engine)
        self.opt_price = 11.0

    def start_simulation(self):
        uFs = [self.get_price_from_date(t)[1] for t in range(1, 101)]
        mean_uF = np.mean(uFs)
        self.opt_price = (105 + 3 * mean_uF) / 10

    def new_price(self, date):
        return self.opt_price
