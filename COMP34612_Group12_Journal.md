# COMP34612 Group Project Journal

**Group:** 12  
**Project:** Adaptive Stackelberg Pricing under Imperfect Information  
**Submission item:** Group journal / written materials  

> The member labels below can be replaced with names before submitting on Blackboard.

## 1. Group Organisation and Task Distribution

### 1.1 Group Members

| Member | Main Responsibilities |
|---|---|
| Member 1 | Overall algorithm design, Stackelberg pricing derivation, final integration |
| Member 2 | Historical-data analysis, OLS/RLS implementation, parameter tuning |
| Member 3 | Testing framework, hidden-follower stress tests, performance evaluation |
| Member 4 | Presentation/journal preparation, literature links, Colab submission checks |

We used a multiple-leader submission structure:

| Leader | Intended Followers | Strategy Space |
|---|---|---|
| `AdaptiveLeader` | MK1, MK2, MK4, MK5 | `[1.00, +inf)` |
| `BoundedAdaptiveLeader` | MK3, MK6 | `[1.00, 15.00]` |

The code is deliberately compact and uses only `numpy`, so it can run within the free Google Colab environment and the 10-minute execution limit.

### 1.2 Initial Plan

At the start of the project we divided the work into four tracks:

1. Understand the game and derive the leader's objective after substituting a learned follower reaction function.
2. Build a baseline leader using the standard course method: estimate the reaction function from historical data using OLS, then compute the Stackelberg-optimal leader price.
3. Add online adaptation, because the project specification says follower parameters may change over time.
4. Test robustness against hidden variants, especially because the marking scheme explicitly says MK4, MK5, and MK6 are intended to expose hardcoding, invalid bounds, runtime errors, and poor generalisation.

The first version of the plan assumed that the standard OLS method would be nearly sufficient. Our main change of direction came after measuring how narrow the historical leader-price range was.

## 2. Progress Journal

### Week 7: Problem Understanding and Baseline

We started by reading the specification and identifying the core Stackelberg structure:

- The leader sets `u_L` first.
- The follower observes `u_L` and responds with `u_F`.
- The leader demand is `S_L(u_L, u_F) = 100 - 5u_L + 3u_F`.
- Daily profit is `(u_L - 1) * S_L`.
- The objective is accumulated profit over days 101-130.

Our first technical step was to model the follower's reaction as:

```text
u_F = alpha + beta * u_L
```

This follows the course treatment of imperfect-information Stackelberg games: learn a reaction function from historical data, then solve the induced leader optimisation problem.

Substituting the learned reaction into the leader profit gives:

```text
profit = (u_L - 1) * (100 - 5u_L + 3(alpha + beta*u_L))
```

Solving the first-order condition gives:

```text
u_L* = (105 + 3*alpha - 3*beta) / (10 - 6*beta)
```

This became the core of `_optimal_price()`.

### Baseline Result and First Difficulty

The naive OLS method was much weaker than expected. In our benchmark comparison it averaged about 85.3% of the benchmark, with MK1 and MK2 especially weak. The reason was not the algebra; it was the data.

The historical leader prices were concentrated in a very small interval, approximately:

```text
u_L in [1.72, 1.90]
```

However, the profitable prices for MK1 and MK2 were around `u_L ~= 20`, and for MK3 around `u_L ~= 11`. This meant the baseline was estimating a slope from a 0.18-wide interval and extrapolating far outside it. Small slope errors caused large pricing errors.

This was the key turning point of the project: our problem was not just "fit OLS"; it was "learn enough outside the historical range to make OLS reliable."

### Exploration Experiments

We then tested deliberate exploration on day 101. The idea was to sacrifice one day of profit to observe the follower response at a much more informative price. This connects to dual-control ideas: the leader's action must both earn profit and reveal information about the system.

| Version | Probe Price | Average Outcome | Decision |
|---|---:|---:|---|
| v1 | `u_L = 5` | 98.2% | Better than naive, but too conservative |
| v2 | `u_L = 10` | 99.3% | Large improvement |
| v4 | `u_L = 12` | 99.5% | Best cost-benefit balance |

We also tested a two-day probe. It gave a slightly more precise estimate but lost an additional exploitation day, so the total 30-day profit was worse. We kept a single day-101 probe.

