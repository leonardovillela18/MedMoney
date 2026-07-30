"""Audita localidades legadas. Por padrão, não altera dados.

Uso: python scripts/audit_reference_data.py [--apply]
"""
import argparse

from sqlalchemy import select

from app.database.session import SessionLocal
from app.models.contractor import Contractor
from app.models.shift import Shift
from app.models.user import User
from app.services.location_service import municipalities, normalize_state, normalize_text


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true', help='aplica apenas correspondências exatas e inequívocas')
    args = parser.parse_args()
    by_location: dict[tuple[str, str], list[dict]] = {}
    for city in municipalities():
        by_location.setdefault((city['state'], city['normalized_name']), []).append(city)
    changes = 0
    with SessionLocal() as db:
        for model in (User, Contractor, Shift):
            for row in db.scalars(select(model)):
                state = normalize_state(getattr(row, 'state', None))
                city = getattr(row, 'city', None)
                candidates = by_location.get((state, normalize_text(city)), []) if state and city else []
                code = candidates[0]['ibge_code'] if len(candidates) == 1 else None
                if state != getattr(row, 'state', None) or (code and not getattr(row, 'city_ibge_code', None)):
                    changes += 1
                    print(f'{model.__tablename__}:{row.id} {row.city}/{row.state} -> {city}/{state} [{code or "ambígua"}]')
                    if args.apply:
                        row.state = state
                        if code:
                            row.city_ibge_code = code
        if args.apply:
            db.commit()
    print(f'{changes} registro(s) candidato(s). Modo: {"aplicação segura" if args.apply else "dry-run"}.')


if __name__ == '__main__':
    main()
