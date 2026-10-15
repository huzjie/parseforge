"""Model Context Protocol (MCP) server adapter.

Implements a minimal MCP tool schema (name / description / inputSchema) and a
``call_tool`` dispatcher. This is the standard shape an MCP host expects; bind it
to a real transport (stdio/SSE) in your host of choice.
"""


class ParseforgeMCPServer:
    """Expose ``parseforge.parse_document`` as an MCP tool."""

    def __init__(self, cfg=None):
        from ..engine import OmniParser
        self.parser = OmniParser(cfg)

    def list_tools(self):
        return [{
            "name": "parse_document",
            "description": "Parse a document into structured JSON blocks.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "document text"},
                    "doc_id": {"type": "string", "description": "optional id"},
                },
                "required": ["text"],
            },
        }]

    def call_tool(self, name, arguments):
        if name != "parse_document":
            raise ValueError("unknown tool %r" % name)
        from ..parse import Document
        doc = Document(doc_id=arguments.get("doc_id", "mcp-0"),
                       text=arguments.get("text", ""),
                       candidates=arguments.get("candidates", []))
        result = self.parser.parse(doc)
        return {"content": [{"type": "text", "text": result.to_json()}]}
