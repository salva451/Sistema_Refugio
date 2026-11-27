"""Formulas estadisticas simples que usan los reportes."""


def porcentaje(parte, total):
    """(parte / total) x 100. Devuelve 0.0 si el total es 0."""
    return float(parte) / float(total) * 100 if total else 0.0


def promedio(valores):
    """Suma de valores / cantidad de valores. Devuelve 0.0 si no hay datos."""
    valores = list(valores)
    return float(sum(valores)) / len(valores) if valores else 0.0