### Online Learning: OLS and RLS

The specification says follower payoff parameters may change over time, so a one-off model fit was not enough. We tested:

- Pure OLS refitting
- Pure RLS updating
- A hybrid approach

The final design uses:

- batch OLS refitting early and every three days,
- recursive least squares between refits,
- forgetting factor `lambda = 0.97`.

We tried `lambda = 0.99`, but it retained too much old data and increased variance. We tried OLS-only, but it was less responsive. The hybrid approach gave the best balance between stability and adaptation.

### Time-Trend Detection

MK2-like behaviour appeared to have a time trend, so we added a simple trend detector:

```text
if abs(corr(date, u_F)) > 0.7:
    fit u_F = alpha + beta*u_L + gamma*t
```

This was useful because the marking scheme rewards evidence-based improvement rather than adding features without justification. The time regressor improved trending-follower performance while leaving stationary cases unchanged.

### Robustness and Hidden Followers

The hidden followers MK4, MK5, and MK6 are not directly available, so we built local stress tests to simulate possible changes:

- steeper and gentler linear slopes,
- different intercepts,
- time trends,
- negative trends,
- nonlinear square-root and logarithmic reactions,
- high noise,
- bounded `[1, 15]` cases,
- steep-slope edge cases.

This testing changed the implementation. For example, a very steep slope can make the denominator `10 - 6*beta` close to zero or negative. The original closed-form optimum then becomes unstable. We fixed this by ramping up gradually when the denominator is unsafe, instead of jumping to an invalid or extreme price.

We also added `BoundedAdaptiveLeader` for MK3/MK6 so the price is capped at 15. This directly addresses the marking-scheme warning about invalid bounds.

### Colab and Submission Readiness

The final notebook sets `group_num = 12`, documents the leader mapping, includes only `numpy` as the project dependency, and can use the included `comp34612.zip` from a cloned repository. We also cleaned saved notebook outputs and widget state so GitHub can render the notebook and a marker can inspect it.

## 3. Technical Method Summary

The final leader performs the following steps:

1. Load historical prices for days 1-100 with `get_price_from_date()`.
2. Filter major follower-price outliers using median absolute deviation.
3. Detect whether the follower has a time trend.
4. Fit a reaction model using OLS.
5. On day 101, probe at `u_L = 12`, respecting the `[1,15]` bound for MK3/MK6.
6. From day 102 onward, update the model using OLS refits and RLS updates.
7. Compute the Stackelberg-optimal price with safety bounds.

The final implementation is intentionally simple:

- no hardcoded follower parameters,
- no dependency beyond `numpy`,
- no long-running simulation or training,
- direct use of historical and online observations,
- separate bounded/unbounded classes for the required strategy spaces.

## 4. Evidence and Evaluation

### 4.1 Baseline Comparison

| Leader | MK1 | MK2 | MK3 | Average |
|---|---:|---:|---:|---:|
| Naive OLS leader | 81.1% | 75.4% | 99.5% | 85.3% |
| Final adaptive leader | 99.2% | 99.4% | 100.0% | 99.5% |

The largest gain came from exploration. This supports our conclusion that the central issue was the narrow historical price range.

### 4.2 Final Performance Summary

| Follower | Test Profit | Approx. Benchmark Percentage |
|---|---:|---:|
| MK1 | 28,841 | 99.2% |
| MK2 | 31,571 | 99.4% |
| MK3 | 16,030 | 100.0% |

We also ran repeated MARK-mode style testing during development. Across repeated runs, the average stayed close to 99%, which gave us confidence that the method was not relying on one lucky deterministic run.

### 4.3 Runtime

The leader code is very fast. Local timing on mock followers showed one complete 30-day decision run taking less than 0.001 seconds. The real engine and Colab startup dominate runtime, not our algorithm. This is comfortably within the 10-minute limit.

## 5. Key Decisions and Rationale

