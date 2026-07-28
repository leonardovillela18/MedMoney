import os

from app.database.session import SessionLocal
from app.services.admin_bootstrap import provision_admin


def main() -> None:
    email = os.getenv('BOOTSTRAP_ADMIN_EMAIL', '').strip()
    password = os.getenv('BOOTSTRAP_ADMIN_PASSWORD', '')
    if not email and not password:
        return
    if not email or not password:
        raise RuntimeError('Defina BOOTSTRAP_ADMIN_EMAIL e BOOTSTRAP_ADMIN_PASSWORD em conjunto.')

    with SessionLocal() as db:
        admin = provision_admin(db, email, password)
    print(f'Administrador provisionado: {admin.email}', flush=True)


if __name__ == '__main__':
    main()
