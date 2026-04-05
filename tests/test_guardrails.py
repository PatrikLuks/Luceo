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

    # --- New tests: normalization bypass prevention ---

    def test_safe_fallback_passes_guardrails(self):
        """The safe fallback itself must not trigger any guardrail."""
        is_safe, reason = check_response_guardrails(SAFE_FALLBACK)
        assert is_safe is True, f"SAFE_FALLBACK triggers guardrail: {reason}"

    def test_detects_without_diacritics(self):
        """Guardrails must catch patterns even without Czech diacritics."""
        is_safe, _ = check_response_guardrails("Vase diagnoza je porucha zavislosti.")
        assert is_safe is False

    def test_detects_jsi_zavisla_feminine(self):
        """Feminine form must also be caught."""
        is_safe, _ = check_response_guardrails("Myslím, že jsi závislá na alkoholu.")
        assert is_safe is False

    def test_detects_jsi_alkoholicka_feminine(self):
        """Feminine alkoholicka must also be caught."""
        is_safe, _ = check_response_guardrails("Jsi alkoholička a potřebuješ pomoc.")
        assert is_safe is False

    def test_detects_baclofen(self):
        """New medication baclofen must be caught."""
        is_safe, _ = check_response_guardrails("Zkus baclofen na snížení chutí.")
        assert is_safe is False

    def test_detects_english_dosage(self):
        """English dosage patterns must be caught."""
        is_safe, _ = check_response_guardrails("Take 50 mg daily with food.")
        assert is_safe is False

    def test_case_insensitive(self):
        """Patterns must match regardless of case."""
        is_safe, _ = check_response_guardrails("NALTREXON je lék na závislost.")
        assert is_safe is False

    def test_reason_does_not_leak_pattern(self):
        """Reason string must not expose internal regex patterns."""
        _, reason = check_response_guardrails("Doporučuji naltrexon.")
        assert reason is not None
        assert "\\" not in reason  # No regex syntax in reason
