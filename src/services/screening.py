"""WHO AUDIT (Alcohol Use Disorders Identification Test) scoring.

The AUDIT is a 10-question screening tool developed by the WHO.
It is public domain and widely validated.
"""

from pydantic import BaseModel


class AuditOption(BaseModel):
    text_cs: str
    text_en: str
    value: int


class AuditQuestion(BaseModel):
    number: int
    text_cs: str
    text_en: str
    options: list[AuditOption]


class AuditResult(BaseModel):
    total_score: int
    risk_level: str
    recommendation_cs: str
    recommendation_en: str


AUDIT_QUESTIONS: list[AuditQuestion] = [
    AuditQuestion(
        number=1,
        text_cs="Jak často piješ alkoholické nápoje?",
        text_en="How often do you have a drink containing alcohol?",
        options=[
            AuditOption(text_cs="Nikdy", text_en="Never", value=0),
            AuditOption(text_cs="Jednou za měsíc nebo méně", text_en="Monthly or less", value=1),
            AuditOption(text_cs="2–4× za měsíc", text_en="2-4 times a month", value=2),
            AuditOption(text_cs="2–3× za týden", text_en="2-3 times a week", value=3),
            AuditOption(text_cs="4× nebo vícekrát za týden", text_en="4 or more times a week", value=4),
        ],
    ),
    AuditQuestion(
        number=2,
        text_cs="Kolik sklenic alkoholu obvykle vypiješ, když piješ?",
        text_en="How many drinks containing alcohol do you have on a typical day when you are drinking?",
        options=[
            AuditOption(text_cs="1–2", text_en="1 or 2", value=0),
            AuditOption(text_cs="3–4", text_en="3 or 4", value=1),
            AuditOption(text_cs="5–6", text_en="5 or 6", value=2),
            AuditOption(text_cs="7–9", text_en="7 to 9", value=3),
            AuditOption(text_cs="10 nebo více", text_en="10 or more", value=4),
        ],
    ),
    AuditQuestion(
        number=3,
        text_cs="Jak často vypiješ 6 nebo více sklenic při jedné příležitosti?",
        text_en="How often do you have 6 or more drinks on one occasion?",
        options=[
            AuditOption(text_cs="Nikdy", text_en="Never", value=0),
            AuditOption(text_cs="Méně než jednou za měsíc", text_en="Less than monthly", value=1),
            AuditOption(text_cs="Jednou za měsíc", text_en="Monthly", value=2),
            AuditOption(text_cs="Jednou za týden", text_en="Weekly", value=3),
            AuditOption(text_cs="Denně nebo téměř denně", text_en="Daily or almost daily", value=4),
        ],
    ),
    AuditQuestion(
        number=4,
        text_cs="Jak často se ti za poslední rok stalo, že jsi nemohl/a přestat pít, když jsi začal/a?",
        text_en="How often during the last year have you found that you were not able to stop drinking once you had started?",
        options=[
            AuditOption(text_cs="Nikdy", text_en="Never", value=0),
            AuditOption(text_cs="Méně než jednou za měsíc", text_en="Less than monthly", value=1),
            AuditOption(text_cs="Jednou za měsíc", text_en="Monthly", value=2),
            AuditOption(text_cs="Jednou za týden", text_en="Weekly", value=3),
            AuditOption(text_cs="Denně nebo téměř denně", text_en="Daily or almost daily", value=4),
        ],
    ),
    AuditQuestion(
        number=5,
        text_cs="Jak často se ti za poslední rok stalo, že jsi kvůli pití nesplnil/a, co se od tebe očekávalo?",
        text_en="How often during the last year have you failed to do what was normally expected of you because of drinking?",
        options=[
            AuditOption(text_cs="Nikdy", text_en="Never", value=0),
            AuditOption(text_cs="Méně než jednou za měsíc", text_en="Less than monthly", value=1),
            AuditOption(text_cs="Jednou za měsíc", text_en="Monthly", value=2),
            AuditOption(text_cs="Jednou za týden", text_en="Weekly", value=3),
            AuditOption(text_cs="Denně nebo téměř denně", text_en="Daily or almost daily", value=4),
        ],
    ),
    AuditQuestion(
        number=6,
        text_cs="Jak často se ti za poslední rok stalo, že jsi po pití potřeboval/a ráno alkohol, abys mohl/a fungovat?",
        text_en="How often during the last year have you needed a first drink in the morning to get yourself going after a heavy drinking session?",
        options=[
            AuditOption(text_cs="Nikdy", text_en="Never", value=0),
            AuditOption(text_cs="Méně než jednou za měsíc", text_en="Less than monthly", value=1),
            AuditOption(text_cs="Jednou za měsíc", text_en="Monthly", value=2),
            AuditOption(text_cs="Jednou za týden", text_en="Weekly", value=3),
            AuditOption(text_cs="Denně nebo téměř denně", text_en="Daily or almost daily", value=4),
        ],
    ),
    AuditQuestion(
        number=7,
        text_cs="Jak často se ti za poslední rok stalo, že jsi měl/a pocit viny nebo výčitek svědomí po pití?",
        text_en="How often during the last year have you had a feeling of guilt or remorse after drinking?",
        options=[
            AuditOption(text_cs="Nikdy", text_en="Never", value=0),
            AuditOption(text_cs="Méně než jednou za měsíc", text_en="Less than monthly", value=1),
            AuditOption(text_cs="Jednou za měsíc", text_en="Monthly", value=2),
            AuditOption(text_cs="Jednou za týden", text_en="Weekly", value=3),
            AuditOption(text_cs="Denně nebo téměř denně", text_en="Daily or almost daily", value=4),
        ],
    ),
    AuditQuestion(
        number=8,
        text_cs="Jak často se ti za poslední rok stalo, že sis nemohl/a vzpomenout, co se stalo předchozí večer, protože jsi pil/a?",
        text_en="How often during the last year have you been unable to remember what happened the night before because of your drinking?",
        options=[
            AuditOption(text_cs="Nikdy", text_en="Never", value=0),
            AuditOption(text_cs="Méně než jednou za měsíc", text_en="Less than monthly", value=1),
            AuditOption(text_cs="Jednou za měsíc", text_en="Monthly", value=2),
            AuditOption(text_cs="Jednou za týden", text_en="Weekly", value=3),
            AuditOption(text_cs="Denně nebo téměř denně", text_en="Daily or almost daily", value=4),
        ],
    ),
    AuditQuestion(
        number=9,
        text_cs="Byl/a jsi ty nebo někdo jiný zraněn v důsledku tvého pití?",
        text_en="Have you or someone else been injured because of your drinking?",
        options=[
            AuditOption(text_cs="Ne", text_en="No", value=0),
            AuditOption(text_cs="Ano, ale ne za poslední rok", text_en="Yes, but not in the last year", value=2),
            AuditOption(text_cs="Ano, za poslední rok", text_en="Yes, during the last year", value=4),
        ],
    ),
    AuditQuestion(
        number=10,
        text_cs="Navrhl ti někdo z příbuzných, přátel, lékař nebo jiný zdravotník, abys omezil/a pití?",
        text_en="Has a relative, friend, doctor, or other health care worker been concerned about your drinking or suggested you cut down?",
        options=[
            AuditOption(text_cs="Ne", text_en="No", value=0),
            AuditOption(text_cs="Ano, ale ne za poslední rok", text_en="Yes, but not in the last year", value=2),
            AuditOption(text_cs="Ano, za poslední rok", text_en="Yes, during the last year", value=4),
        ],
    ),
]

