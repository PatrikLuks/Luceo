from src.services.screening import score_audit


class TestAuditScoring:
    def test_low_risk_zeros(self):
        result = score_audit([0] * 10)
        assert result.total_score == 0
        assert result.risk_level == "low_risk"

    def test_low_risk_boundary(self):
        result = score_audit([4, 3, 0, 0, 0, 0, 0, 0, 0, 0])
        assert result.total_score == 7
        assert result.risk_level == "low_risk"

    def test_hazardous(self):
        result = score_audit([4, 4, 0, 0, 0, 0, 0, 0, 0, 0])
        assert result.total_score == 8
        assert result.risk_level == "hazardous"

    def test_hazardous_boundary(self):
        result = score_audit([4, 4, 4, 3, 0, 0, 0, 0, 0, 0])
        assert result.total_score == 15
        assert result.risk_level == "hazardous"

    def test_harmful(self):
        result = score_audit([4, 4, 4, 4, 0, 0, 0, 0, 0, 0])
        assert result.total_score == 16
        assert result.risk_level == "harmful"

    def test_harmful_boundary(self):
        result = score_audit([4, 4, 4, 4, 3, 0, 0, 0, 0, 0])
        assert result.total_score == 19
        assert result.risk_level == "harmful"

    def test_possible_dependence(self):
        result = score_audit([4, 4, 4, 4, 4, 0, 0, 0, 0, 0])
        assert result.total_score == 20
        assert result.risk_level == "possible_dependence"

    def test_max_score(self):
        result = score_audit([4, 4, 4, 4, 4, 4, 4, 4, 4, 4])
        assert result.total_score == 40
        assert result.risk_level == "possible_dependence"

    def test_recommendation_not_empty(self):
        result = score_audit([0] * 10)
        assert len(result.recommendation_cs) > 0
        assert len(result.recommendation_en) > 0

    def test_wrong_count_raises(self):
        import pytest

        with pytest.raises(ValueError):
            score_audit([0] * 9)
