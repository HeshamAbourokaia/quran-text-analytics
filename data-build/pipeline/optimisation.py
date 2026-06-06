# -*- coding: utf-8 -*-
"""Decision modelling (MIS775) applied to the Qur'an.

Hifz Plan Optimiser - a linear program for a memorisation schedule:

  Decision variables:
    N = new lines memorised per day
    R = review lines per day
  Maximise N   (finish sooner)
  subject to
    t_new*N + t_rev*R <= D        (daily minutes budget)
    R - rho*N >= 0                (retention: review >= rho x new intake)
    N, R >= 0

Solved with scipy.optimize.linprog (HiGHS) to demonstrate the LP machinery and
extract the shadow price (dual value) of the daily-budget constraint, exactly
like the MIS775 portfolio model. The closed-form optimum is also emitted so the
UI can re-solve instantly as the user changes the budget.
"""
from scipy.optimize import linprog

DEFAULT = dict(tNew=4.0, tRev=0.5, rho=10.0, dailyMinutes=60.0, totalLines=9060)
# totalLines: 604-page Madani Mushaf x 15 lines (standard count)

def solve(tNew, tRev, rho, D):
    # variables x = [N, R]; minimise -N
    c = [-1.0, 0.0]
    A_ub = [[tNew, tRev],     # time budget <= D
            [rho, -1.0]]       # rho*N - R <= 0  (i.e. R >= rho*N)
    b_ub = [D, 0.0]
    res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=[(0, None), (0, None)], method='highs')
    N, R = res.x
    # shadow price of the budget row = how many extra new-lines/day per extra minute
    shadow = float(-res.ineqlin.marginals[0]) if res.ineqlin is not None else None
    return N, R, shadow

def build(params=None):
    p = dict(DEFAULT)
    if params:
        p.update(params)
    N, R, shadow = solve(p['tNew'], p['tRev'], p['rho'], p['dailyMinutes'])
    days = p['totalLines'] / N if N > 0 else None
    grid = []
    for D in [20, 30, 45, 60, 90, 120, 180]:
        n, r, _ = solve(p['tNew'], p['tRev'], p['rho'], D)
        grid.append({'dailyMinutes': D, 'newLinesPerDay': round(n, 2),
                     'daysToFinish': round(p['totalLines'] / n, 0) if n > 0 else None})
    return {
        'params': p,
        'solution': {
            'newLinesPerDay': round(N, 3),
            'reviewLinesPerDay': round(R, 2),
            'daysToFinish': round(days, 0) if days else None,
            'monthsToFinish': round(days / 30.0, 1) if days else None,
        },
        # value of one extra minute/day, in new-lines/day (the budget shadow price)
        'shadowPriceMinute': round(shadow, 4) if shadow is not None else None,
        'sensitivity': grid,
        'note': 'Lines = 604-page Madani Mushaf x 15. Review ratio rho = review lines per new line to retain.',
    }

if __name__ == '__main__':
    import json
    print(json.dumps(build(), indent=2))
