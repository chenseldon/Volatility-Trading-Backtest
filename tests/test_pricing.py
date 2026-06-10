import math

import pytest

from volbacktest.pricing import black_scholes


def test_black_scholes_respects_put_call_parity() -> None:
    call = black_scholes(100, 100, 0.5, 0.03, 0.01, 0.2, "call")
    put = black_scholes(100, 100, 0.5, 0.03, 0.01, 0.2, "put")

    parity = 100 * math.exp(-0.01 * 0.5) - 100 * math.exp(-0.03 * 0.5)
    assert call.price - put.price == pytest.approx(parity, rel=1e-8)
    assert 0 < call.delta < 1
    assert -1 < put.delta < 0
    assert call.vega > 0
