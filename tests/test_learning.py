import pytest

from simulation import run_simulation, SimulationResult


def test_run_simulation_returns_expected_metrics():
    result = run_simulation(runs=20, seed=123, verbose=False)

    assert isinstance(result, SimulationResult)
    d = result.as_dict()
    assert set(d) >= {
        "pdr_aco",
        "pdr_base",
        "pdr_greedy",
        "lat_aco",
        "lat_base",
        "lat_greedy",
        "red_aco",
        "red_base",
        "red_greedy",
        "packets_sent",
        "packets_received_aco",
        "packets_received_baseline",
        "packets_received_greedy",
    }
    assert 0 <= result.pdr_aco <= 1
    assert 0 <= result.pdr_base <= 1
    assert 0 <= result.pdr_greedy <= 1
    assert result.lat_aco >= 0
    assert result.lat_base >= 0
    assert result.red_aco >= 0
    assert result.red_base >= 0
    assert result.packets_sent == 20 * 6


def test_run_simulation_is_repeatable_with_seed():
    first = run_simulation(runs=20, seed=123, verbose=False)
    second = run_simulation(runs=20, seed=123, verbose=False)

    assert first.as_dict() == second.as_dict()


def test_run_simulation_returns_per_iteration_history():
    result = run_simulation(runs=30, seed=42, verbose=False)

    assert len(result.history) == 30
    for h in result.history:
        assert 0 <= h.pdr_aco <= 1
        assert 0 <= h.pdr_base <= 1
        assert 0 <= h.pdr_greedy <= 1


def test_simulation_survives_total_failure():
    """At high failure rate, ACO should still outperform the static baseline."""
    result = run_simulation(runs=50, failure_rate=1.0, seed=42, verbose=False)
    # The static baseline is more fragile than ACO under heavy failures.
    assert result.pdr_aco >= result.pdr_base


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
