# TPI – Metodología de Sistemas II
## Sistema de Gestión de Membresías y Cuotas de un Gimnasio

**Tecnicatura Universitaria en Programación – UTN**

**Materia:** Metodología de Sistemas II  
**Año:** 2026  
**Lenguaje:** Python 3.11  
**Testing:** pytest

**Integrantes:**

- Gonzalo Castellini
- Hernán Casalderrey
- Lautaro Buchek
  
Comisión: 4

Link a video: https://youtu.be/ZHZbdamoZ_w

Fecha de entrega: 08/11/2026

---

## 1. Descripción del proyecto

Este repositorio contiene el Trabajo Práctico Integrador de Metodología de Sistemas II.

El proyecto consiste en analizar y mejorar un sistema de gestión de socios, planes de membresía y pagos de un gimnasio.

Se parte de una implementación funcional, pero con problemas de diseño y mantenibilidad. A partir de ella, se realiza un proceso de diagnóstico y refactoring, aplicando buenas prácticas de desarrollo de software.

El objetivo principal es **mejorar la calidad interna del código sin modificar su comportamiento funcional externo**.

Todos los datos utilizados son ficticios y tienen fines académicos.

## 2. Objetivos

- Identificar problemas de calidad interna y deuda técnica.
- Detectar code smells y dificultades de mantenibilidad.
- Aplicar principios de Clean Code.
- Implementar técnicas de refactoring seguro.
- Aplicar principios SOLID.
- Incorporar patrones de diseño cuando aporten valor.
- Reducir el acoplamiento y aumentar la cohesión.
- Mantener las funcionalidades existentes.
- Verificar el comportamiento mediante pruebas automatizadas.

## 3. Funcionalidades del sistema

El sistema permite realizar las siguientes operaciones:

### Registrar socios

Permite dar de alta nuevos socios ingresando nombre, apellido, DNI, correo electrónico, teléfono, plan y fecha de alta.

Se realizan validaciones para evitar registros incorrectos o duplicados.

### Gestionar planes

El gimnasio cuenta con tres planes de membresía:

| Plan | Código | Importe |
|---|---|---:|
| Mensual | M | $10.000 |
| Trimestral | T | $27.000 |
| Anual | A | $102.000 |

Los planes trimestral y anual incluyen descuentos del 10% y 15%, respectivamente, sobre el importe correspondiente a sus períodos.

El sistema permite cambiar el plan de un socio y recalcular su cuota.

### Registrar pagos

Permite registrar pagos y actualizar el estado del socio.

Los pagos realizados después del día 10 tienen un recargo del 10%.

Cuando el importe abonado es suficiente, el socio pasa al estado `activo`.

### Reportar socios morosos

Genera un listado de socios con pagos pendientes e informa el importe total adeudado.

### Persistencia de datos

La información de socios y pagos se almacena en archivos JSON, permitiendo conservar los registros entre ejecuciones.

## 4. Estructura del repositorio

```text
TPI_MetodologiaII_2026/
│
├── Antes/
│   ├── gimnasio.py
│   └── test_gimnasio.py
│
├── Despues/
│   ├── gimnasio.py
│   └── test_gimnasio.py
│
├── docs/
│   └── diagnostico.md
│
└── README.md
```

**Antes:** contiene la implementación inicial del sistema, utilizada como punto de partida para identificar los problemas de calidad.

**Despues:** contiene la versión refactorizada, con una mejor distribución de responsabilidades, abstracciones y pruebas adicionales.

**docs:** contiene documentación técnica relacionada con el diagnóstico, las mejoras y las decisiones de diseño.

## 5. Diagnóstico inicial

En la implementación original se identificaron diferentes problemas de calidad interna:

| Problema | Consecuencia |
|---|---|
| Clase con múltiples responsabilidades | Dificulta el mantenimiento |
| Código duplicado | Aumenta el riesgo de inconsistencias |
| Variables poco descriptivas | Reduce la legibilidad |
| Valores hardcodeados | Dificulta modificar reglas de negocio |
| Demasiados parámetros | Complica las operaciones |
| Persistencia mezclada con negocio | Genera alto acoplamiento |
| Manejo genérico de excepciones | Puede ocultar errores |

Estos problemas representan deuda técnica porque aumentan el costo y el riesgo de introducir futuras modificaciones.

## 6. Refactoring aplicado

El código fue reorganizado para mejorar su estructura interna, manteniendo el comportamiento existente.

### Extract Method

Se extrajeron operaciones específicas, como la búsqueda de socios y el cálculo de cuotas, para evitar duplicación y mejorar la legibilidad.

### Introduce Parameter Object

Se incorporó `DatosAltaSocio`, utilizando `@dataclass`, para agrupar los datos necesarios para registrar un socio.

Esto permite trabajar con un objeto estructurado en lugar de depender exclusivamente de múltiples parámetros individuales.

### Move Method

Se trasladaron las responsabilidades del reporte de morosos a la clase `ReporteMorosos`.

Así, el servicio principal deja de concentrar la construcción del reporte.

### Separación de persistencia

Se incorporó una interfaz `RepositorioDatos` y una implementación `RepositorioJson`.

De esta manera, la lógica de negocio puede trabajar con diferentes mecanismos de almacenamiento.

### Manejo de errores

Se incorporaron excepciones específicas:

- `ErrorPersistencia`
- `ArchivoDatosInvalidoError`

Esto permite identificar con mayor claridad los problemas relacionados con la lectura y escritura de archivos.

## 7. Principios SOLID

La versión refactorizada incorpora los siguientes principios:

| Principio | Aplicación |
|---|---|
| SRP – Responsabilidad Única | Separación entre planes, persistencia, reportes y gestión de socios |
| OCP – Abierto/Cerrado | Los nuevos tipos de planes pueden implementarse mediante nuevas clases |
| LSP – Sustitución de Liskov | Las implementaciones de `Plan` respetan el contrato común de cálculo |
| ISP – Segregación de Interfaces | Se utilizan contratos acotados para los planes y repositorios |
| DIP – Inversión de Dependencias | `GimnasioService` depende de `RepositorioDatos` y no directamente de JSON |

Esta organización mejora la extensibilidad, testabilidad y mantenibilidad del sistema.

## 8. Patrones de diseño

### Strategy

Se utiliza para implementar los diferentes planes de membresía.

La clase abstracta `Plan` define el método `calcular_cuota()`, que es implementado por:

- `PlanMensual`
- `PlanTrimestral`
- `PlanAnual`

Cada clase encapsula su propia regla de cálculo.

Esto permite incorporar nuevos planes sin modificar la lógica de cálculo de los existentes.

### Inyección de dependencias

`GimnasioService` permite recibir un repositorio externo mediante su constructor.

Esto facilita reemplazar la persistencia JSON por una implementación alternativa, como un repositorio en memoria para pruebas.

## 9. Tecnologías utilizadas

| Tecnología | Propósito |
|---|---|
| Python 3.11 | Desarrollo del sistema |
| pytest | Pruebas automatizadas |
| JSON | Almacenamiento de información |
| dataclasses | Agrupación estructurada de datos |
| abc | Definición de clases abstractas e interfaces |

No se requiere una base de datos externa para ejecutar el proyecto.

## 10. Instalación y ejecución

### Requisitos previos

- Python 3.11
- pip
- Git (para clonar el repositorio)

### Clonar el repositorio

```bash
git clone https://github.com/hcasalderrey/TPI_MetodologiaII_2026.git
```

Ingresar al directorio:

```bash
cd TPI_MetodologiaII_2026
```

### Instalar pytest

```bash
python -m pip install pytest
```

### Ejecutar la versión original

```bash
cd Antes
python gimnasio.py
```

### Ejecutar la versión refactorizada

Desde la raíz del proyecto:

```bash
cd Despues
python gimnasio.py
```

La ejecución utiliza un escenario demostrativo con datos ficticios.

## 11. Pruebas automatizadas

Las pruebas se realizaron utilizando `pytest`.

Para ejecutar las pruebas de la versión refactorizada:

```bash
cd Despues
python -m pytest -v
```

Para ejecutar las pruebas de la versión original:

```bash
cd Antes
python -m pytest -v
```

Los casos de prueba contemplan:

- Registro válido de socios.
- Validación de DNI y correo electrónico.
- Prevención de socios duplicados.
- Cálculo de cuotas y descuentos.
- Cambios de planes.
- Registro de pagos.
- Recargos por pagos tardíos.
- Generación del reporte de morosos.
- Persistencia de información.
- Manejo de errores de almacenamiento.
- Uso de repositorios alternativos.
- Funcionamiento independiente de las estrategias de planes.

Las pruebas permiten comprobar que el refactoring conserva los comportamientos principales de la implementación original y que los nuevos componentes funcionan correctamente.

## 12. Integración de las ramas

Durante el desarrollo se trabajó con distintas ramas:

- `tpi/diagnostico-y-refactoring`
- `tpi/mejoras-refactoring`
- `tpi/solid-refactoring`

Los cambios de estas ramas se encuentran incorporados en `main`, que contiene la versión consolidada del trabajo.

La estructura `Antes/` y `Despues/` se conserva intencionalmente para permitir comparar la implementación original con la refactorizada.

## 13. Resultados y conclusiones

El trabajo permitió aplicar conceptos de calidad y diseño de software sobre un caso práctico.

Las principales mejoras fueron:

- Mayor claridad y organización del código.
- Reducción de lógica duplicada.
- Separación de responsabilidades.
- Menor acoplamiento entre componentes.
- Mayor facilidad para realizar pruebas.
- Mejor manejo de errores.
- Posibilidad de incorporar nuevos planes.
- Mayor mantenibilidad y extensibilidad.

**Conclusión:** un sistema puede funcionar correctamente desde el punto de vista del usuario y, aun así, presentar problemas de calidad interna.

La aplicación de Clean Code, refactoring, principios SOLID y patrones de diseño permite mejorar la estructura del software y reducir el costo de futuros cambios sin alterar las funcionalidades existentes.

---

## 14. Integrantes

Trabajo Práctico Integrador – Metodología de Sistemas II

**Tecnicatura Universitaria en Programación – UTN**

**Ciclo lectivo:** 2026

**Integrantes:**

- Gonzalo Castellini
- Hernán Casalderrey
- Lautaro Buchek
  
Comisión: 4
Docente: Lobos Diego

Link a video: https://youtu.be/ZHZbdamoZ_w

Fecha de entrega: 08/11/2026

