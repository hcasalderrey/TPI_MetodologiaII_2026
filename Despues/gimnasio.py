import json
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass

#Constantes utilizadas en el proyecto
CUOTA_BASE = 10_000

MESES_PLAN_TRIMESTRAL = 3
FACTOR_PLAN_TRIMESTRAL = 0.90

MESES_PLAN_ANUAL = 12
FACTOR_PLAN_ANUAL = 0.85

PLAN_MENSUAL = "M"
PLAN_TRIMESTRAL = "T"
PLAN_ANUAL = "A"

DIA_LIMITE_PAGO = 10
FACTOR_RECARGO_PAGO_TARDIO = 1.10

LONGITUD_DNI = 8

ESTADO_MOROSO = "moroso"
ESTADO_ACTIVO = "activo"

ARCHIVO_POR_DEFECTO = "datos.json"

#Excepciones propias para manejo de errores
class ErrorPersistencia(Exception):
    """Error general relacionado con la persistencia de datos."""


class ArchivoDatosInvalidoError(ErrorPersistencia):
    """El archivo existe, pero no contiene JSON válido."""

@dataclass(frozen=True)
class DatosAltaSocio:
    nombre: str
    apellido: str
    dni: str
    email: str
    telefono: str
    plan: str
    fecha_alta: str

#Planes (Strategy): un plan nuevo es una clase nueva, sin tocar el service
class Plan(ABC):
    @abstractmethod
    def calcular_cuota(self):
        """Devuelve la cuota que paga el socio con este plan."""


class PlanMensual(Plan):
    def calcular_cuota(self):
        return CUOTA_BASE


class PlanTrimestral(Plan):
    def calcular_cuota(self):
        return round(CUOTA_BASE * MESES_PLAN_TRIMESTRAL * FACTOR_PLAN_TRIMESTRAL, 2)


class PlanAnual(Plan):
    def calcular_cuota(self):
        return round(CUOTA_BASE * MESES_PLAN_ANUAL * FACTOR_PLAN_ANUAL, 2)


PLANES = {
    PLAN_MENSUAL: PlanMensual(),
    PLAN_TRIMESTRAL: PlanTrimestral(),
    PLAN_ANUAL: PlanAnual(),
}


class RepositorioJson:
    def __init__(self, archivo):
        self.archivo = archivo

    def cargar(self):
        if not os.path.exists(self.archivo):
            return {"socios": [], "pagos": []}

        try:
            with open(self.archivo, encoding="utf-8") as archivo:
                return json.load(archivo)
        except json.JSONDecodeError as error:
            raise ArchivoDatosInvalidoError(
                f"El archivo '{self.archivo}' contiene JSON inválido"
            ) from error
        except OSError as error:
            raise ErrorPersistencia(
                f"No fue posible leer el archivo '{self.archivo}'"
            ) from error

    def guardar(self, datos):
        try:
            with open(self.archivo, "w", encoding="utf-8") as archivo:
                json.dump(datos, archivo)
        except OSError as error:
            raise ErrorPersistencia(
                f"No fue posible guardar los datos en '{self.archivo}'"
            ) from error

