# ETL Junior — Python + SQL + Excel

Proyecto de portfolio que transforma un CSV de pedidos sucios en filas limpias, separa rechazos con razones explícitas y deja los datos listos para cargar a SQL y revisar en Excel.

![ETL CI](https://github.com/agustiininicabral/04-etl-junior-sql-python-excel/actions/workflows/ci.yml/badge.svg)

## Objetivo

Demostrar un ETL reproducible: lectura, normalización de fechas y moneda, validación de campos, cálculo de importes, registro de filas rechazadas y ejecución de pruebas.

Todos los datos son sintéticos.

## Requisitos

- Python 3.12 o posterior.
- Dependencia runtime: pandas.

Instalación:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Para desarrollo y pruebas, instalar también `requirements-dev.txt`.

## Ejecutar el ETL

```powershell
python etl/etl_clean_orders.py --in data/orders_dirty.csv --out data/orders_clean.csv --rejected data/orders_rejected.csv
```

El proceso informa cuántas filas entraron, cuántas quedaron limpias y cuántas fueron rechazadas. Cada fila rechazada incluye la fila de origen y una razón; el archivo fuente no se modifica.

Reglas principales:
- Aceptar fechas ISO (`YYYY-MM-DD`) o `DD/MM/YYYY`.
- Convertir importes con o sin símbolo de moneda.
- Interpretar descuento vacío como 0 y rechazar descuentos inválidos o fuera de 0–80%.
- Exigir IDs y cantidades enteras positivas.
- Rechazar fechas inválidas, precios no positivos y IDs de pedido duplicados.
- Calcular net_amount con redondeo decimal half-up a dos decimales.

## SQL y Excel

- `sql/schema.sql`: estructura de la tabla staging.
- `sql/queries.sql`: ventas netas por día y top de productos.
- `excel/etl_summary.xlsx`: resumen visual de ejemplo.

El archivo limpio se puede cargar en la tabla `stg_order` después de crear el esquema. Revisá primero `orders_rejected.csv`; no descartes silenciosamente las filas rechazadas.

## Pruebas y CI

```powershell
python -m pytest -q
ruff format --check etl tests
ruff check etl tests
```

GitHub Actions ejecuta las pruebas, verifica formato/lint y corre el ETL sobre el dataset incluido. Publica los CSV limpio y rechazado como artefactos temporales.

## Estructura

- `data/orders_dirty.csv`: fuente sintética con casos a corregir.
- `data/orders_clean.csv`: salida de ejemplo; regenerala con el comando anterior antes de usarla.
- `etl/etl_clean_orders.py`: parsers y pipeline ETL.
- `tests/test_etl_clean_orders.py`: casos de parsing, rechazo y redondeo.
- `sql/`: esquema y consultas.
- `excel/etl_summary.xlsx`: dashboard de demostración.

## Licencia

MIT.
