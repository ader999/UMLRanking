import requests
from typing import Optional, Dict, Any, List

try:
    from .session_manager import save_session, load_session, clear_session, save_last_server, load_last_server
except (ImportError, ValueError):
    from session_manager import save_session, load_session, clear_session, save_last_server, load_last_server


DEFAULT_TIMEOUT = 25  # 25 segundos para tolerar inicios en frío en Railway y variaciones móviles


class APIClient:
    """
    Cliente HTTP para interactuar con los endpoints DRF del backend de eventos.
    Maneja autenticación por Token, URLs base, persistencia de sesión por 1 mes y manejo seguro de errores de red.
    """
    def __init__(self, base_url: str = "https://planeauml.codeader.com", timeout: int = DEFAULT_TIMEOUT):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.last_error: Optional[str] = None

        self.token: Optional[str] = None
        self.user: Optional[Dict[str, Any]] = None
        self.session = requests.Session()

    def set_base_url(self, new_url: str):
        self.base_url = new_url.rstrip("/")

    def set_token(self, token: Optional[str]):
        self.token = token
        if token:
            self.session.headers.update({"Authorization": f"Token {token}"})
        else:
            self.session.headers.pop("Authorization", None)

    def load_stored_session(self) -> bool:
        """
        Carga la sesión guardada si existe y es válida (vigencia: 1 mes / 30 días).
        Configura automáticamente base_url, token y usuario.
        """
        data = load_session()
        if data and data.get("token") and data.get("user"):
            if data.get("base_url"):
                self.set_base_url(data["base_url"])
            self.set_token(data["token"])
            self.user = data["user"]
            return True
        return False

    def _parse_error(self, resp) -> Dict[str, Any]:
        """Extrae el mensaje de error o sanea respuestas HTML (errores 500 de Django con DEBUG=True)."""
        try:
            return resp.json()
        except Exception:
            text = (resp.text or "").strip()
            if "<title>" in text and "</title>" in text:
                title = text.split("<title>")[1].split("</title>")[0].strip()
                title = " ".join(title.split())
                return {"detail": f"Error en servidor ({resp.status_code}): {title}"}
            if text.startswith("<!DOCTYPE") or "<html" in text:
                return {"detail": f"Error del servidor ({resp.status_code}): El backend respondió con una página de error."}
            return {"detail": text[:200] or f"Error HTTP {resp.status_code}"}

    def _request(self, method: str, url: str, **kwargs) -> Optional[requests.Response]:
        """
        Ejecuta una petición HTTP asegurando timeout adecuado y capturando
        todas las excepciones de red (Timeout, ConnectionError, etc.) para evitar caídas de la app.
        """
        if "timeout" not in kwargs:
            kwargs["timeout"] = self.timeout
        self.last_error = None
        try:
            m = method.upper()
            if m == "GET":
                return self.session.get(url, **kwargs)
            elif m == "POST":
                return self.session.post(url, **kwargs)
            elif m == "PUT":
                return self.session.put(url, **kwargs)
            elif m == "DELETE":
                return self.session.delete(url, **kwargs)
            return self.session.request(method, url, **kwargs)
        except requests.exceptions.Timeout:
            self.last_error = "El servidor tardó demasiado en responder (Tiempo de espera agotado)."
            return None
        except requests.exceptions.ConnectionError:
            self.last_error = "No se pudo conectar con el servidor. Verifica tu conexión a internet o el estado del backend."
            return None
        except requests.exceptions.RequestException as e:
            self.last_error = f"Error en la conexión con el servidor: {e}"
            return None
        except Exception as e:
            self.last_error = f"Error inesperado de red: {e}"
            return None

    def login(self, username: str, password: str) -> Dict[str, Any]:
        username = (username or "").strip()
        password = (password or "").strip()
        url = f"{self.base_url}/api/eventos/auth/login/"
        resp = self._request("POST", url, json={"username": username, "password": password})
        if resp is None:
            return {"success": False, "error": {"detail": self.last_error or "No se pudo conectar al servidor."}}

        if resp.status_code == 200:
            data = resp.json()
            self.set_token(data.get("token"))
            self.user = data.get("user")
            save_session(self.token, self.user, base_url=self.base_url)
            save_last_server(self.base_url)
            return {"success": True, "data": data}
        return {"success": False, "error": self._parse_error(resp)}

    def logout(self) -> Dict[str, Any]:
        clear_session()
        url = f"{self.base_url}/api/eventos/auth/logout/"
        self._request("POST", url, timeout=5)
        self.set_token(None)
        self.user = None
        return {"success": True}

    def get_me(self) -> Dict[str, Any]:
        url = f"{self.base_url}/api/eventos/auth/me/"
        resp = self._request("GET", url)
        if resp is None:
            return {"success": False, "status_code": None, "error": {"detail": self.last_error}}
        if resp.status_code == 200:
            self.user = resp.json()
            return {"success": True, "data": self.user, "status_code": 200}
        return {
            "success": False,
            "status_code": resp.status_code,
            "error": self._parse_error(resp)
        }

    def get_usuarios_disponibles(self, evento_id: Optional[int] = None) -> List[Dict[str, Any]]:
        if evento_id:
            url = f"{self.base_url}/api/eventos/auth/usuarios-disponibles/{evento_id}/"
        else:
            url = f"{self.base_url}/api/eventos/auth/usuarios/"
        resp = self._request("GET", url)
        if resp is not None and resp.status_code == 200:
            try:
                return resp.json()
            except Exception:
                return []
        return []

    # ------------------------------------------------------------------------
    # EVENTOS CRUD
    # ------------------------------------------------------------------------
    def get_eventos(self, status: Optional[str] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/api/eventos/eventos/"
        params = {}
        if status:
            params["status"] = status
        if search:
            params["search"] = search
        resp = self._request("GET", url, params=params)
        if resp is not None and resp.status_code == 200:
            try:
                return resp.json()
            except Exception:
                return []
        return []

    def get_evento(self, evento_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/api/eventos/eventos/{evento_id}/"
        resp = self._request("GET", url)
        if resp is None:
            return {"success": False, "error": {"detail": self.last_error}}
        if resp.status_code == 200:
            try:
                return {"success": True, "data": resp.json()}
            except Exception:
                pass
        return {"success": False, "error": self._parse_error(resp)}

    def create_evento(self, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/api/eventos/eventos/"
        resp = self._request("POST", url, json=data)
        if resp is None:
            return {"success": False, "error": {"detail": self.last_error}}
        if resp.status_code in [200, 201]:
            try:
                return {"success": True, "data": resp.json()}
            except Exception:
                pass
        return {"success": False, "error": self._parse_error(resp)}

    def update_evento(self, evento_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/api/eventos/eventos/{evento_id}/"
        resp = self._request("PATCH", url, json=data)
        if resp is None:
            return {"success": False, "error": {"detail": self.last_error}}
        if resp.status_code == 200:
            try:
                return {"success": True, "data": resp.json()}
            except Exception:
                pass
        return {"success": False, "error": self._parse_error(resp)}

    def delete_evento(self, evento_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/api/eventos/eventos/{evento_id}/"
        resp = self._request("DELETE", url)
        if resp is None:
            return {"success": False, "error": {"detail": self.last_error}}
        if resp.status_code in [200, 204]:
            return {"success": True}
        return {"success": False, "error": self._parse_error(resp)}

    # ------------------------------------------------------------------------
    # CRITERIOS
    # ------------------------------------------------------------------------
    def add_criterio(self, evento_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/api/eventos/eventos/{evento_id}/criterios/"
        resp = self._request("POST", url, json=data)
        if resp is None:
            return {"success": False, "error": {"detail": self.last_error}}
        if resp.status_code in [200, 201]:
            try:
                return {"success": True, "data": resp.json()}
            except Exception:
                pass
        return {"success": False, "error": self._parse_error(resp)}

    def delete_criterio(self, criterio_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/api/eventos/criterios/{criterio_id}/"
        resp = self._request("DELETE", url)
        if resp is None:
            return {"success": False, "error": {"detail": self.last_error}}
        if resp.status_code in [200, 204]:
            return {"success": True}
        return {"success": False, "error": self._parse_error(resp)}

    # ------------------------------------------------------------------------
    # PARTICIPANTES
    # ------------------------------------------------------------------------
    def add_participante(self, evento_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/api/eventos/eventos/{evento_id}/participantes/"
        resp = self._request("POST", url, json=data)
        if resp is None:
            return {"success": False, "error": {"detail": self.last_error}}
        if resp.status_code in [200, 201]:
            try:
                return {"success": True, "data": resp.json()}
            except Exception:
                pass
        return {"success": False, "error": self._parse_error(resp)}

    def delete_participante(self, participante_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/api/eventos/participantes/{participante_id}/"
        resp = self._request("DELETE", url)
        if resp is None:
            return {"success": False, "error": {"detail": self.last_error}}
        if resp.status_code in [200, 204]:
            return {"success": True}
        return {"success": False, "error": self._parse_error(resp)}

    # ------------------------------------------------------------------------
    # JURADOS
    # ------------------------------------------------------------------------
    def get_jurados(self, evento_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/api/eventos/eventos/{evento_id}/jurados/"
        resp = self._request("GET", url)
        if resp is not None and resp.status_code == 200:
            try:
                return resp.json()
            except Exception:
                pass
        return {"jurados": [], "usuarios_disponibles": []}

    def add_jurado(self, evento_id: int, usuario_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/api/eventos/eventos/{evento_id}/jurados/"
        resp = self._request("POST", url, json={"usuario_id": usuario_id})
        if resp is None:
            return {"success": False, "error": {"detail": self.last_error}}
        if resp.status_code in [200, 201]:
            try:
                return {"success": True, "data": resp.json()}
            except Exception:
                pass
        return {"success": False, "error": self._parse_error(resp)}

    def delete_jurado(self, jurado_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/api/eventos/jurados/{jurado_id}/"
        resp = self._request("DELETE", url)
        if resp is None:
            return {"success": False, "error": {"detail": self.last_error}}
        if resp.status_code in [200, 204]:
            return {"success": True}
        return {"success": False, "error": self._parse_error(resp)}

    # ------------------------------------------------------------------------
    # EVALUACIÓN
    # ------------------------------------------------------------------------
    def get_evaluar_lista(self, evento_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/api/eventos/eventos/{evento_id}/evaluar/"
        resp = self._request("GET", url)
        if resp is None:
            return {"success": False, "error": {"detail": self.last_error}}
        if resp.status_code == 200:
            try:
                return {"success": True, "data": resp.json()}
            except Exception:
                pass
        return {"success": False, "error": self._parse_error(resp)}

    def get_evaluar_proyecto(self, evento_id: int, participante_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/api/eventos/eventos/{evento_id}/evaluar/{participante_id}/"
        resp = self._request("GET", url)
        if resp is None:
            return {"success": False, "error": {"detail": self.last_error}}
        if resp.status_code == 200:
            try:
                return {"success": True, "data": resp.json()}
            except Exception:
                pass
        return {"success": False, "error": self._parse_error(resp)}

    def submit_evaluacion(self, evento_id: int, participante_id: int, evaluaciones: List[Dict[str, Any]]) -> Dict[str, Any]:
        url = f"{self.base_url}/api/eventos/eventos/{evento_id}/evaluar/{participante_id}/"
        resp = self._request("POST", url, json={"evaluaciones": evaluaciones})
        if resp is None:
            return {"success": False, "error": {"detail": self.last_error}}
        if resp.status_code == 200:
            try:
                return {"success": True, "data": resp.json()}
            except Exception:
                pass
        return {"success": False, "error": self._parse_error(resp)}

    # ------------------------------------------------------------------------
    # RESULTADOS
    # ------------------------------------------------------------------------
    def get_resultados(self, evento_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/api/eventos/eventos/{evento_id}/resultados/"
        resp = self._request("GET", url)
        if resp is None:
            return {"success": False, "error": {"detail": self.last_error}}
        if resp.status_code == 200:
            try:
                return {"success": True, "data": resp.json()}
            except Exception:
                pass
        return {"success": False, "error": self._parse_error(resp)}