class GimnasioService:
    def __init__(self, archivo=ARCHIVO_POR_DEFECTO):
        self.repositorio = RepositorioJson(archivo)
        self.datos = self.repositorio.cargar()

    def _calcular_cuota(self, codigo_plan):
        plan = PLANES.get(codigo_plan)
        if plan is None:
            return None
        return plan.calcular_cuota()


    def _buscar_socio(self, dni):
        for socio in self.datos["socios"]:
            if socio["dni"] == dni:
                return socio
        return None

    def registrar_socio(self, nombre, apellido, dni, email, telefono, plan, fecha_alta):
        datos_alta = DatosAltaSocio(nombre, apellido, dni, email, telefono, plan, fecha_alta)
        return self.registrar_socio_con_datos(datos_alta)

    def registrar_socio_con_datos(self, datos_alta: DatosAltaSocio):
        if datos_alta.nombre == "" or datos_alta.apellido == "":
            print("Error: nombre invalido")
            return None
        if len(datos_alta.dni) != LONGITUD_DNI or not datos_alta.dni.isdigit():
            print("Error: DNI invalido")
            return None
        if "@" not in datos_alta.email or "." not in datos_alta.email:
            print("Error: email invalido")
            return None
        if self._buscar_socio(datos_alta.dni) is not None:
            print("Error: DNI ya registrado")
            return None

        cuota = self._calcular_cuota(datos_alta.plan)
        if cuota is None:
            print("Error: plan invalido")
            return None

        socio = {
            "nombre": datos_alta.nombre,
            "apellido": datos_alta.apellido,
            "dni": datos_alta.dni,
            "email": datos_alta.email,
            "telefono": datos_alta.telefono,
            "plan": datos_alta.plan,
            "cuota": cuota,
            "estado": ESTADO_MOROSO,
            "fecha_alta": datos_alta.fecha_alta,
        }
        self.datos["socios"].append(socio)
        self.repositorio.guardar(self.datos)
        print(
            "Socio registrado: "
            + datos_alta.nombre + " " + datos_alta.apellido + " - cuota $" + str(cuota)
        )
        return socio

    def cambiar_plan(self, dni, plan_nuevo):
        if len(dni) != LONGITUD_DNI or not dni.isdigit():
            print("Error: DNI invalido")
            return None
        socio = self._buscar_socio(dni)
        if socio == None:
            print("Error: socio no existe")
            return None

        cuota = self._calcular_cuota(plan_nuevo)
        if cuota is None:
            print("Error: plan invalido")
            return None
        socio["plan"] = plan_nuevo
        socio["cuota"] = cuota
        self.repositorio.guardar(self.datos)
        print("Plan cambiado: " + socio["nombre"] + " - nueva cuota $" + str(cuota))
        return socio

    def registrar_pago(self, dni, monto, dia):
        if len(dni) != LONGITUD_DNI or not dni.isdigit():
            print("Error: DNI invalido")
            return None
        socio = self._buscar_socio(dni)
        if socio == None:
            print("Error: socio no existe")
            return None
        debido = socio["cuota"]
        if dia > DIA_LIMITE_PAGO:
            debido = round(debido * FACTOR_RECARGO_PAGO_TARDIO, 2)
        if monto < debido:
            print("Error: monto insuficiente, se debe $" + str(debido))
            return None
        pago = {"dni": dni, "monto": monto, "dia": dia}
        self.datos["pagos"].append(pago)
        socio["estado"] = ESTADO_ACTIVO
        self.repositorio.guardar(self.datos)
        print("Pago registrado: " + socio["nombre"] + " - $" + str(monto))
        return pago

    def reporte_morosos(self):
        socios_morosos = []
        total_adeudado = 0
        for socio in self.datos["socios"]:
            if socio["estado"] == ESTADO_MOROSO:
                socios_morosos.append(socio["apellido"] + ", " + socio["nombre"] + " (" + socio["dni"] + ") debe $" + str(socio["cuota"]))
                total_adeudado += socio["cuota"]
        print("=== MOROSOS ===")
        for reporte in socios_morosos:
            print(reporte)
        print("Total adeudado: $" + str(total_adeudado))
        return socios_morosos


if __name__ == "__main__":
    # demo: escenario fijo, datos inventados
    if os.path.exists("datos_demo.json"):
        os.remove("datos_demo.json")
    gimnasio = GimnasioService("datos_demo.json")
    gimnasio.registrar_socio("Ana", "Perez", "11111111", "ana@mail.com", "1111", "M", "2026-10-01")
    gimnasio.registrar_socio("Luis", "Gomez", "22222222", "luis@mail.com", "2222", "T", "2026-10-02")
    gimnasio.registrar_socio("Marta", "Diaz", "33333333", "marta@mail.com", "3333", "A", "2026-10-03")
    gimnasio.registrar_socio("Pedro", "Ruiz", "abc", "pedro@mail.com", "4444", "M", "2026-10-04")
    gimnasio.cambiar_plan("11111111", "A")
    gimnasio.registrar_pago("22222222", 27000, 5)
    gimnasio.registrar_pago("33333333", 102000, 15)
    gimnasio.registrar_pago("33333333", 112200, 15)
    gimnasio.reporte_morosos()
