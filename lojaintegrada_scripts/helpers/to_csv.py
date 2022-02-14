import csv
from os import path

CWD = path.dirname(path.abspath(__file__))


def to_csv(data: list[dict]):
    if not data:
        return

    keys = data[0].keys()
    headers = [" ".join([text.title() for text in key.split("_")]) for key in keys]

    file_path = path.join(CWD, "tmp.csv")

    # valor_total = round(sum([p.valor_total for p in pagamentos]), 2)
    # valor_taxa = round(sum([p.valor_taxa for p in pagamentos]), 2)
    # valor_desconto = round(sum([p.valor_desconto for p in pagamentos]), 2)
    # valor_frete = 0
    # valor_custo = 0
    # valor_lucro = 0

    with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, dialect="excel", delimiter=",")
        writer.writerow(headers)

        for d in data:
            row = [d[key] for key in keys]
            writer.writerow(row)

    return file_path
