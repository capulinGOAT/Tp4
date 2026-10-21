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
