from app.advanced_stats import bh_fdr, holdout_split, transition_matrix
from app.stats import edge_assessment, nonce_audit


def test_symmetric_edge_gate():
    zero = edge_assessment([0]*6000 + [1]*4000)
    one = edge_assessment([1]*6000 + [0]*4000)
    assert zero["favored_side"] == 0 and zero["positive_edge_evidence"]
    assert one["favored_side"] == 1 and one["positive_edge_evidence"]


def test_integrity_helpers():
    assert nonce_audit([1,2,2,4])["duplicates"] == [2]
    assert holdout_split(list(range(10)), .7)["holdout"] == [7,8,9]
    assert transition_matrix([0,1,0,1])["counts"]["01"] == 2
    assert 0 in bh_fdr([.001,.2,.9])["discoveries"]