| Decision | Rationale | Evidence |
|---|---|---|
| Use OLS as the base model | Matches lecture method and linear demand structure | Good model fit after exploration |
| Add day-101 exploration | Historical prices were too narrow for reliable extrapolation | Average rose from 85.3% to about 99% |
| Probe at `u_L = 12` | Informative but still valid for `[1,15]` bounded followers | Better than probes at 5 or 10 |
| Use OLS + RLS hybrid | Need both stability and adaptation | OLS-only and pure RLS were weaker |
| Use `lambda = 0.97` | Good balance between old and new data | `lambda = 0.99` increased variance |
| Add time-trend detection | Handles changing follower parameters | Improved MK2-like cases |
| Add bounded leader | Required for MK3/MK6 strategy space | Prevents invalid prices |
| Keep implementation compact | Colab runtime and reliability matter | No unnecessary dependencies |

## 6. Difficulties and How We Overcame Them

### Narrow Historical Data

The most important difficulty was that the historical leader prices were too clustered. A standard OLS model looked reasonable on historical data but failed when extrapolated. We overcame this by adding deliberate exploration.

### Balancing Exploration and Exploitation

Exploration improves learning but costs profit. The two-day probe experiment showed that more information is not always better. We kept the one-day probe because the remaining 29 days are more valuable for exploitation.

### Time-Varying Followers

The project specification warned that parameters may change over time. We first tried a stationary model, then added a time regressor only when the data showed a strong trend. This avoided overcomplicating stationary cases while improving trending cases.

### Hidden-Follower Robustness

Because MK4-MK6 are hidden, we could not optimise directly against them. Instead, we designed stress tests that changed slopes, trends, noise, and functional forms. This led to safer pricing logic and a bounded class for MK3/MK6.

### Colab Compatibility

The final submission had to be inspectable and runnable in Colab. We cleaned the notebook, removed unnecessary generated artifacts, included the required zip directly, and avoided nonstandard dependencies.

## 7. Reflection

### What Went Well

The strongest part of our project was the evidence-driven development process. We did not simply add complexity; we tested each idea and removed or reverted changes that did not improve performance. The day-101 probe was a small change, but it was strongly justified by the data and produced the largest improvement.

The final method also generalises well because it learns the reaction function from each follower's historical data instead of hardcoding follower-specific parameters.

### What Went Badly

We spent too much time exploring more complex methods before fully quantifying the value of simpler probes. Thompson Sampling was interesting theoretically, but in this setting it did not improve performance over a deterministic probe. If we repeated the project, we would prototype high-risk ideas earlier and reject weak ones faster.

We also initially underestimated how important Colab/notebook packaging would be. A good algorithm is not enough if the submitted notebook cannot be rendered or run cleanly.

### What We Would Do Differently

With another chance, we would:

- create the stress-test suite earlier,
- track meeting notes more systematically from the first week,
- run every feature through a fixed ablation table before keeping it,
- test notebook submission and GitHub rendering earlier,
- compare more nonlinear reaction models for MK3-like followers.

### Work We Would Do With More Time

Future work could include:

- a principled regret analysis of the one-day probe,
- adaptive probe selection based on uncertainty,
- nonlinear model selection for bounded followers,
- automatic detection of whether a follower is bounded,
- confidence intervals for the estimated optimal price.

## 8. Feedback on the Coursework Style

The project was effective because it forced us to connect theory to a working system. The hidden followers are valuable because they discourage hardcoding and reward robust learning. However, it would be helpful if the project materials included a clearer final submission checklist, especially for the notebook, required zip file, README/leader mapping, and journal submission.

## 9. Contribution Summary

The marking scheme says no separate unequal-contribution email is needed if contributions were roughly even. The table below records an equal-contribution assumption; edit it before submission if that is not accurate.

| Member | Contribution Percentage | Main Contributions |
|---|---:|---|
| Member 1 | 25% | Algorithm design, Stackelberg pricing derivation, final integration |
| Member 2 | 25% | Historical-data analysis, OLS/RLS implementation, parameter tuning |
| Member 3 | 25% | Testing framework, hidden-follower stress tests, performance evaluation |
| Member 4 | 25% | Presentation/journal preparation, literature links, Colab submission checks |

## 10. Final Statement

Our final approach is an adaptive Stackelberg pricing leader based on course methods, extended with evidence-driven exploration, online updating, trend detection, and robustness checks. The most important lesson was that textbook OLS is not enough when the historical data covers only a tiny part of the price space. By using one carefully chosen probe and then exploiting the learned reaction function, we achieved high performance while keeping the implementation simple, fast, and Colab-compatible.
