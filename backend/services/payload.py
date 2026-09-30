import sys
from pathlib import Path
from datetime import datetime, date, time, timedelta
from typing import List, Dict, Any

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from utils.AES256 import encrypt
from db.connection import get_user_by_cpf


def build_payload_bytes(cpf: int, data_inicial: datetime, data_final: datetime) -> bytes:
    """Monta a payload em formato binário sem compressão (16 bytes)"""
    return (
        int(cpf).to_bytes(8, "big")
        + int(data_inicial.timestamp()).to_bytes(4, "big")
        + int(data_final.timestamp()).to_bytes(4, "big")
    )


compress = build_payload_bytes


def get_dates(cpf: int, length: int = 1) -> List[List[datetime]]:
    """Gera as próximas n datas para um usuário, ou apenas a disponível se não for recorrente"""
    user = get_user_by_cpf(cpf)
    if not user:
        return []

    start = time.fromisoformat(user["access_hours"]["start"])
    end = time.fromisoformat(user["access_hours"]["end"])

    # Se não for recorrente, retorna apenas a data específica disponível
    if not user.get("is_recurring", True):
        d = date.fromisoformat(str(user["specific_date"])[:10])
        return [[datetime.combine(d, start), datetime.combine(d, end)]]

    if not user.get("access_days"):
        return []

    dates, day = [], date.today()
    while len(dates) < length:
        if day.weekday() in user["access_days"]:
            dates.append([datetime.combine(day, start), datetime.combine(day, end)])
        day += timedelta(days=1)

    return dates


def get_payloads(cpf: int, length: int = 1) -> List[Dict[str, Any]]:
    """Retorna uma lista de payloads encriptadas com base no CPF do usuário e tamanho do lote"""
    return [
        {
            "data": encrypt(build_payload_bytes(cpf, dt_ini, dt_fim)).hex(),
            "startDate": dt_ini.isoformat(),
            "endDate": dt_fim.isoformat(),
        }
        for dt_ini, dt_fim in get_dates(cpf, length=length)
    ]