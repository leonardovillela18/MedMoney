# API MedMoney

Requer Python 3.12. Crie um ambiente virtual e execute:

```sh
pip install -r requirements.txt -r requirements-dev.txt
copy .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

Valide com `ruff check app tests`, `pytest --cov=app` e `alembic upgrade head`. `/live`, `/ready`, `/health` e `/metrics` suportam probes e monitoramento.
