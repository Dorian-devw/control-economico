# Control economico personal - Fase 1

Backend base para:
- movimientos (ingresos/gastos)
- categorias
- presupuestos
- metas de ahorro
- reporte mensual a Excel con graficos

## 1) Instalacion

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 2) Configuracion de base de datos

1. Copia `.env.example` a `.env`.
2. Configura PostgreSQL:

```env
DATABASE_URL=postgresql+psycopg2://postgres:tu_password@localhost:5432/control_economico
```

## 3) Ejecutar API

```bash
uvicorn app.main:app --reload
```

Docs:
- http://127.0.0.1:8000/docs

## 4) Cargar datos demo

```bash
python scripts/seed_demo.py
```

## 5) Generar reporte Excel

```bash
python scripts/export_report.py --year 2026 --month 4
```

Se crea en `exports/reporte_YYYY_MM.xlsx`.

## Endpoints base (Fase 1)

- `POST /categories`
- `GET /categories`
- `POST /movements`
- `GET /movements?year=2026&month=4`
- `POST /budgets`
- `GET /budgets?year=2026&month=4`
- `POST /savings-goals`
- `GET /savings-goals`
- `GET /summary?year=2026&month=4`
- `POST /reports/monthly?year=2026&month=4`
