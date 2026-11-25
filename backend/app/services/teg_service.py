class TEGExceededException(Exception):
    def __init__(self, teg: float):
        self.teg = teg
        super().__init__(f"TEG {teg:.2%} dépasse le plafond réglementaire de 24%")


def compute_teg(
    principal: float,
    monthly_payment: float,
    n_months: int,
    fees_rate: float = 0.0,
    insurance_rate: float = 0.0,
) -> float:
    """Compute the annual effective interest rate (TEG) using Newton-Raphson.

    The TEG is the annual rate i_a such that:
        principal + fees = sum(monthly_payment / (1 + i_m)^t, t=1..n)
    where i_a = (1 + i_m)^12 - 1.

    Raises TEGExceededException if teg_annual > 0.24 (24%).
    """
    fees = principal * fees_rate + principal * insurance_rate * n_months / 12
    adjusted_principal = principal + fees

    i = 0.01  # initial guess: 1% monthly
    for _ in range(100):
        pv = sum(monthly_payment / (1 + i) ** t for t in range(1, n_months + 1))
        f = pv - adjusted_principal
        df = -sum(t * monthly_payment / (1 + i) ** (t + 1) for t in range(1, n_months + 1))
        if abs(df) < 1e-12:
            break
        i = i - f / df
        if abs(f) < 1e-8:
            break

    teg_annual = (1 + i) ** 12 - 1
    if teg_annual > 0.24:
        raise TEGExceededException(teg_annual)
    return teg_annual
