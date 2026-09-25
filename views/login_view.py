import flet as ft
try:
    from ..theme import (
        COLOR_PRIMARY, COLOR_PRIMARY_DARK, COLOR_PRIMARY_LIGHT,
        COLOR_CARD, COLOR_BORDER, COLOR_TEXT_MAIN, COLOR_TEXT_MUTED, COLOR_DANGER, safe_update
    )
except (ImportError, ValueError):
    from theme import (
        COLOR_PRIMARY, COLOR_PRIMARY_DARK, COLOR_PRIMARY_LIGHT,
        COLOR_CARD, COLOR_BORDER, COLOR_TEXT_MAIN, COLOR_TEXT_MUTED, COLOR_DANGER, safe_update
    )


def build_login_view(api_client, on_login_success):
    """
    Construye la vista de autenticación y configuración de conexión.
    """
    server_input = ft.TextField(
        label="Servidor Backend (URL)",
        value=api_client.base_url,
        prefix_icon=ft.Icons.DASHBOARD,
        hint_text="https://planeauml.codeader.com",
    )

    username_input = ft.TextField(
        label="Nombre de Usuario",
        prefix_icon=ft.Icons.PERSON,
        autofocus=True,
    )
    password_input = ft.TextField(
        label="Contraseña",
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.Icons.LOCK,
    )
    error_container = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.ERROR_OUTLINE, color=COLOR_DANGER, size=18),
                ft.Text("", color=COLOR_DANGER, size=13, expand=True),
            ],
            spacing=8,
        ),
        bgcolor="#FEE2E2",
        border_radius=8,
        padding=10,
        visible=False,
    )
    login_btn = ft.FilledButton(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.LOGIN, color=ft.Colors.WHITE, size=18),
                ft.Text("Iniciar Sesión", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.WHITE),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            tight=True,
        ),
        style=ft.ButtonStyle(bgcolor=COLOR_PRIMARY),
        height=48,
    )

    def handle_submit(e):
        base_url = server_input.value.strip() if server_input.value else "http://127.0.0.1:8000"
        api_client.set_base_url(base_url)

        u = username_input.value.strip() if username_input.value else ""
        p = password_input.value or ""

        if not u or not p:
            error_container.content.controls[1].value = "Por favor ingresa usuario y contraseña."
            error_container.visible = True
            safe_update(error_container)
            return

        login_btn.disabled = True
        safe_update(login_btn)

        result = api_client.login(u, p)
        login_btn.disabled = False
        safe_update(login_btn)

        if result.get("success"):
            error_container.visible = False
            on_login_success(result["data"]["user"])
        else:
            err = result.get("error", {})
            msg = err.get("detail") or "Credenciales incorrectas o servidor no disponible."
            error_container.content.controls[1].value = str(msg)
            error_container.visible = True
            safe_update(error_container)

    login_btn.on_click = handle_submit
    password_input.on_submit = handle_submit

    card = ft.Container(
        content=ft.Column(
            controls=[
                # Cabecera con Icono
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Container(
                                content=ft.Icon(ft.Icons.EMOJI_EVENTS, size=48, color=COLOR_PRIMARY),
                                bgcolor=COLOR_PRIMARY_LIGHT,
                                border_radius=40,
                                padding=16,
                            ),
                            ft.Text("UMLRanking", size=26, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MAIN),
                            ft.Text(
                                "Plataforma de Evaluación y Clasificación de Eventos",
                                size=13,
                                color=COLOR_TEXT_MUTED,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=6,
                    ),
                    alignment=ft.Alignment(0, 0),
                    margin=ft.Padding.only(bottom=16),
                ),
                error_container,
                server_input,
                username_input,
                password_input,
                ft.Container(
                    content=login_btn,
                    margin=ft.Padding.only(top=10),
                ),
                ft.Text(
                    "Ingresa con tus credenciales asignadas en el sistema.",
                    size=11,
                    color=COLOR_TEXT_MUTED,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            spacing=14,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=COLOR_CARD,
        border=ft.Border.all(1, COLOR_BORDER),
        border_radius=16,
        padding=24,
        shadow=ft.BoxShadow(
            spread_radius=2,
            blur_radius=16,
            color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
            offset=ft.Offset(0, 4),
        ),
    )

    return ft.Container(
        content=ft.Column(
            controls=[card],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
        ),
        alignment=ft.Alignment(0, 0),
        padding=16,
        expand=True,
    )
