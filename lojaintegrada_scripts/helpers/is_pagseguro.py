def is_pagseguro(codigo: str) -> bool:
    return codigo in ["pagsegurov2", "psboleto"]
