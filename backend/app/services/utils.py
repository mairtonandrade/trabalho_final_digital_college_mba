import re
from pathlib import Path

ALLOWED_MIME = {
    b"%PDF": "application/pdf",
    b"\x89PNG": "image/png",
    b"\xff\xd8\xff": "image/jpeg",
}


def validar_cnpj(cnpj: str) -> bool:
    digits = re.sub(r"\D", "", cnpj)
    if len(digits) != 14 or len(set(digits)) == 1:
        return False

    def calc(digs, weights):
        s = sum(int(d) * w for d, w in zip(digs, weights))
        r = s % 11
        return "0" if r < 2 else str(11 - r)

    w1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    w2 = [6] + w1
    if calc(digits[:12], w1) != digits[12]:
        return False
    if calc(digits[:13], w2) != digits[13]:
        return False
    return True


def formatar_cnpj(cnpj: str) -> str:
    d = re.sub(r"\D", "", cnpj)
    return f"{d[:2]}.{d[2:5]}.{d[5:8]}/{d[8:12]}-{d[12:]}"


def validar_cpf(cpf: str) -> bool:
    digits = re.sub(r"\D", "", cpf)
    if len(digits) != 11 or len(set(digits)) == 1:
        return False
    if digits == digits[0] * 11:
        return False

    def dv(nums: str, weights: list[int]) -> str:
        s = sum(int(n) * w for n, w in zip(nums, weights))
        r = s % 11
        return "0" if r < 2 else str(11 - r)

    if dv(digits[:9], list(range(10, 1, -1))) != digits[9]:
        return False
    if dv(digits[:10], list(range(11, 1, -1))) != digits[10]:
        return False
    return True


def formatar_cpf(cpf: str) -> str:
    d = re.sub(r"\D", "", cpf)
    return f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}"


def validar_competencia(comp: str) -> bool:
    """Formato MM/AAAA"""
    return bool(re.match(r"^(0[1-9]|1[0-2])/\d{4}$", comp.strip()))


def validar_mime_arquivo(path: Path) -> tuple[bool, str]:
    header = path.read_bytes()[:8]
    for sig, mime in ALLOWED_MIME.items():
        if header.startswith(sig):
            return True, mime
    return False, "tipo_invalido"


def benford_suspeito(valor: float) -> bool:
    """Valores redondos demais ou padrão atípico para demo."""
    s = f"{valor:.2f}".replace(".", "")
    if s.startswith("0"):
        return True
    first_digit = int(s[0])
    # Heurística simples: muitos pagamentos começando com 9 em sequência
    return first_digit == 9 and valor > 50000


def nivel_risco(score: float) -> str:
    if score >= 0.7:
        return "alto"
    if score >= 0.4:
        return "medio"
    return "baixo"
