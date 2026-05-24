import pytest

from simulation import run_simulation


def test_run_simulation_returns_expected_metrics():
    result = run_simulation(runs=20, seed=123, verbose=False)

    assert set(result) >= {
        "pdr_aco",
        "pdr_base",
        "lat_aco",
        "lat_base",
        "red_aco",
        "red_base",
        "packets_sent",
        "packets_received_aco",
        "packets_received_baseline",
    }
    assert 0 <= result["pdr_aco"] <= 1
    assert 0 <= result["pdr_base"] <= 1
    assert result["lat_aco"] >= 0
    assert result["lat_base"] >= 0
    assert result["red_aco"] >= 0
    assert result["red_base"] >= 0
    assert result["packets_sent"] == 20 * 6


def test_run_simulation_is_repeatable_with_seed():
    first = run_simulation(runs=20, seed=123, verbose=False)
    second = run_simulation(runs=20, seed=123, verbose=False)

    assert first == second


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"runs": -1}, "runs"),
        ({"failure_rate": -0.1}, "failure_rate"),
        ({"failure_rate": 1.1}, "failure_rate"),
        ({"congestion_factor": 0.9}, "congestion_factor"),
    ],
)
def test_run_simulation_rejects_invalid_inputs(kwargs, message):
    with pytest.raises(ValueError, match=message):
        run_simulation(**kwargs, verbose=False)
