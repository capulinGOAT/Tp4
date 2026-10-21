from datetime import date
from decimal import Decimal

import pytest

from checkout import (
    CheckoutError,
    calcular_descuento,
    calcular_envio,
    calcular_subtotal,
    calcular_total,
    validar_item,
)

HOY_VIGENTE = date(2026, 10, 1)


def item(producto="buzo", talle="M", cantidad=1, **extra):
    return {"producto": producto, "talle": talle, "cantidad": cantidad, **extra}


def codigo_de_error(funcion, *args):
    with pytest.raises(CheckoutError) as error:
        funcion(*args)
    return error.value.code


def test_cantidad_cero_es_invalida():
    assert codigo_de_error(validar_item, item(cantidad=0)) == "CANTIDAD_INVALIDA"

def test_cantidad_10_es_valida():
    validar_item({"producto": "buzo", "talle": "M", "cantidad": 10})

def test_validar_item_no_modifica_diccionario_original():
    item_original = {"producto": "buzo", "talle": "  m  ", "cantidad": 1}
    item_copia = dict(item_original)
    validar_item(item_original)
    assert item_original == item_copia

def test_calcular_subtotal_ignora_precio_enviado_por_cliente():
    items = [{"producto": "buzo", "talle": "M", "cantidad": 1, "precio": Decimal("1.00")}]
    subtotal = calcular_subtotal(items)
    assert subtotal == Decimal("24999.90")

def test_aplicar_cupon_acepta_minusculas():
    subtotal = Decimal("10000.00")
    descuento = calcular_descuento(subtotal, 1, "egresados2026", date(2026, 10, 1))
    assert descuento == Decimal("1500.00")

def test_cupon_vencido_lanza_error():
    subtotal = Decimal("10000.00")
    # El cupón "EGRESADOS2026" vence el 2026-12-31, así que para el 2027-01-01 ya está vencido
    try:
        calcular_descuento(subtotal, 1, "EGRESADOS2026", date(2027, 1, 1))
        assert False, "Debería haber lanzado CheckoutError por cupón vencido"
    except CheckoutError as e:
        assert e.codigo == "CUPON_VENCIDO"