import json
import threading
import urllib.error
import urllib.request

import pytest

import api

RUTA = "/api/v1/pedidos"


@pytest.fixture
def url(tmp_path):
    servidor = api.crear_servidor(str(tmp_path / "tienda.db"), 0)
    threading.Thread(target=servidor.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True).start()
    yield f"http://127.0.0.1:{servidor.server_address[1]}"
    servidor.shutdown()
    servidor.server_close()


def pedir(url, metodo, ruta, cuerpo=None, crudo=None):
    datos = crudo if crudo is not None else (json.dumps(cuerpo).encode() if cuerpo is not None else None)
    req = urllib.request.Request(url + ruta, data=datos, method=metodo,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, json.loads(r.read() or b"null")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"null")


def compra(**cambios):
    cuerpo = {"email": "ana@mail.com", "zona": "CABA",
              "carrito": [{"producto": "buzo", "talle": "M", "cantidad": 1}]}
    cuerpo.update(cambios)
    return cuerpo


def assert_error(cuerpo, codigo):
    assert set(cuerpo) == {"error"}
    assert set(cuerpo["error"]) == {"code", "message"}
    assert cuerpo["error"]["code"] == codigo
    assert isinstance(cuerpo["error"]["message"], str) and cuerpo["error"]["message"]


# ---------- Un test por endpoint ----------

def test_post_crea_un_pedido(url):
    status, cuerpo = pedir(url, "POST", RUTA, compra(
        carrito=[{"producto": "remera", "talle": "M", "cantidad": 1}],
        cupon="EGRESADOS2026", fecha="2026-11-30"))
    assert status == 201
    assert isinstance(cuerpo["id"], int)
    assert cuerpo == {"id": cuerpo["id"], "subtotal": "11999.50", "descuento": "1799.93",
                      "envio": "2500.00", "total": "12699.57"}


def test_get_devuelve_el_pedido(url):
    _, creado = pedir(url, "POST", RUTA, compra())
    status, pedido = pedir(url, "GET", f"{RUTA}/{creado['id']}")
    assert status == 200
    assert set(pedido) == {"id", "email", "zona", "cupon", "subtotal", "descuento", "envio", "total", "items"}
    assert pedido["id"] == creado["id"]
    assert pedido["total"] == creado["total"]


# ---------- 4 errores de R11 ----------

def test_json_invalido_400(url):
    status, cuerpo = pedir(url, "POST", RUTA, crudo=b"no es json")
    assert status == 400
    assert_error(cuerpo, "JSON_INVALIDO")


def test_datos_incompletos_400_email_de_otro_tipo(url):
    status, cuerpo = pedir(url, "POST", RUTA, compra(email=123))
    assert status == 400
    assert_error(cuerpo, "DATOS_INCOMPLETOS")


def test_talle_invalido_422(url):
    status, cuerpo = pedir(url, "POST", RUTA, compra(
        carrito=[{"producto": "buzo", "talle": "XXXL", "cantidad": 1}]))
    assert status == 422
    assert_error(cuerpo, "TALLE_INVALIDO")


def test_pedido_inexistente_404(url):
    status, cuerpo = pedir(url, "GET", f"{RUTA}/999")
    assert status == 404
    assert_error(cuerpo, "PEDIDO_INEXISTENTE")
