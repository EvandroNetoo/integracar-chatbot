from docling.document_converter import DocumentConverter

source = "/home/evandro/Downloads/APRESENTAÇÃO - INTEGRACAR - NP 101, CANCELAMENTO, ERROS DO SISTEMA.pdf"  # file path or URL
converter = DocumentConverter()
doc = converter.convert(source).document

print(doc.export_to_markdown())  # output: "### Docling Technical Report[...]"