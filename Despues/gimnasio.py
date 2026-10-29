import json
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class DatosAltaSocio:
    nombre: str
    apellido: str
    dni: str
    email: str
    telefono: str
    plan: str
    fecha_alta: str

class RepositorioJson:
    def __init__(self, archivo):
        self.archivo = archivo

    def cargar(self):
        if not os.path.exists(self.archivo):
            return {"socios": [], "pagos": []}
        try:
            with open(self.archivo, encoding="utf-8") as archivo:
                return json.load(archivo)
        except:
            print("error leyendo archivo")
            return {"socios": [], "pagos": []}

    def guardar(self, datos):
        with open(self.archivo, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo)

class GimnasioService:
    def __init__(self, archivo="datos.json"):
        self.repositorio = RepositorioJson(archivo)
        self.d = self.repositorio.cargar()

    def _calcular_cuota(self, plan):
        if plan == "M":
            return 10000
        elif plan == "T":
            return round(10000 * 3 * 0.90, 2)
        elif plan == "A":
            return round(10000 * 12 * 0.85, 2)
        return None
    def _buscar_socio(self, dni):
        for socio in self.d["socios"]:
            if socio["dni"] == dni:
                return socio
        return None

    def registrar_socio(self, nombre, apellido, dni, email, telefono, plan, fecha_alta):
        datos = DatosAltaSocio(nombre, apellido, dni, email, telefono, plan, fecha_alta)
        return self.registrar_socio_con_datos(datos)

    def registrar_socio_con_datos(self, datos: DatosAltaSocio):
        if datos.nombre == "" or datos.apellido == "":
            print("Error: nombre invalido")
            return None
        if len(datos.dni) != 8 or not datos.dni.isdigit():
            print("Error: DNI invalido")
            return None
        if "@" not in datos.email or "." not in datos.email:
            print("Error: email invalido")
            return None
        if self._buscar_socio(datos.dni) is not None:
            print("Error: DNI ya registrado")
            return None

        cuota = self._calcular_cuota(datos.plan)
        if cuota is None:
            print("Error: plan invalido")
            return None

        socio = {
            "nombre": datos.nombre,
            "apellido": datos.apellido,
            "dni": datos.dni,
            "email": datos.email,
            "telefono": datos.telefono,
            "plan": datos.plan,
            "cuota": cuota,
            "estado": "moroso",
            "fecha_alta": datos.fecha_alta,
        }
        self.d["socios"].append(socio)
        self.repositorio.guardar(self.d)
        print(
            "Socio registrado: "
            + datos.nombre + " " + datos.apellido + " - cuota $" + str(cuota)
        )
        return socio

    def cambiar_plan(self, dni, plan_nuevo):
        if len(dni) != 8 or not dni.isdigit():
            print("Error: DNI invalido")
            return None
        socio = self._buscar_socio(dni)
        if socio == None:
            print("Error: socio no existe")
            return None

        c = self._calcular_cuota(plan_nuevo)
        if c is None:
            print("Error: plan invalido")
            return None
        socio["plan"] = plan_nuevo
        socio["cuota"] = c
        self.repositorio.guardar(self.d)
        print("Plan cambiado: " + socio["nombre"] + " - nueva cuota $" + str(c))
        return socio

    def registrar_pago(self, dni, monto, dia):
        if len(dni) != 8 or not dni.isdigit():
            print("Error: DNI invalido")
            return None
        socio = self._buscar_socio(dni)
        if socio == None:
            print("Error: socio no existe")
            return None
        debido = socio["cuota"]
        if dia > 10:
            debido = round(debido * 1.10, 2)
        if monto < debido:
            print("Error: monto insuficiente, se debe $" + str(debido))
            return None
        p = {"dni": dni, "monto": monto, "dia": dia}
        self.d["pagos"].append(p)
        socio["estado"] = "activo"
        self.repositorio.guardar(self.d)
        print("Pago registrado: " + socio["nombre"] + " - $" + str(monto))
        return p

    def reporte_morosos(self):
        lst = []
        t = 0
        for s in self.d["socios"]:
            if s["estado"] == "moroso":
                lst.append(s["apellido"] + ", " + s["nombre"] + " (" + s["dni"] + ") debe $" + str(s["cuota"]))
                t = t + s["cuota"]
        print("=== MOROSOS ===")
        for r in lst:
            print(r)
        print("Total adeudado: $" + str(t))
        return lst


if __name__ == "__main__":
    # demo: escenario fijo, datos inventados
    if os.path.exists("datos_demo.json"):
        os.remove("datos_demo.json")
    g = GimnasioService("datos_demo.json")
    g.registrar_socio("Ana", "Perez", "11111111", "ana@mail.com", "1111", "M", "2026-10-01")
    g.registrar_socio("Luis", "Gomez", "22222222", "luis@mail.com", "2222", "T", "2026-10-02")
    g.registrar_socio("Marta", "Diaz", "33333333", "marta@mail.com", "3333", "A", "2026-10-03")
    g.registrar_socio("Pedro", "Ruiz", "abc", "pedro@mail.com", "4444", "M", "2026-10-04")
    g.cambiar_plan("11111111", "A")
    g.registrar_pago("22222222", 27000, 5)
    g.registrar_pago("33333333", 102000, 15)
    g.registrar_pago("33333333", 112200, 15)
    g.reporte_morosos()
