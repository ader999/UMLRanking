import unittest
from unittest.mock import MagicMock, patch
import flet as ft

try:
    from .api_client import APIClient
    from .theme import status_badge, COLOR_SUCCESS, COLOR_WARNING, COLOR_MUTED
    from .components.event_card import create_event_card, format_iso_date
    from .components.navbar import build_app_bar
    from .views.login_view import build_login_view
    from .views.eventos_view import build_eventos_view
    from .views.evento_detail_view import build_evento_detail_view
    from .views.evento_form_view import (
        build_evento_form_view, _extract_date_str, _extract_time_str, _get_initial_datetime
    )
    from .views.evaluar_view import build_evaluar_lista_view, build_evaluar_proyecto_view
    from .views.resultados_view import build_resultados_view
except (ImportError, ValueError):
    from api_client import APIClient
    from theme import status_badge, COLOR_SUCCESS, COLOR_WARNING, COLOR_MUTED
    from components.event_card import create_event_card, format_iso_date
    from components.navbar import build_app_bar
    from views.login_view import build_login_view
    from views.eventos_view import build_eventos_view
    from views.evento_detail_view import build_evento_detail_view
    from views.evento_form_view import (
        build_evento_form_view, _extract_date_str, _extract_time_str, _get_initial_datetime
    )
    from views.evaluar_view import build_evaluar_lista_view, build_evaluar_proyecto_view
    from views.resultados_view import build_resultados_view

try:
    from .session_manager import (
        save_session, load_session, clear_session,
        is_session_valid, SESSION_DURATION_SECONDS,
        save_last_server, load_last_server
    )
except (ImportError, ValueError):
    from session_manager import (
        save_session, load_session, clear_session,
        is_session_valid, SESSION_DURATION_SECONDS,
        save_last_server, load_last_server
    )


