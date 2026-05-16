import os
from typing import Optional

import httpx

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3:8b")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")


def _parecer_template(
    razao_social: str,
    cnpj: str,
    valor: float,
    risk_score: float,
    flags: list[str],
    dados_conferem: bool,
) -> str:
    nivel = "ALTO" if risk_score >= 0.7 else "MÉDIO" if risk_score >= 0.4 else "BAIXO"
    flags_txt = "; ".join(flags) if flags else "Nenhuma anomalia heurística crítica"
    conf = "CONFEREM" if dados_conferem else "NÃO CONFEREM"
    return (
        f"[Parecer Auditor IA - Risco {nivel} ({risk_score:.0%})]\n"
        f"Fornecedor: {razao_social} (CNPJ {cnpj}). Valor: R$ {valor:,.2f}.\n"
        f"Cruzamento documental: dados do anexo {conf} com o cadastro.\n"
        f"Alertas: {flags_txt}.\n"
        f"Recomendação: "
        + (
            "Bloquear ou exigir justificativa do gerente antes da liberação bancária."
            if risk_score >= 0.7
            else "Liberar com monitoramento se demais controles estiverem OK."
            if risk_score < 0.4
            else "Revisão gerencial obrigatória antes da liberação."
        )
    )


async def _ollama_generate(prompt: str) -> Optional[str]:
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(
                OLLAMA_URL,
                json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            )
            if r.status_code == 200:
                return r.json().get("response", "").strip()
    except Exception:
        pass
    return None


async def gerar_parecer_auditoria(
    razao_social: str,
    cnpj: str,
    valor: float,
    risk_score: float,
    flags: list[str],
    dados_conferem: bool,
    nome_documento: Optional[str] = None,
) -> str:
    prompt = f"""Você é auditor financeiro sênior. Analise este pagamento e responda em português em 4 linhas:
Fornecedor: {razao_social}, CNPJ: {cnpj}, Valor: R$ {valor:.2f}
Score de fraude ML: {risk_score:.0%}
Alertas: {', '.join(flags) or 'nenhum'}
Documento anexo: {nome_documento or 'não informado'}
Dados conferem com cadastro: {'sim' if dados_conferem else 'não'}
Dê parecer objetivo sobre risco e recomendação (aprovar, revisar ou bloquear)."""

    llm = await _ollama_generate(prompt)
    if llm and len(llm) > 50:
        return llm

    return _parecer_template(razao_social, cnpj, valor, risk_score, flags, dados_conferem)


def conferir_dados_documento(
    razao_social: str, cnpj: str, valor: float, nome_arquivo: Optional[str]
) -> bool:
    """Simulação OCR: nome do arquivo contendo parte do CNPJ ou 'ok' = conferência OK."""
    if not nome_arquivo:
        return True
    nome = nome_arquivo.lower()
    digits = "".join(c for c in cnpj if c.isdigit())[:8]
    if "fraud" in nome or "fake" in nome or "suspeito" in nome:
        return False
    if digits and digits[:4] in nome.replace(".", "").replace("-", ""):
        return True
    if "nf" in nome or "nota" in nome or "fatura" in nome:
        return True
    return valor < 50000
