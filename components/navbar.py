import flet as ft
from ..theme import COLOR_PRIMARY, COLOR_PRIMARY_DARK, COLOR_TEXT_MUTED


def build_app_bar(user, on_navigate, on_logout):
    """
    Construye la barra superior elegante para la aplicación UMLRanking.
    """
    user_display = "Invitado"
    if user:
        user_display = user.get("full_name") or user.get("username", "Usuario")

    title_content = ft.Row(
        controls=[
            ft.Container(
                content=ft.Icon(ft.Icons.EMOJI_EVENTS, color=ft.Colors.WHITE, size=24),
                bgcolor=COLOR_PRIMARY_DARK,
                border_radius=8,
                padding=6,
            ),
            ft.Column(
                controls=[
                    ft.Text("UMLRanking", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Text("Gestión y Evaluación de Eventos", size=11, color=ft.Colors.WHITE_70),
                ],
                spacing=0,
            ),
        ],
        spacing=10,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    actions = []
    if user:
        actions.extend([
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.EVENT, color=ft.Colors.WHITE, size=18),
                        ft.Text("Eventos", color=ft.Colors.WHITE, weight=ft.FontWeight.W_500, size=13),
                    ],
                    spacing=4,
                ),
                padding=ft.Padding.symmetric(horizontal=12, vertical=6),
                border_radius=6,
                ink=True,
                on_click=lambda _: on_navigate("eventos"),
            ),
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.ADD_CIRCLE_OUTLINE, color=ft.Colors.WHITE, size=18),
                        ft.Text("Crear Evento", color=ft.Colors.WHITE, weight=ft.FontWeight.W_500, size=13),
                    ],
                    spacing=4,
                ),
                padding=ft.Padding.symmetric(horizontal=12, vertical=6),
                border_radius=6,
                ink=True,
                on_click=lambda _: on_navigate("crear_evento"),
            ),
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.CircleAvatar(
                            content=ft.Icon(ft.Icons.PERSON, size=16, color=COLOR_PRIMARY),
                            bgcolor=ft.Colors.WHITE,
                            radius=14,
                        ),
                        ft.Text(user_display, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=13),
                    ],
                    spacing=6,
                ),
                padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                bgcolor=ft.Colors.WHITE_12,
                border_radius=20,
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
        leading_width=300,
        title=title_content,
        bgcolor=COLOR_PRIMARY,
        center_title=False,
        actions=actions,
    )
