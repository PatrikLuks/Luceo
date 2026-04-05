from src.services.screening import AUDIT_QUESTIONS, score_audit


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


class TestAuditQ9Q10Validation:
    """Q9 and Q10 only accept values {0, 2, 4}, not 1 or 3."""

    def test_q9_q10_valid_values(self):
        """Valid option values for Q9 and Q10 are {0, 2, 4}."""
        q9_values = {o.value for o in AUDIT_QUESTIONS[8].options}
        q10_values = {o.value for o in AUDIT_QUESTIONS[9].options}
        assert q9_values == {0, 2, 4}
        assert q10_values == {0, 2, 4}

    def test_q9_value_1_not_in_options(self):
        """Value 1 is not a valid option for Q9."""
        q9_values = {o.value for o in AUDIT_QUESTIONS[8].options}
        assert 1 not in q9_values

    def test_q9_value_3_not_in_options(self):
        """Value 3 is not a valid option for Q9."""
        q9_values = {o.value for o in AUDIT_QUESTIONS[8].options}
        assert 3 not in q9_values
