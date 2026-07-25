from engine.scoring import compute_score
from engine.cost import estimate_cost


def test_compute_score_perfect_dataset():
    breakdown = compute_score(0, 0, 0, 0, 0)
    assert breakdown.dataset_score == 100.0


def test_compute_score_penalizes_issues():
    breakdown = compute_score(50, 0, 0, 0, 0)
    assert breakdown.dataset_score < 100.0
    assert breakdown.component_scores["nulls"] == 50.0


def test_estimate_cost_zero_issues():
    result = estimate_cost(0, 0, 0, 0, 0)
    assert result.total_cost == 0.0


def test_estimate_cost_nonzero():
    result = estimate_cost(total_nulls=10, total_duplicate_rows=2, total_format_errors=1,
                            total_outliers=3, total_rule_violations=1)
    assert result.total_cost > 0
    assert result.breakdown["null_cost"] == 5.0
