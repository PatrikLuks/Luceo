from src.core.guardrails import SAFE_FALLBACK, check_response_guardrails


class TestGuardrails:
    def test_safe_response(self):
        is_safe, reason = check_response_guardrails(
            "Rozumím, že máš těžké období. Zkusme techniku dýchání."
        )
        assert is_safe is True
        assert reason is None

    def test_detects_icd10_code(self):
        is_safe, reason = check_response_guardrails(
            "Tvá diagnóza je F10.2, závislost na alkoholu."
        )
        assert is_safe is False
        assert reason is not None

    def test_detects_medication_name(self):
        is_safe, reason = check_response_guardrails(
            "Doporučuji ti naltrexon na snížení chutí."
        )
        assert is_safe is False

    def test_detects_dosage(self):
        is_safe, reason = check_response_guardrails(
            "Užívej 50 mg denně."
        )
        assert is_safe is False

    def test_detects_diagnostic_language(self):
        is_safe, reason = check_response_guardrails(
            "Jsi alkoholik a potřebuješ léčbu."
        )
        assert is_safe is False

    def test_detects_jsi_zavisly(self):
        is_safe, reason = check_response_guardrails(
            "Myslím, že jsi závislý na alkoholu."
        )
        assert is_safe is False

    def test_safe_fallback_exists(self):
        assert len(SAFE_FALLBACK) > 0
        assert "lékaře" in SAFE_FALLBACK
