import json
import os
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any

# Duración de la sesión: 1 mes (30 días en segundos)
SESSION_DURATION_SECONDS = 30 * 24 * 60 * 60  # 2,592,000 segundos


def get_storage_dir() -> Path:
    """
    Obtiene el directorio de almacenamiento persistente adecuado según la plataforma.
    En Android con Flet/Flutter, utiliza FLET_APP_STORAGE_DATA (almacenamiento privado persistente).
    En Desktop (Linux, macOS, Windows), utiliza ~/.umlranking.
    """
    flet_data = os.environ.get("FLET_APP_STORAGE_DATA")
    if flet_data:
        p = Path(flet_data)
        try:
            p.mkdir(parents=True, exist_ok=True)
            return p
        except Exception:
            pass

    try:
        home_p = Path.home() / ".umlranking"
        home_p.mkdir(parents=True, exist_ok=True)
        test_file = home_p / ".write_test"
        test_file.touch()
        test_file.unlink(missing_ok=True)
        return home_p
    except Exception:
        pass

    try:
        cwd_p = Path.cwd() / ".umlranking"
        cwd_p.mkdir(parents=True, exist_ok=True)
        return cwd_p
    except Exception:
        pass

    temp_p = Path(tempfile.gettempdir()) / "umlranking"
    temp_p.mkdir(parents=True, exist_ok=True)
    return temp_p


def get_session_file() -> Path:
    return get_storage_dir() / "session.json"


def get_config_file() -> Path:
    return get_storage_dir() / "config.json"


def save_session(
    token: str,
    user: Dict[str, Any],
    base_url: Optional[str] = None,
    duration_seconds: int = SESSION_DURATION_SECONDS,
) -> bool:
    """
    Guarda la sesión del usuario con una validez de 1 mes (30 días).
    """
    now = time.time()
    expires_at = now + duration_seconds

    data = {
        "token": token,
        "user": user,
        "base_url": base_url,
        "created_at": now,
        "created_at_iso": datetime.fromtimestamp(now, tz=timezone.utc).isoformat(),
        "expires_at": expires_at,
        "expires_at_iso": datetime.fromtimestamp(expires_at, tz=timezone.utc).isoformat(),
        "duration_days": duration_seconds / 86400,
    }

    try:
        session_file = get_session_file()
        session_dir = session_file.parent
        session_dir.mkdir(parents=True, exist_ok=True)

        temp_file = session_dir / f"session_{int(now)}.tmp"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        temp_file.replace(session_file)

        if base_url:
            save_last_server(base_url)
        return True
    except Exception as e:
        print(f"[session_manager] Error guardando sesión: {e}")
        return False


def load_session() -> Optional[Dict[str, Any]]:
    """
    Carga la sesión guardada si existe y no ha expirado.
    Si ha expirado (más de 1 mes), la elimina y retorna None.
    """
    session_file = get_session_file()
    if not session_file.exists():
        return None

    try:
        with open(session_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        now = time.time()
        expires_at = data.get("expires_at", 0)

        if now >= expires_at:
            print(f"[session_manager] Sesión expirada ({data.get('expires_at_iso')}). Limpiando...")
            clear_session()
            return None

        if not data.get("token") or not data.get("user"):
            clear_session()
            return None

        return data
    except Exception as e:
        print(f"[session_manager] Error leyendo sesión: {e}")
        clear_session()
        return None


def clear_session() -> bool:
    """
    Elimina los datos de sesión activa.
    """
    try:
        session_file = get_session_file()
        if session_file.exists():
            session_file.unlink(missing_ok=True)
        return True
    except Exception as e:
        print(f"[session_manager] Error limpiando sesión: {e}")
        return False


def is_session_valid() -> bool:
    """
    Verifica de manera rápida si existe una sesión activa y vigente.
    """
    return load_session() is not None


def save_last_server(base_url: str) -> bool:
    """
    Guarda la última URL de servidor utilizada para conveniencia del usuario.
    """
    try:
        config_file = get_config_file()
        config = {}
        if config_file.exists():
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
            except Exception:
                config = {}

        config["last_server"] = base_url.rstrip("/")
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        return True
    except Exception:
        return False


def load_last_server() -> Optional[str]:
    """
    Carga la última URL de servidor utilizada.
    """
    try:
        config_file = get_config_file()
        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
                return config.get("last_server")
    except Exception:
        pass
    return None
