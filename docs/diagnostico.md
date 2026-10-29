# Diagnóstico de calidad interna

## Calidad externa e interna

El sistema permite registrar socios, cambiar planes, registrar pagos y listar morosos. La demostración se ejecuta y las 9 pruebas iniciales pasan. Sin embargo, la estructura interna concentra responsabilidades y repite lógica, lo que aumenta el riesgo y el esfuerzo de futuros cambios.

## Deuda técnica y code smells

| N.º | Problema y ubicación en `Antes/gimnasio.py` | Impacto | Prioridad |
|---|---|---|---|
| 1 | `GimnasioService` reúne validación, cálculo, persistencia, presentación y reportes (líneas 5–118). | Un cambio en cualquiera de esas tareas obliga a modificar la misma clase. | Alta |
| 2 | `registrar_socio` recibe siete datos separados (línea 17). | Es fácil intercambiar argumentos y difícil ampliar el alta. | Media |
| 3 | Se usan nombres poco descriptivos como `d`, `c`, `x`, `p` y `lst` (líneas 8, 34, 42, 98 y 108). | El código requiere más esfuerzo para entenderse y revisarse. | Media |
| 4 | El cálculo de cuotas se repite en `registrar_socio` y `cambiar_plan` (líneas 33–38 y 64–69). | Una modificación de precios puede quedar aplicada en un solo lugar. | Alta |
| 5 | La búsqueda de socios por DNI se repite en varias operaciones (líneas 28–31, 58–60 y 85–88). | Las reglas de búsqueda pueden divergir con el tiempo. | Media |
| 6 | La escritura del archivo JSON se repite tres veces (líneas 47–49, 75–77 y 101–103). | El manejo de errores y el formato de guardado pueden volverse inconsistentes. | Alta |
| 7 | El constructor captura cualquier excepción al leer datos (línea 14). | Puede ocultar un archivo corrupto u otro fallo y continuar como si no hubiera datos. | Alta |
| 8 | Precios, descuentos, día límite y recargo están escritos directamente en los métodos (líneas 33–38, 64–69 y 93–94). | Cambiar reglas de negocio exige buscar y editar varios fragmentos de código. | Media |

## Orden propuesto de corrección

Primero se protegerá el comportamiento con pruebas. Después se extraerán el cálculo de cuotas y la búsqueda de socios, se separará la persistencia y se agruparán los parámetros del alta. Cada cambio se verificará con las pruebas antes de continuar.