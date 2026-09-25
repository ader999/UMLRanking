import flet as ft
try:
    from ..theme import COLOR_PRIMARY, COLOR_PRIMARY_DARK, COLOR_TEXT_MUTED
except (ImportError, ValueError):
    from theme import COLOR_PRIMARY, COLOR_PRIMARY_DARK, COLOR_TEXT_MUTED


def build_app_bar(user, on_navigate, on_logout):
    """
    Construye la barra superior elegante para la aplicación UMLRanking.
    """
    user_display = "Invitado"
    if user:
        user_display = user.get("full_name") or user.get("username", "Usuario")

    title_content = ft.Row(
        controls=[
            ft.Icon(ft.Icons.EMOJI_EVENTS, color=ft.Colors.WHITE, size=22),
            ft.Text("UMLRanking", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
        ],
        spacing=8,
        tight=True,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    actions = []
    if user:
        actions.extend([
            ft.IconButton(
                icon=ft.Icons.EVENT,
                icon_color=ft.Colors.WHITE,
                tooltip="Eventos",
                on_click=lambda _: on_navigate("eventos"),
            ),
            ft.IconButton(
                icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                icon_color=ft.Colors.WHITE,
                tooltip="Crear Evento",
                on_click=lambda _: on_navigate("crear_evento"),
            ),
            ft.PopupMenuButton(
                content=ft.CircleAvatar(
                    content=ft.Icon(ft.Icons.PERSON, size=16, color=COLOR_PRIMARY),
                    bgcolor=ft.Colors.WHITE,
                    radius=14,
                ),
                tooltip=user_display,
                items=[
                    ft.PopupMenuItem(
                        content=ft.Row([
                            ft.Icon(ft.Icons.PERSON, size=18, color=COLOR_PRIMARY),
                            ft.Text(user_display, weight=ft.FontWeight.BOLD, size=13),
                        ], spacing=8),
                        disabled=True,
                    ),
                    ft.PopupMenuItem(),
                    ft.PopupMenuItem(
                        content=ft.Row([
                            ft.Icon(ft.Icons.EVENT, size=18),
                            ft.Text("Eventos", size=13),
                        ], spacing=8),
                        on_click=lambda _: on_navigate("eventos"),
                    ),
                    ft.PopupMenuItem(
                        content=ft.Row([
                            ft.Icon(ft.Icons.ADD_CIRCLE_OUTLINE, size=18),
                            ft.Text("Crear Evento", size=13),
                        ], spacing=8),
                        on_click=lambda _: on_navigate("crear_evento"),
                    ),
                    ft.PopupMenuItem(),
                    ft.PopupMenuItem(
                        content=ft.Row([
                            ft.Icon(ft.Icons.LOGOUT, size=18, color=COLOR_PRIMARY),
                            ft.Text("Cerrar Sesión", size=13, color=COLOR_PRIMARY),
                        ], spacing=8),
                        on_click=lambda _: on_logout(),
                    ),
                ],
            ),
            ft.IconButton(
                icon=ft.Icons.LOGOUT,
                icon_color=ft.Colors.WHITE,
                tooltip="Cerrar Sesión",
                on_click=lambda _: on_logout(),
            ),
        ])
    else:
        actions.append(
            ft.FilledButton(
                content=ft.Text("Iniciar Sesión"),
                icon=ft.Icons.LOGIN,
                on_click=lambda _: on_navigate("login"),
            )
        )

    return ft.AppBar(
        title=title_content,
        bgcolor=COLOR_PRIMARY,
        center_title=False,
        actions=actions,
    )
