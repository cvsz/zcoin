from app.strategy import compare_strategies, monte_carlo_null, walk_forward_bias_strategy


def test_paper_tools_only_compute_simulations():
    values = [0,1]*300
    assert len(compare_strategies(values)) == 7
    assert walk_forward_bias_strategy(values, train_window=100, min_edge=.10)["report"]["trades"] == 0
    result = monte_carlo_null(100, simulations=100)
    assert result["simulations"] == 100
