import flet as ft

try:
    from .api_client import APIClient
    from .theme import COLOR_BG
    from .components.navbar import build_app_bar
    from .views.login_view import build_login_view
    from .views.eventos_view import build_eventos_view
    from .views.evento_detail_view import build_evento_detail_view
    from .views.evento_form_view import build_evento_form_view
    from .views.evaluar_view import build_evaluar_lista_view, build_evaluar_proyecto_view
    from .views.resultados_view import build_resultados_view
except ImportError:
    from api_client import APIClient
    from theme import COLOR_BG
    from components.navbar import build_app_bar
    from views.login_view import build_login_view
    from views.eventos_view import build_eventos_view
    from views.evento_detail_view import build_evento_detail_view
    from views.evento_form_view import build_evento_form_view
    from views.evaluar_view import build_evaluar_lista_view, build_evaluar_proyecto_view
    from views.resultados_view import build_resultados_view


def main(page: ft.Page):
    page.title = "UMLRanking - Sistema de Evaluación de Eventos"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = COLOR_BG
    page.padding = 0

    api_client = APIClient()

    state = {
        "current_view": "login",
        "current_evento_id": None,
        "current_participante_id": None,
    }

    body_container = ft.Container(expand=True)

    def navigate_to(view_name: str, **kwargs):
        state["current_view"] = view_name
        if "evento_id" in kwargs:
            state["current_evento_id"] = kwargs["evento_id"]
        if "participante_id" in kwargs:
            state["current_participante_id"] = kwargs["participante_id"]

        update_appbar()

        active_control = None

        if view_name == "login":
            active_control = build_login_view(
                api_client,
                on_login_success=lambda user: navigate_to("eventos"),
            )
        elif view_name == "eventos":
            active_control = build_eventos_view(
                api_client,
                on_navigate=navigate_to,
                on_view_event=lambda ev_id: navigate_to("detalle", evento_id=ev_id),
                on_evaluate_event=lambda ev_id: navigate_to("evaluar_lista", evento_id=ev_id),
                on_results_event=lambda ev_id: navigate_to("resultados", evento_id=ev_id),
            )
        elif view_name == "crear_evento":
            active_control = build_evento_form_view(
                api_client,
                evento_id=None,
                on_success=lambda ev_id: navigate_to("detalle", evento_id=ev_id),
                on_cancel=lambda: navigate_to("eventos"),
            )
        elif view_name == "editar_evento":
            active_control = build_evento_form_view(
                api_client,
                evento_id=state["current_evento_id"],
                on_success=lambda ev_id: navigate_to("detalle", evento_id=ev_id),
                on_cancel=lambda: navigate_to("detalle", evento_id=state["current_evento_id"]),
            )
        elif view_name == "detalle":
            active_control = build_evento_detail_view(
                api_client,
                evento_id=state["current_evento_id"],
                page=page,
                on_back=lambda: navigate_to("eventos"),
                on_edit_evento=lambda ev_id: navigate_to("editar_evento", evento_id=ev_id),
                on_evaluate_evento=lambda ev_id: navigate_to("evaluar_lista", evento_id=ev_id),
                on_results_evento=lambda ev_id: navigate_to("resultados", evento_id=ev_id),
            )
        elif view_name == "evaluar_lista":
            active_control = build_evaluar_lista_view(
                api_client,
                evento_id=state["current_evento_id"],
                on_back=lambda: navigate_to("detalle", evento_id=state["current_evento_id"]),
                on_select_project=lambda pid: navigate_to(
                    "evaluar_proyecto",
                    evento_id=state["current_evento_id"],
                    participante_id=pid
                ),
            )
        elif view_name == "evaluar_proyecto":
            active_control = build_evaluar_proyecto_view(
                api_client,
                evento_id=state["current_evento_id"],
                participante_id=state["current_participante_id"],
                page=page,
                on_back=lambda: navigate_to("evaluar_lista", evento_id=state["current_evento_id"]),
            )
        elif view_name == "resultados":
            active_control = build_resultados_view(
                api_client,
                evento_id=state["current_evento_id"],
                on_back=lambda: navigate_to("detalle", evento_id=state["current_evento_id"]),
            )

        body_container.content = active_control
        page.update()

        # Si el control tiene método para cargar datos asíncrono / post-montaje
        if hasattr(active_control, "load_data"):
            active_control.load_data()

    def update_appbar():
        if api_client.user:
            page.appbar = build_app_bar(
                user=api_client.user,
                on_navigate=navigate_to,
                on_logout=handle_logout,
            )
        else:
            page.appbar = None

    def handle_logout():
        api_client.logout()
        navigate_to("login")

    # Iniciar en Login
    page.add(body_container)
    navigate_to("login")


if __name__ == "__main__":
    if hasattr(ft, "run"):
        ft.run(main)
    else:
        ft.app(target=main)
