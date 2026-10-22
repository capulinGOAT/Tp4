from datetime import date

import pytest

import pedidos
from checkout import CheckoutError
from decimal import Decimal

HOY_VIGENTE = date(2026, 10, 1)


@pytest.fixture
def ruta(tmp_path):
    return str(tmp_path / "tienda.db")


@pytest.fixture
def con(ruta):
    conexion = pedidos.conectar(ruta)
    pedidos.crear_esquema(conexion)
    yield conexion
    conexion.close()


def item(producto="buzo", talle="M", cantidad=1, **extra):
    return {"producto": producto, "talle": talle, "cantidad": cantidad, **extra}


def contar(ruta, tabla):
    assert tabla in ("pedidos", "items")
    otra = pedidos.conectar(ruta)
    try:
        return otra.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0]
    finally:
        otra.close()


def guardar(con, email="ana@mail.com", carrito=None, zona="CABA", cupon=None, fecha=HOY_VIGENTE):
    # Si tu firma es distinta, ajustá solo esta línea.
    if carrito is None:
        carrito = [item()]
    return pedidos.guardar_pedido(con, email, carrito, zona, cupon=cupon, fecha=fecha)


# 1. Atomicidad: un error en el ítem 2 no deja nada guardado
def test_talle_invalido_en_el_item_2_no_deja_nada_guardado(ruta, con):
    carrito = [item("buzo", "M", 1), item("remera", "XXXL", 1)]
    with pytest.raises(CheckoutError) as exc:
        guardar(con, carrito=carrito)
    e = exc.value
    assert "TALLE_INVALIDO" in (getattr(e, "code", None), getattr(e, "codigo", None), str(e)) \
        or "TALLE_INVALIDO" in str(e)
    assert contar(ruta, "pedidos") == 0
    assert contar(ruta, "items") == 0


# 2. El pedido es definitivo: lo ve otra conexión, con todos sus ítems
def test_otra_conexion_ve_el_pedido_completo(ruta, con):
    carrito = [item("buzo", "M", 1), item("remera", "L", 2), item("campera", "S", 1)]
    id_ = guardar(con, carrito=carrito)
    otra = pedidos.conectar(ruta)
    try:
        pedido = pedidos.obtener_pedido(otra, id_)
    finally:
        otra.close()
    assert pedido is not None
    assert pedido["id"] == id_
    assert len(pedido["items"]) == 3


# 3. Precio del catálogo: el precio del cliente se ignora
def test_el_precio_enviado_por_el_cliente_se_ignora(con):
    id_ = guardar(con, carrito=[item("buzo", "M", 1, precio=1)])
    p = pedidos.obtener_pedido(con, id_)
    assert p is not None
    assert p["items"][0]["precio_unitario"] == Decimal("24999.90")
    assert p["subtotal"] == Decimal("24999.90")


# 4. Inyección SQL: una consulta extra no destruye la tabla
def test_inyeccion_sql_con_consulta_extra(ruta, con):
    guardar(con, email="ana@mail.com")
    guardar(con, email="bruno@mail.com")
    assert pedidos.pedidos_de(con, "x'; DROP TABLE pedidos; --") == []
    assert contar(ruta, "pedidos") == 2