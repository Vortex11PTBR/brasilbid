"""Cliente da API pública do PNCP."""
import time
import requests
from datetime import date
from typing import Generator

BASE = "https://pncp.gov.br/api/consulta/v1"
PAGE_SIZE = 50

# Todas as modalidades disponíveis na API
MODALIDADES = [1, 2, 3, 4, 5, 6, 7, 8]

SESSION = requests.Session()
SESSION.headers.update({"Accept": "application/json", "User-Agent": "BrasilBid/1.0"})


def _get(url: str, params: dict, retries: int = 3) -> dict | None:
    for attempt in range(retries):
        try:
            r = SESSION.get(url, params=params, timeout=30)
            if r.status_code == 204:
                return None
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            if attempt == retries - 1:
                print(f"  ⚠️  {url} {params} → {e}")
                return None
            time.sleep(2 ** attempt)
    return None


def fetch_contratacoes(
    data_inicial: date,
    data_final: date,
) -> Generator[dict, None, None]:
    """Gera todos os registros de contratações no intervalo de datas."""
    fmt = lambda d: d.strftime("%Y%m%d")

    for modalidade in MODALIDADES:
        pagina = 1
        while True:
            data = _get(
                f"{BASE}/contratacoes/publicacao",
                params={
                    "dataInicial": fmt(data_inicial),
                    "dataFinal": fmt(data_final),
                    "codigoModalidadeContratacao": modalidade,
                    "pagina": pagina,
                    "tamanhoPagina": PAGE_SIZE,
                },
            )
            if not data:
                break

            items = data.get("data", [])
            if not items:
                break

            yield from items

            total = data.get("totalRegistros", 0)
            if pagina * PAGE_SIZE >= total:
                break
            pagina += 1
            time.sleep(0.3)  # respeitar rate limit


def normalizar(raw: dict) -> dict:
    """Mapeia campos da API para o schema da tabela."""
    orgao = raw.get("orgaoEntidade") or {}
    unidade = raw.get("unidadeOrgao") or {}
    return {
        "numero_controle_pncp": raw.get("numeroControlePNCP"),
        "orgao_cnpj":           orgao.get("cnpj"),
        "orgao_nome":           orgao.get("razaoSocial"),
        "modalidade_id":        raw.get("modalidadeId"),
        "modalidade_nome":      raw.get("modalidadeNome"),
        "modo_disputa_nome":    raw.get("modoDisputaNome"),
        "objeto_compra":        raw.get("objetoCompra"),
        "valor_total_estimado": raw.get("valorTotalEstimado"),
        "valor_homologado":     raw.get("valorTotalHomologado"),
        "uf_sigla":             unidade.get("ufSigla"),
        "municipio_nome":       unidade.get("municipioNome"),
        "situacao_nome":        raw.get("situacaoCompraNome"),
        "data_publicacao":      raw.get("dataPublicacaoPncp"),
        "data_encerramento":    raw.get("dataEncerramentoProposta"),
        "data_inclusao":        raw.get("dataInclusao"),
        "link_edital":          raw.get("linkSistemaOrigem") or raw.get("linkProcessoEletronico"),
        "numero_compra":        raw.get("numeroCompra"),
        "ano_compra":           raw.get("anoCompra"),
    }
