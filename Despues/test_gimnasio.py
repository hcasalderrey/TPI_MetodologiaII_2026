import pytest

from gimnasio import (
    ArchivoDatosInvalidoError,
    DatosAltaSocio,
    ErrorPersistencia,
    GimnasioService,
    PlanAnual,
    PlanMensual,
    PlanTrimestral,
    RepositorioDatos,
    RepositorioJson,
    ReporteMorosos,
    dni_es_valido,
    email_es_valido,
)


@pytest.fixture
def g(tmp_path):
    return GimnasioService(str(tmp_path / "datos.json"))


def alta(g, dni="11111111", plan="M"):
    return g.registrar_socio("Ana", "Perez", dni, "ana@mail.com", "1111", plan, "2026-10-01")


def test_alta_valida_plan_mensual(g):
    socio = alta(g)
    assert socio["cuota"] == 10000
    assert socio["estado"] == "moroso"


def test_cuota_trimestral_y_anual_con_descuento(g):
    assert alta(g, "11111111", "T")["cuota"] == 27000
    assert alta(g, "22222222", "A")["cuota"] == 102000


def test_alta_rechaza_dni_invalido_duplicado_plan_invalido(g):
    alta(g)
    assert alta(g, "abc") is None
    assert alta(g) is None
    assert alta(g, "22222222", "X") is None


def test_alta_rechaza_email_invalido(g):
    assert g.registrar_socio("Ana", "Perez", "11111111", "sin-arroba", "1", "M", "2026-10-01") is None


def test_cambiar_plan_recalcula_cuota(g):
    alta(g)
    assert g.cambiar_plan("11111111", "A")["cuota"] == 102000
    assert g.cambiar_plan("99999999", "M") is None


def test_pago_a_tiempo_activa_al_socio(g):
    alta(g)
    assert g.registrar_pago("11111111", 10000, 5) is not None
    assert g.reporte_morosos() == []


def test_pago_tardio_exige_recargo_del_10_por_ciento(g):
    alta(g)
    assert g.registrar_pago("11111111", 10000, 15) is None
    assert g.registrar_pago("11111111", 11000, 15) is not None


def test_reporte_lista_morosos(g):
    alta(g, "11111111", "M")
    g.registrar_socio("Luis", "Gomez", "22222222", "luis@mail.com", "2", "T", "2026-10-02")
    g.registrar_pago("22222222", 27000, 3)
    assert g.reporte_morosos() == ["Perez, Ana (11111111) debe $10000"]


def test_los_datos_persisten_en_archivo(tmp_path):
    ruta = str(tmp_path / "datos.json")
    alta(GimnasioService(ruta))
    assert len(GimnasioService(ruta).datos["socios"]) == 1

def test_alta_con_objeto_de_datos(g):
    datos = DatosAltaSocio(
        nombre="Ana",
        apellido="Perez",
        dni="11111111",
        email="ana@mail.com",
        telefono="1111",
        plan="M",
        fecha_alta="2026-10-01",
    )

    socio = g.registrar_socio_con_datos(datos)

    assert socio["dni"] == "11111111"
    assert socio["cuota"] == 10000
    assert len(g.datos["socios"]) == 1

#Pruebas sobre excepciones
def test_repositorio_inicializa_datos_vacios_si_archivo_no_existe(tmp_path):
    ruta = tmp_path / "inexistente.json"
    repositorio = RepositorioJson(str(ruta))

    datos = repositorio.cargar()

    assert datos == {"socios": [], "pagos": []}


def test_repositorio_informa_error_si_json_es_invalido(tmp_path):
    ruta = tmp_path / "datos.json"
    ruta.write_text("{contenido inválido", encoding="utf-8")
    repositorio = RepositorioJson(str(ruta))

    with pytest.raises(
        ArchivoDatosInvalidoError,
        match="contiene JSON inválido",
    ):
        repositorio.cargar()


def test_repositorio_informa_error_si_no_puede_guardar(tmp_path):
    repositorio = RepositorioJson(str(tmp_path))

    with pytest.raises(
        ErrorPersistencia,
        match="No fue posible guardar",
    ):
        repositorio.guardar({"socios": [], "pagos": []})

#Pruebas de los refactorings estructurales
def test_cada_plan_calcula_su_cuota():
    assert PlanMensual().calcular_cuota() == 10000
    assert PlanTrimestral().calcular_cuota() == 27000
    assert PlanAnual().calcular_cuota() == 102000


def test_service_funciona_con_repositorio_inyectado_en_memoria():
    class RepositorioEnMemoria(RepositorioDatos):
        def __init__(self):
            self.guardado = None

        def cargar(self):
            return {"socios": [], "pagos": []}

        def guardar(self, datos):
            self.guardado = datos

    repositorio = RepositorioEnMemoria()
    servicio = GimnasioService(repositorio=repositorio)

    alta(servicio)

    assert repositorio.guardado["socios"][0]["dni"] == "11111111"


def test_validaciones_compartidas():
    assert dni_es_valido("12345678")
    assert not dni_es_valido("1234")
    assert not dni_es_valido("abcdefgh")
    assert email_es_valido("ana@mail.com")
    assert not email_es_valido("sin-arroba")


def test_reporte_morosos_calcula_lineas_y_total():
    socios = [
        {"apellido": "Perez", "nombre": "Ana", "dni": "11111111", "cuota": 10000, "estado": "moroso"},
        {"apellido": "Gomez", "nombre": "Luis", "dni": "22222222", "cuota": 27000, "estado": "activo"},
    ]
    reporte = ReporteMorosos(socios)

    assert reporte.lineas() == ["Perez, Ana (11111111) debe $10000"]
    assert reporte.total_adeudado() == 10000
