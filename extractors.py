import io
import re
import requests
from bs4 import BeautifulSoup
from pdfminer.high_level import extract_text as pdf_extract_text

HEADERS = {"User-Agent": "Mozilla/5.0 (PaperSummarizerBot)"}

ARXIV_ABS = re.compile(r"https?://arxiv\.org/abs/([\w\.-]+)")
ARXIV_PDF = re.compile(r"https?://arxiv\.org/pdf/([\w\.-]+)\.pdf")


def _to_arxiv_pdf(url: str) -> str | None:
    m_abs = ARXIV_ABS.match(url)
    if m_abs:
        return f"https://arxiv.org/pdf/{m_abs.group(1)}.pdf"
    m_pdf = ARXIV_PDF.match(url)
    if m_pdf:
        return url
    return None


def _fetch(url: str) -> requests.Response:
    resp = requests.get(url, headers=HEADERS, timeout=45)
    resp.raise_for_status()
    return resp


def _extract_from_pdf_bytes(pdf_bytes: bytes) -> str:
    with io.BytesIO(pdf_bytes) as f:
        text = pdf_extract_text(f)
    return text


def _extract_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    # Prefer article-like content if available
    for sel in ["article", "main", "#content", ".content", "#paper", "#abs"]:
        node = soup.select_one(sel)
        if node:
            return "\n".join(p.get_text(" ", strip=True) for p in node.find_all(["p", "li"]))
    # Fallback: all paragraphs
    return "\n".join(p.get_text(" ", strip=True) for p in soup.find_all("p"))


def extract_text_from_url(url: str) -> str:
    """Extract text from arXiv (PDF), direct PDF, or generic HTML."""
    # 1) arXiv convenience
    pdf_url = _to_arxiv_pdf(url)
    if pdf_url:
        resp = _fetch(pdf_url)
        return _extract_from_pdf_bytes(resp.content)

    # 2) direct PDF
    if url.lower().endswith(".pdf"):
        resp = _fetch(url)
        return _extract_from_pdf_bytes(resp.content)

    # 3) generic HTML
    resp = _fetch(url)
    ctype = resp.headers.get("Content-Type", "").lower()
    if "pdf" in ctype:
        return _extract_from_pdf_bytes(resp.content)
    return _extract_from_html(resp.text)