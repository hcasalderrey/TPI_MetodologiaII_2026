# TPI Metodología de Sistemas II – Membresías y cuotas de un gimnasio

Trabajo Práctico Integrador: análisis y refactoring seguro de un módulo simple de gestión de socios, planes y pagos de un gimnasio (Python). Todos los datos son inventados.

## Estructura

| Carpeta | Contenido |
|---|---|
| `Antes/` | Versión inicial, con problemas de diseño detectables (tag `estado-inicial`) |
| `Despues/` | Versión refactorizada (tag `estado-refactorizado`) |
| `docs/` | Diagnóstico de smells, checklist de code review, evidencias y decisiones técnicas |

## Funcionalidades

- Registrar socio (validaciones y cálculo de cuota según plan)
- Cambiar plan
- Registrar pago (con recargo por pago tardío)
- Reporte de socios morosos

## Uso

```bash
pip install pytest
cd Antes        # o Despues
python gimnasio.py   # demo con un escenario fijo
python -m pytest     # tests
```

Los tests de `Antes/` y `Despues/` son los mismos: verifican que el comportamiento externo no cambia con el refactoring.

## Tecnologías

Python 3.11, pytest.

## Integrantes

_(completar)_
