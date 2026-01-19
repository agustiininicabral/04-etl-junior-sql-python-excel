# ETL Junior (Python + SQL + Excel)

## Objetivo
Pipeline simple: dataset sucio → limpieza/validación → salida limpia → carga a SQL → resumen en Excel.

## Stack
- Python (pandas)
- SQL (staging table)
- Excel (resumen + gráfico)
- Dataset incluido

## Cómo ejecutar (rápido)
1) `python etl/etl_clean_orders.py --in data/orders_dirty.csv --out data/orders_clean.csv`
2) Crear tabla: `sql/schema.sql`
3) Cargar `orders_clean.csv` a `stg_order`
4) Ejecutar: `sql/queries.sql`
5) Abrir `excel/etl_summary.xlsx`

## Estructura
```
04-etl-junior-sql-python-excel/
├── data/
├── etl/etl_clean_orders.py
├── sql/
└── excel/etl_summary.xlsx
```

