"""Stackelberg pricing game leaders."""
import numpy as np


class _AdaptiveCore:
    """Core adaptive logic. Not a Leader subclass - won't appear in GUI."""

    UPPER_BOUND = float('inf')

    def _init_state(self):
        self.hist_uL, self.hist_uF = [], []
        self.alpha, self.beta, self.gamma = 0.0, 0.0, 0.0
        self.sigma2, self.lam = 1.0, 0.97
        self.P = np.eye(2) * 100.0
        self.all_uL, self.all_uF, self.all_dates = [], [], []
        self.use_time = False
        self.rmse = self.mape = self.r_squared = 0.0

    def start_simulation(self):
        for t in range(1, 101):
            uL, uF = self.get_price_from_date(t)
            self.hist_uL.append(uL)
            self.hist_uF.append(uF)
        self.all_uL = list(self.hist_uL)
        self.all_uF = list(self.hist_uF)
        self.all_dates = list(range(1, 101))
        self._filter_outliers()
        self._detect_time_trend()
        self._fit_ols()
        self._compute_metrics()

    def _filter_outliers(self):
        uF = np.array(self.hist_uF)
        med = np.median(uF)
        mad = np.median(np.abs(uF - med))
        if mad > 0:
            mask = np.abs(uF - med) < 10 * mad
            self.all_uL = list(np.array(self.hist_uL)[mask])
            self.all_uF = list(uF[mask])

    def _detect_time_trend(self):
        corr = np.corrcoef(np.arange(1, 101), self.hist_uF)[0, 1]
        if abs(corr) > 0.7:
            self.use_time = True

    def _fit_ols(self):
        uL, uF = np.array(self.all_uL), np.array(self.all_uF)
        X = np.column_stack([np.ones_like(uL), uL])
        if self.use_time:
            X = np.column_stack([X, np.array(self.all_dates)])
        theta = np.linalg.lstsq(X, uF, rcond=None)[0]
        self.alpha, self.beta = theta[0], theta[1]
        self.gamma = theta[2] if self.use_time else 0.0
        res = uF - X @ theta
        self.sigma2 = max(np.var(res), 1e-6)
        n = X.shape[1]
        self.P = np.linalg.inv(X.T @ X / self.sigma2 + np.eye(n) * 0.001)

    def _compute_metrics(self):
        uL, uF = np.array(self.all_uL), np.array(self.all_uF)
        pred = self.alpha + self.beta * uL
        if self.use_time:
            pred += self.gamma * np.array(self.all_dates)
        res = uF - pred
        self.rmse = np.sqrt(np.mean(res**2))
        self.mape = np.mean(np.abs(res) / np.maximum(np.abs(uF), 1e-6))
        self.r_squared = 1 - np.var(res) / max(np.var(uF), 1e-6)

    def _optimal_price(self, date=115):
        a = self.alpha + self.gamma * date
        b = self.beta
        denom = 10 - 6 * b
        if denom > 0.1:
            uL = (105 + 3 * a - 3 * b) / denom
        else:
            # beta >= 5/3: demand grows with u_L, ramp up gradually
            prev_uL = self.all_uL[-1] if self.all_uL else 12.0
            uL = prev_uL * 1.5  # 50% increase each day
        uL = max(1.01, min(uL, self.UPPER_BOUND))
        uF_pred = a + b * uL
        if 100 - 5 * uL + 3 * uF_pred < 5:
            uL = max(1.01, (95 + 3 * uF_pred) / 5)
        return min(uL, self.UPPER_BOUND)

    def _rls_update(self, uL, uF):
        x = np.array([1.0, uL])
        P2 = self.P[:2, :2] if self.P.shape[0] > 2 else self.P
        Px = P2 @ x
        gain = Px / (self.lam + x @ Px)
        theta = np.array([self.alpha, self.beta])
        theta += gain * (uF - (self.alpha + self.beta * uL))
        self.alpha, self.beta = theta[0], theta[1]
        self.P = (P2 - np.outer(gain, x @ P2)) / self.lam

    def new_price(self, date):
        if date > 101:
            prev_uL, prev_uF = self.get_price_from_date(date - 1)
            self.all_uL.append(prev_uL)
            self.all_uF.append(prev_uF)
            self.all_dates.append(date - 1)
            if date <= 105 or (date - 101) % 3 == 0:
                self._fit_ols()
            else:
                self._rls_update(prev_uL, prev_uF)
        if date == 101:
            return min(12.0, self.UPPER_BOUND)
        return self._optimal_price(date)


class AdaptiveLeader(_AdaptiveCore, Leader):
    """For MK1, MK2, MK4, MK5: unbounded strategy space [1, +inf)."""
    UPPER_BOUND = float('inf')
    def __init__(self, name, engine):
        Leader.__init__(self, name, engine)
        self._init_state()


class BoundedAdaptiveLeader(_AdaptiveCore, Leader):
    """For MK3, MK6: bounded strategy space [1, 15]."""
    UPPER_BOUND = 15.0
    def __init__(self, name, engine):
        Leader.__init__(self, name, engine)
        self._init_state()
