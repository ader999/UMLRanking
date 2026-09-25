import requests
from typing import Optional, Dict, Any, List


class APIClient:
    """
    Cliente HTTP para interactuar con los endpoints DRF del backend de eventos.
    Maneja autenticación por Token, URLs base y manejo de errores.
    """
    def __init__(self, base_url: str = "https://planeauml.codeader.com"):
        self.base_url = base_url.rstrip("/")

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

    def login(self, username: str, password: str) -> Dict[str, Any]:
        url = f"{self.base_url}/api/eventos/auth/login/"
        try:
            resp = self.session.post(url, json={"username": username, "password": password}, timeout=10)
        except Exception as e:
            return {"success": False, "error": {"detail": f"No se pudo conectar al servidor: {e}"}}

        if resp.status_code == 200:
            data = resp.json()
            self.set_token(data.get("token"))
            self.user = data.get("user")
            return {"success": True, "data": data}
        return {"success": False, "error": self._parse_error(resp)}

    def logout(self) -> Dict[str, Any]:
        url = f"{self.base_url}/api/eventos/auth/logout/"
        try:
            self.session.post(url, timeout=5)
        except Exception:
            pass
        self.set_token(None)
        self.user = None
        return {"success": True}

    def get_me(self) -> Dict[str, Any]:
        url = f"{self.base_url}/api/eventos/auth/me/"
        resp = self.session.get(url, timeout=10)
        if resp.status_code == 200:
            self.user = resp.json()
            return {"success": True, "data": self.user}
        return {"success": False, "error": resp.json() if resp.content else {}}

    def get_usuarios_disponibles(self, evento_id: Optional[int] = None) -> List[Dict[str, Any]]:
        if evento_id:
            url = f"{self.base_url}/api/eventos/auth/usuarios-disponibles/{evento_id}/"
        else:
            url = f"{self.base_url}/api/eventos/auth/usuarios/"
        resp = self.session.get(url, timeout=10)
        if resp.status_code == 200:
            return resp.json()
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
        resp = self.session.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        return []

    def get_evento(self, evento_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/api/eventos/eventos/{evento_id}/"
        resp = self.session.get(url, timeout=10)
        if resp.status_code == 200:
            return {"success": True, "data": resp.json()}
        return {"success": False, "error": resp.json() if resp.content else {}}

    def create_evento(self, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/api/eventos/eventos/"
        resp = self.session.post(url, json=data, timeout=10)
        if resp.status_code in [200, 201]:
            return {"success": True, "data": resp.json()}
        try:
            return {"success": False, "error": resp.json()}
        except Exception:
            return {"success": False, "error": {"detail": resp.text}}

    def update_evento(self, evento_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/api/eventos/eventos/{evento_id}/"
        resp = self.session.patch(url, json=data, timeout=10)
        if resp.status_code == 200:
            return {"success": True, "data": resp.json()}
        try:
            return {"success": False, "error": resp.json()}
        except Exception:
            return {"success": False, "error": {"detail": resp.text}}

    def delete_evento(self, evento_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/api/eventos/eventos/{evento_id}/"
        resp = self.session.delete(url, timeout=10)
        if resp.status_code in [200, 204]:
            return {"success": True}
        try:
            return {"success": False, "error": resp.json()}
        except Exception:
            return {"success": False, "error": {"detail": resp.text}}

    # ------------------------------------------------------------------------
    # CRITERIOS
    # ------------------------------------------------------------------------
    def add_criterio(self, evento_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/api/eventos/eventos/{evento_id}/criterios/"
        resp = self.session.post(url, json=data, timeout=10)
        if resp.status_code in [200, 201]:
            return {"success": True, "data": resp.json()}
        return {"success": False, "error": resp.json() if resp.content else {}}

    def delete_criterio(self, criterio_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/api/eventos/criterios/{criterio_id}/"
        resp = self.session.delete(url, timeout=10)
        if resp.status_code in [200, 204]:
            return {"success": True}
        return {"success": False, "error": resp.json() if resp.content else {}}

    # ------------------------------------------------------------------------
    # PARTICIPANTES
    # ------------------------------------------------------------------------
    def add_participante(self, evento_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/api/eventos/eventos/{evento_id}/participantes/"
        resp = self.session.post(url, json=data, timeout=10)
        if resp.status_code in [200, 201]:
            return {"success": True, "data": resp.json()}
        return {"success": False, "error": resp.json() if resp.content else {}}

    def delete_participante(self, participante_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/api/eventos/participantes/{participante_id}/"
        resp = self.session.delete(url, timeout=10)
        if resp.status_code in [200, 204]:
            return {"success": True}
        return {"success": False, "error": resp.json() if resp.content else {}}

    # ------------------------------------------------------------------------
    # JURADOS
    # ------------------------------------------------------------------------
    def get_jurados(self, evento_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/api/eventos/eventos/{evento_id}/jurados/"
        resp = self.session.get(url, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        return {"jurados": [], "usuarios_disponibles": []}

    def add_jurado(self, evento_id: int, usuario_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/api/eventos/eventos/{evento_id}/jurados/"
        resp = self.session.post(url, json={"usuario_id": usuario_id}, timeout=10)
        if resp.status_code in [200, 201]:
            return {"success": True, "data": resp.json()}
        return {"success": False, "error": resp.json() if resp.content else {}}

    def delete_jurado(self, jurado_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/api/eventos/jurados/{jurado_id}/"
        resp = self.session.delete(url, timeout=10)
        if resp.status_code in [200, 204]:
            return {"success": True}
        return {"success": False, "error": resp.json() if resp.content else {}}

    # ------------------------------------------------------------------------
    # EVALUACIÓN
    # ------------------------------------------------------------------------
    def get_evaluar_lista(self, evento_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/api/eventos/eventos/{evento_id}/evaluar/"
        resp = self.session.get(url, timeout=10)
        if resp.status_code == 200:
            return {"success": True, "data": resp.json()}
        return {"success": False, "error": resp.json() if resp.content else {}}

    def get_evaluar_proyecto(self, evento_id: int, participante_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/api/eventos/eventos/{evento_id}/evaluar/{participante_id}/"
        resp = self.session.get(url, timeout=10)
        if resp.status_code == 200:
            return {"success": True, "data": resp.json()}
        return {"success": False, "error": resp.json() if resp.content else {}}

    def submit_evaluacion(self, evento_id: int, participante_id: int, evaluaciones: List[Dict[str, Any]]) -> Dict[str, Any]:
        url = f"{self.base_url}/api/eventos/eventos/{evento_id}/evaluar/{participante_id}/"
        resp = self.session.post(url, json={"evaluaciones": evaluaciones}, timeout=10)
        if resp.status_code == 200:
            return {"success": True, "data": resp.json()}
        return {"success": False, "error": resp.json() if resp.content else {}}

    # ------------------------------------------------------------------------
    # RESULTADOS
    # ------------------------------------------------------------------------
    def get_resultados(self, evento_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/api/eventos/eventos/{evento_id}/resultados/"
        resp = self.session.get(url, timeout=10)
        if resp.status_code == 200:
            return {"success": True, "data": resp.json()}
        return {"success": False, "error": resp.json() if resp.content else {}}
