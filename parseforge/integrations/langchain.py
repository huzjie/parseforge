"""LangChain tool adapter.

Optional: uses langchain if installed, otherwise degrades to a plain callable
with the same interface. Keeps the package zero-dependency by only importing
langchain lazily.
"""


class ParseDocumentTool:
    """A LangChain-style tool that parses a document into structured JSON.

    Exposes ``name``, ``description`` and ``run(text)`` so it can be dropped into
    an agent's tool list without importing langchain.
    """

    name = "parse_document"
    description = ("Parse a document (text and/or image) into structured JSON "
                   "blocks. Useful before downstream extraction or search.")

    def __init__(self, cfg=None):
        from ..engine import OmniParser
        self.parser = OmniParser(cfg)

    def run(self, text, doc_id="langchain-0", candidates=None):
        from ..parse import Document
        doc = Document(doc_id=doc_id, text=text, candidates=candidates or [])
        result = self.parser.parse(doc)
        return result.to_json()

    def as_langchain_tool(self):
        """Return a real langchain Tool when the library is present."""
        from langchain.tools import Tool
        return Tool(
            name=self.name,
            description=self.description,
            func=lambda text: self.run(text),
        )

    def __call__(self, text):
        return self.run(text)