# Risk levels per WHO AUDIT manual
_RISK_LEVELS = {
    "low_risk": (0, 7),
    "hazardous": (8, 15),
    "harmful": (16, 19),
    "possible_dependence": (20, 40),
}

_RECOMMENDATIONS_CS = {
    "low_risk": "Tvé odpovědi naznačují nízké riziko. Pokračuj v udržování zdravého vztahu k alkoholu.",
    "hazardous": "Tvé odpovědi naznačují rizikové pití. Luceo ti může pomoci s technikami pro snížení konzumace.",
    "harmful": "Tvé odpovědi naznačují škodlivé pití. Doporučujeme konzultaci s odborníkem. Luceo tě podpoří na cestě ke změně.",
    "possible_dependence": "Tvé odpovědi naznačují, že by ti prospěla konzultace se zdravotnickým odborníkem. Luceo tě může podpořit, ale odborné vedení je důležité.",
}

_RECOMMENDATIONS_EN = {
    "low_risk": "Your responses suggest a low-risk relationship with alcohol.",
    "hazardous": "Your responses suggest hazardous drinking. Luceo can help you with techniques to reduce consumption.",
    "harmful": "Your responses suggest harmful drinking. We recommend consulting with a professional. Luceo will support you on your path to change.",
    "possible_dependence": "Your responses suggest it would be beneficial to speak with a healthcare professional. Luceo can support you, but professional guidance is recommended.",
}


def score_audit(answers: list[int]) -> AuditResult:
    """Score AUDIT questionnaire answers. Expects a list of 10 integers."""
    if len(answers) != 10:
        raise ValueError("AUDIT requires exactly 10 answers")

    total = sum(answers)

    risk_level = "low_risk"
    for level, (low, high) in _RISK_LEVELS.items():
        if low <= total <= high:
            risk_level = level
            break

    return AuditResult(
        total_score=total,
        risk_level=risk_level,
        recommendation_cs=_RECOMMENDATIONS_CS[risk_level],
        recommendation_en=_RECOMMENDATIONS_EN[risk_level],
    )