class UMLRankingFletAppTestCase(unittest.TestCase):
    def setUp(self):
        clear_session()
        self.client = APIClient("http://127.0.0.1:8000")
        self.mock_user = {
            "id": 1,
            "username": "carlos_admin",
            "full_name": "Carlos Administrador",
            "email": "carlos@example.com",
            "is_superuser": True
        }
        self.mock_evento = {
            "id": 10,
            "nombre": "Hackathon Flet & Django 2026",
            "descripcion": "Competencia de desarrollo de software",
            "fecha_inicio": "2026-09-25T10:00:00",
            "fecha_fin": "2026-09-26T18:00:00",
            "requiere_jurado": True,
            "esta_activo": True,
            "ha_finalizado": False,
            "total_criterios_score": 100,
            "participantes_count": 2,
            "jurados_count": 1,
            "es_jurado": True,
            "es_administrador": True,
            "creado_por_detalle": self.mock_user,
            "criterios": [
                {"id": 1, "nombre": "Innovación", "descripcion": "Grado de novedad", "puntaje_maximo": 40},
                {"id": 2, "nombre": "Código Limpio", "descripcion": "Arquitectura y tests", "puntaje_maximo": 60},
            ],
            "participantes": [
                {"id": 101, "nombre": "Equipo Nexus", "descripcion": "Sistema IoT", "integrantes": "Ana, Pedro", "estado_evaluacion": "Pendiente"},
                {"id": 102, "nombre": "Equipo Quantum", "descripcion": "App Móvil", "integrantes": "Lucía", "estado_evaluacion": "Completado"},
            ],
            "jurados": [
                {"id": 501, "usuario_detalle": {"id": 2, "username": "jurado1", "full_name": "Dr. Jurado"}},
            ],
        }

    def tearDown(self):
        clear_session()

    # ------------------------------------------------------------------------
    # 1. PRUEBAS DEL CLIENTE API
    # ------------------------------------------------------------------------
    def test_api_client_token_management(self):
        self.client.set_token("token_abc_123")
        self.assertEqual(self.client.session.headers.get("Authorization"), "Token token_abc_123")
        self.client.set_token(None)
        self.assertNotIn("Authorization", self.client.session.headers)

    @patch("requests.Session.post")
    def test_api_client_login_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "token": "test_token_xyz",
            "user": self.mock_user,
            "detail": "Bienvenido"
        }
        mock_post.return_value = mock_response

        res = self.client.login("carlos_admin", "password123")
        self.assertTrue(res["success"])
        self.assertEqual(self.client.token, "test_token_xyz")
        self.assertEqual(self.client.user["username"], "carlos_admin")

    @patch("requests.Session.post")
    def test_api_client_login_strips_whitespace(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "token": "token_stripped",
            "u…

    @patch("requests.Session.get")
    def test_api_client_get_eventos(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [self.mock_evento]
        mock_get.return_value = mock_response

        eventos = self.client.get_eventos(status="activos")
        self.assertEqual(len(eventos), 1)
        self.assertEqual(eventos[0]["nombre"], "Hackathon Flet & Django 2026")

    @patch("requests.Session.post")
    def test_api_client_submit_evaluacion(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"detail": "Guardado exitosamente"}
        mock_post.return_value = mock_response

        evals = [{"criterio_id": 1, "puntaje": 35}, {"criterio_id": 2, "puntaje": 55}]
        res = self.client.submit_evaluacion(10, 101, evals)
        self.assertTrue(res["success"])

    # ------------------------------------------------------------------------
    # 2. PRUEBAS DE COMPONENTES UI (Theme, Cards, Badges, Navbar)
    # ------------------------------------------------------------------------
    def test_status_badge_creation(self):
        badge = status_badge("En Curso", COLOR_SUCCESS, ft.Icons.PLAY_CIRCLE)
        self.assertIsInstance(badge, ft.Container)
        self.assertEqual(badge.bgcolor, COLOR_SUCCESS)

    def test_format_iso_date(self):
        formatted = format_iso_date("2026-09-25T14:30:00Z")
        self.assertEqual(formatted, "25/09/2026 14:30")

    def test_event_card_rendering(self):
        card = create_event_card(
            self.mock_evento,
            on_view_details=lambda x: None,
            on_evaluate=lambda x: None,
            on_view_results=lambda x: None,
        )
        self.assertIsInstance(card, ft.Container)
        self.assertIsNone(card.width)

        card_custom = create_event_card(
            self.mock_evento,
            on_view_details=lambda x: None,
            width=360,
        )
        self.assertEqual(card_custom.width, 360)

    def test_navbar_rendering_authenticated(self):
        navbar = build_app_bar(
            user=self.mock_user,
            on_navigate=lambda x: None,
            on_logout=lambda: None,
        )
        self.assertIsInstance(navbar, ft.AppBar)
        # Debe contener botones de navegación y avatar de usuario
        self.assertTrue(len(navbar.actions) >= 3)

    # ------------------------------------------------------------------------
    # 3. PRUEBAS DE VISTAS (Views)
    # ------------------------------------------------------------------------
    def test_login_view_construction(self):
        on_success_called = []
        view = build_login_view(
            self.client,
            on_login_success=lambda u: on_success_called.append(u),
        )
        self.assertIsInstance(view, ft.Container)

    @patch.object(APIClient, "get_eventos")
    def test_eventos_view_construction_and_load(self, mock_get_eventos):
        mock_get_eventos.return_value = [self.mock_evento]
        view = build_eventos_view(
            self.client,
            on_navigate=lambda x: None,
            on_view_event=lambda x: None,
            on_evaluate_event=lambda x: None,
            on_results_event=lambda x: None,
        )
        self.assertIsInstance(view, ft.Container)
        self.assertTrue(hasattr(view, "load_data"))
        # Simular carga
        view.load_data()
        mock_get_eventos.assert_called_once()

    @patch.object(APIClient, "get_evento")
    def test_evento_detail_view_construction(self, mock_get_evento):
        mock_get_evento.return_value = {"success": True, "data": self.mock_evento}
        mock_page = MagicMock()
        mock_page.overlay = []

        view = build_evento_detail_view(
            self.client,
            evento_id=10,
            page=mock_page,
            on_back=lambda: None,
            on_edit_evento=lambda x: None,
            on_evaluate_evento=lambda x: None,
            on_results_evento=lambda x: None,
        )
        self.assertIsInstance(view, ft.Container)
        self.assertTrue(hasattr(view, "load_data"))
        view.load_data()
        mock_get_evento.assert_called_once_with(10)

    @patch.object(APIClient, "get_evento")
    def test_evento_form_view_construction(self, mock_get_evento):
        mock_get_evento.return_value = {"success": True, "data": self.mock_evento}
        # Modo Edición
        view_edit = build_evento_form_view(
            self.client,
            evento_id=10,
            on_success=lambda x: None,
            on_cancel=lambda: None,
        )
        self.assertIsInstance(view_edit, ft.Container)
        self.assertTrue(hasattr(view_edit, "load_data"))
        view_edit.load_data()

        # Modo Creación
        view_create = build_evento_form_view(
            self.client,
            evento_id=None,
            on_success=lambda x: None,
            on_cancel=lambda: None,
        )
        self.assertIsInstance(view_create, ft.Container)

    def test_datetime_picker_helpers(self):
        from datetime import datetime as dt, date as d, time as tm
        # Test _extract_date_str
        self.assertEqual(_extract_date_str(dt(2026, 9, 25, 14, 26)), "2026-09-25")
        self.assertEqual(_extract_date_str(d(2026, 9, 25)), "2026-09-25")
        self.assertEqual(_extract_date_str("2026-09-25T14:26:00.000"), "2026-09-25")
        self.assertEqual(_extract_date_str(None, "2026-09-25"), "2026-09-25")

        # Test _extract_time_str
        self.assertEqual(_extract_time_str(tm(14, 26)), "14:26")
        self.assertEqual(_extract_time_str("14:26:00"), "14:26")
        self.assertEqual(_extract_time_str("9:5"), "09:05")
        self.assertEqual(_extract_time_str(None, "18:45:00"), "18:45")

        # Test _get_initial_datetime
        parsed_d, parsed_t = _get_initial_datetime("2026-09-25T14:26")
        self.assertEqual(parsed_d.year, 2026)
        self.assertEqual(parsed_d.month, 9)
        self.assertEqual(parsed_d.day, 25)
        self.assertEqual(parsed_t.hour, 14)
        self.assertEqual(parsed_t.minute, 26)

    @patch.object(APIClient, "get_evaluar_lista")
    def test_evaluar_lista_view_construction(self, mock_evaluar_lista):
        mock_evaluar_lista.return_value = {
            "success": True,
            "data": {
                "evento_id": 10,
                "evento_nombre": "Hackathon 2026",
                "participantes": [
                    {"id": 101, "nombre": "Equipo Nexus", "descripcion": "IoT", "integrantes": "Ana", "estado_evaluacion": "Pendiente"}
                ]
            }
        }
        view = build_evaluar_lista_view(
            self.client,
            evento_id=10,
            on_back=lambda: None,
            on_select_project=lambda x: None,
        )
        self.assertIsInstance(view, ft.Container)
        self.assertTrue(hasattr(view, "load_data"))
        view.load_data()
        mock_evaluar_lista.assert_called_once_with(10)

    @patch.object(APIClient, "get_evaluar_proyecto")
    def test_evaluar_proyecto_view_construction(self, mock_evaluar_proj):
        mock_evaluar_proj.return_value = {
            "success": True,
            "data": {
                "evento_id": 10,
                "evento_nombre": "Hackathon 2026",
                "participante": {"id": 101, "nombre": "Equipo Nexus", "descripcion": "IoT", "integrantes": "Ana"},
                "criterios": [
                    {"id": 1, "nombre": "Innovación", "descripcion": "Novedad", "puntaje_maximo": 40, "puntaje_actual": 30},
                    {"id": 2, "nombre": "Código Limpio", "descripcion": "Calidad", "puntaje_maximo": 60, "puntaje_actual": 50},
                ],
                "total_criterios_score": 100,
                "total_asignado": 80,
            }
        }
        mock_page = MagicMock()
        mock_page.overlay = []

        view = build_evaluar_proyecto_view(
            self.client,
            evento_id=10,
            participante_id=101,
            page=mock_page,
            on_back=lambda: None,
        )
        self.assertIsInstance(view, ft.Container)
        self.assertTrue(hasattr(view, "load_data"))
        view.load_data()
        mock_evaluar_proj.assert_called_once_with(10, 101)

    @patch.object(APIClient, "get_resultados")
    def test_resultados_view_construction(self, mock_get_resultados):
        mock_get_resultados.return_value = {
            "success": True,
            "data": {
                "evento": self.mock_evento,
                "criterios": self.mock_evento["criterios"],
                "podio": {
                    "primero": {"participante": {"nombre": "Equipo Quantum"}, "puntaje_promedio": 95.0, "evaluadores_count": 2},
                    "segundo": {"participante": {"nombre": "Equipo Nexus"}, "puntaje_promedio": 85.0, "evaluadores_count": 2},
                    "tercero": None,
                },
                "resultados": [
                    {"puesto": 1, "participante": {"nombre": "Equipo Quantum"}, "puntaje_promedio": 95.0, "evaluadores_count": 2, "desglose_criterios": {"1": 38.0, "2": 57.0}},
                    {"puesto": 2, "participante": {"nombre": "Equipo Nexus"}, "puntaje_promedio": 85.0, "evaluadores_count": 2, "desglose_criterios": {"1": 35.0, "2": 50.0}},
                ],
                "es_previsualizacion": False,
            }
        }
        view = build_resultados_view(
            self.client,
            evento_id=10,
            on_back=lambda: None,
        )
        self.assertIsInstance(view, ft.Container)
        self.assertTrue(hasattr(view, "load_data"))
        view.load_data()
        mock_get_resultados.assert_called_once_with(10)

    # ------------------------------------------------------------------------
    # 5. PRUEBAS DE PERSISTENCIA DE SESIÓN (1 MES / 30 DÍAS)
    # ------------------------------------------------------------------------
    def test_session_manager_save_and_load_30_days(self):
        saved = save_session("token_30d_abc", self.mock_user, "https://planeauml.codeader.com")
        self.assertTrue(saved)
        self.assertTrue(is_session_valid())

        session = load_session()
        self.assertIsNotNone(session)
        self.assertEqual(session["token"], "token_30d_abc")
        self.assertEqual(session["user"]["username"], "carlos_admin")
        self.assertEqual(session["base_url"], "https://planeauml.codeader.com")

        # Verificar duración exacta: 30 días (1 mes = 2,592,000 segundos)
        duration = session["expires_at"] - session["created_at"]
        self.assertEqual(duration, SESSION_DURATION_SECONDS)
        self.assertEqual(duration, 30 * 24 * 60 * 60)

    def test_session_manager_expires_after_one_month(self):
        # Simular una sesión creada hace más de 1 mes (ya expirada)
        save_session("token_old", self.mock_user, duration_seconds=-10)
        self.assertFalse(is_session_valid())
        self.assertIsNone(load_session())

    def test_session_manager_clear(self):
        save_session("token_to_clear", self.mock_user)
        self.assertTrue(is_session_valid())
        cleared = clear_session()
        self.assertTrue(cleared)
        self.assertFalse(is_session_valid())
        self.assertIsNone(load_session())

    @patch("requests.Session.post")
    def test_api_client_persists_session_on_login_and_restores(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "token": "stored_token_999",
            "user": self.mock_user,
            "detail": "Bienvenido"
        }
        mock_post.return_value = mock_response

        # 1. Login inicial
        res = self.client.login("carlos_admin", "password123")
        self.assertTrue(res["success"])

        # 2. Nueva instancia simulando reinicio de la aplicación
        fresh_client = APIClient()
        self.assertIsNone(fresh_client.token)
        self.assertIsNone(fresh_client.user)

        # 3. Restaurar sesión almacenada
        has_session = fresh_client.load_stored_session()
        self.assertTrue(has_session)
        self.assertEqual(fresh_client.token, "stored_token_999")
        self.assertEqual(fresh_client.user["username"], "carlos_admin")
        self.assertEqual(fresh_client.session.headers.get("Authorization"), "Token stored_token_999")

    def test_api_client_logout_clears_stored_session(self):
        save_session("token_logout", self.mock_user)
        self.assertTrue(is_session_valid())

        self.client.logout()
        self.assertFalse(is_session_valid())
        self.assertIsNone(load_session())
        self.assertIsNone(self.client.token)
        self.assertIsNone(self.client.user)


if __name__ == "__main__":
    unittest.main()
