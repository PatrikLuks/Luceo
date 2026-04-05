"""Unit tests for crisis detection — the most safety-critical module."""

from src.core.crisis import CrisisLevel, CrisisResult, detect_crisis, get_crisis_response, normalize_text


class TestNormalizeText:
    def test_strips_diacritics(self):
        assert normalize_text("Chci zemřít") == "chci zemrit"

    def test_lowercases(self):
        assert normalize_text("CHCI SE ZABÍT") == "chci se zabit"

    def test_collapses_whitespace(self):
        assert normalize_text("chci   se   zabít") == "chci se zabit"

    def test_empty_string(self):
        assert normalize_text("") == ""

    def test_strips_zero_width_characters(self):
        # Zero-width chars should be stripped to prevent keyword bypass
        assert normalize_text("sebe\u200Bvrazda") == "sebevrazda"
        assert normalize_text("chci\u200D zemrit") == "chci zemrit"
        assert normalize_text("\ufefftest") == "test"


class TestCriticalDetection:
    def test_chci_zemrit_with_diacritics(self):
        result = detect_crisis("Chci zemřít")
        assert result.level == CrisisLevel.CRITICAL

    def test_chci_zemrit_without_diacritics(self):
        result = detect_crisis("chci zemrit")
        assert result.level == CrisisLevel.CRITICAL

    def test_sebevrazda(self):
        result = detect_crisis("Přemýšlím o sebevraždě")
        assert result.level == CrisisLevel.CRITICAL

    def test_chci_se_zabit(self):
        result = detect_crisis("Chci se zabít, nemůžu dál")
        assert result.level == CrisisLevel.CRITICAL

    def test_nechci_zit(self):
        result = detect_crisis("Nechci žít")
        assert result.level == CrisisLevel.CRITICAL

    def test_english_suicide(self):
        result = detect_crisis("I want to kill myself")
        assert result.level == CrisisLevel.CRITICAL

    def test_english_want_to_die(self):
        result = detect_crisis("I want to die")
        assert result.level == CrisisLevel.CRITICAL

    def test_crisis_contacts_included(self):
        result = detect_crisis("Chci zemřít")
        assert len(result.crisis_contacts) > 0

    def test_matched_keywords_populated(self):
        result = detect_crisis("Chci zemřít")
        assert len(result.matched_keywords) > 0

    def test_zero_width_bypass_blocked(self):
        """Zero-width characters must not bypass crisis detection."""
        result = detect_crisis("sebe\u200Bvražda")
        assert result.level == CrisisLevel.CRITICAL


class TestHighDetection:
    def test_chci_si_ublizit(self):
        result = detect_crisis("Chci si ublížit")
        assert result.level == CrisisLevel.HIGH

    def test_predavkovat_se(self):
        result = detect_crisis("Chci se předávkovat")
        assert result.level == CrisisLevel.HIGH

    def test_self_harm(self):
        result = detect_crisis("I've been self-harming")
        assert result.level == CrisisLevel.HIGH


class TestMediumDetection:
    def test_chci_pit(self):
        result = detect_crisis("Chci pít, mám obrovský craving")
        assert result.level == CrisisLevel.MEDIUM

    def test_relaps(self):
        result = detect_crisis("Měl jsem relaps")
        assert result.level == CrisisLevel.MEDIUM

    def test_nema_to_smysl(self):
        result = detect_crisis("Nemá to smysl, nedokážu přestat")
        assert result.level == CrisisLevel.MEDIUM

    def test_beznadej(self):
        result = detect_crisis("Cítím takovou beznaděj")
        assert result.level == CrisisLevel.MEDIUM

    def test_fewer_contacts_for_medium(self):
        result = detect_crisis("Měl jsem relaps")
        assert len(result.crisis_contacts) <= 4


class TestNoneDetection:
    def test_normal_greeting(self):
        result = detect_crisis("Ahoj, jak se máš?")
        assert result.level == CrisisLevel.NONE

    def test_normal_question(self):
        result = detect_crisis("Kolik dní jsem střízlivý?")
        assert result.level == CrisisLevel.NONE

    def test_empty_message(self):
        result = detect_crisis("")
        assert result.level == CrisisLevel.NONE

    def test_positive_message(self):
        result = detect_crisis("Dnes je dobrý den, cítím se skvěle")
        assert result.level == CrisisLevel.NONE

    def test_no_contacts_for_none(self):
        result = detect_crisis("Normální zpráva")
        assert result.crisis_contacts == []


class TestCrisisResponse:
    def test_critical_response_includes_phone(self):
        result = detect_crisis("Chci zemřít")
        response = get_crisis_response(result)
        assert "116 123" in response
        assert "155" in response

    def test_high_response_includes_phone(self):
        result = detect_crisis("Chci si ublížit")
        response = get_crisis_response(result)
        assert "116 123" in response

    def test_medium_response_includes_phone(self):
        result = detect_crisis("Mám relaps")
        response = get_crisis_response(result)
        assert "800 350 000" in response

    def test_none_response_is_empty(self):
        result = detect_crisis("Ahoj")
        response = get_crisis_response(result)
        assert response == ""
