import sys
from pathlib import Path
from datetime import datetime

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from utils.AES256 import encrypt


def compress(id_val: int, data_inicial: datetime, data_final: datetime) -> bytes:
    """Função de compressão da payload"""
    t_inicio = int(data_inicial.timestamp()) // 1800 # 30 * 60, intervalos de meia hora
    t_fim = int(data_final.timestamp()) // 1800

    return (
        id_val.to_bytes(2, byteorder="big")
        + t_inicio.to_bytes(3, byteorder="big") # 957 anos
        + t_fim.to_bytes(3, byteorder="big") # 957 anos
    )

def get_payloads(userid: int, length=1) -> list[dict]:
    """Retorna uma lista de payloads já encriptadas"""

    print(length)
    # def get_dates(userid)
    dates = [
        [datetime(2026, 9, 18, 8, 0), datetime(2026, 9, 18, 18, 0)],
        [datetime(2026, 9, 19, 8, 0), datetime(2026, 9, 19, 18, 0)],
        [datetime(2026, 9, 20, 8, 0), datetime(2026, 9, 20, 18, 0)],
        [datetime(2026, 9, 21, 8, 0), datetime(2026, 9, 21, 18, 0)],
        [datetime(2026, 9, 22, 8, 0), datetime(2026, 9, 22, 18, 0)],
    ]

    user_id = userid
    payloads = []

    for i in dates:
        compressed = compress(user_id, i[0], i[1])
        encrypted = encrypt(compressed)
        item = {
            "data": encrypted.hex(),
            "startDate": i[0].isoformat(),
            "endDate": i[1].isoformat(),
        }
        payloads.append(item)

    return payloads

if __name__ == "__main__":
    payloads = get_payloads(42500)
    for i in payloads:
        print(i)
    print("Quantidade de itens:", len(payloads))
    print("Tamanho do data (hex):", len(payloads[0]["data"]))