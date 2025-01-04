"""Módulo para conversão de documentos Markdown.

Este módulo fornece funcionalidades para converter documentos Markdown
em outros formatos, como JSON.
"""

import re
from typing import Any

import markdown
from bs4 import BeautifulSoup


class MarkdownConverter:
    """Conversor de documentos Markdown.

    Esta classe fornece métodos para converter documentos Markdown
    em outros formatos, como JSON.

    Attributes
    ----------
    md : markdown.Markdown
        Instância do conversor Markdown.

    """

    def __init__(self) -> None:
        """Inicializa o conversor.

        Configura o conversor Markdown com as extensões necessárias.
        """
        self.md = markdown.Markdown(extensions=['extra'])

    def to_json(self, content: str) -> dict[str, Any]:
        """Convert a Markdown document to JSON format.

        Parameters
        ----------
        content : str
            Conteúdo do documento em formato Markdown.

        Returns
        -------
        dict[str, Any]
            Documento convertido em formato JSON.

        """
        # Converte Markdown para HTML
        html = self.md.convert(content)
        soup = BeautifulSoup(html, 'html.parser')

        # Extrai título
        title = soup.find('h1')
        title = title.text if title else ''

        # Extrai subtítulos
        headings = soup.find_all(['h2', 'h3', 'h4', 'h5', 'h6'])
        sections = [h.text for h in headings]

        # Extrai links
        links = []
        for a in soup.find_all('a'):
            href = a.get('href', '')
            text = a.text
            if href and text:
                links.append({
                    'text': text,
                    'url': href
                })

        # Extrai código
        code_blocks = []
        for code in soup.find_all('code'):
            code_blocks.append(code.text)

        # Extrai texto principal
        text = re.sub(r'\s+', ' ', soup.get_text()).strip()

        return {
            'title': title,
            'sections': sections,
            'links': links,
            'code_blocks': code_blocks,
            'text': text,
            'html': html
        }
