"""Czech crisis contacts — hardcoded for reliability.

This module has NO external dependencies. It must work even if the database
or any API is down. Crisis contacts are life-critical information.
"""

from pydantic import BaseModel


class CrisisContact(BaseModel):
    name: str
    phone: str
    description: str
    available: str
    url: str | None = None


CZECH_CRISIS_CONTACTS: list[CrisisContact] = [
    CrisisContact(
        name="Linka bezpečí",
        phone="116 111",
        description="Krizová linka pro děti a mladistvé",
        available="24/7",
        url="https://www.linkabezpeci.cz",
    ),
    CrisisContact(
        name="Linka první psychické pomoci",
        phone="116 123",
        description="Telefonická krizová intervence a první psychická pomoc",
        available="24/7",
        url="https://www.csspraha.cz",
    ),
    CrisisContact(
        name="Národní linka pro odvykání",
        phone="800 350 000",
        description="Bezplatná linka pro závislosti (alkohol, drogy, tabák)",
        available="Po-Pá 10:00-18:00",
        url="https://www.adfranklinova.cz",
    ),
    CrisisContact(
        name="Podané ruce",
        phone="549 257 217",
        description="Poradenství a léčba závislostí",
        available="Po-Pá 8:00-16:00",
        url="https://www.podaneruce.cz",
    ),
    CrisisContact(
        name="Záchranná služba",
        phone="155",
        description="Zdravotnická záchranná služba",
        available="24/7",
    ),
    CrisisContact(
        name="Tísňová linka",
        phone="112",
        description="Integrovaný záchranný systém",
        available="24/7",
    ),
]
