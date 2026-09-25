import flet as ft
try:
    from ..theme import COLOR_PRIMARY, COLOR_DANGER
except (ImportError, ValueError):
    from theme import COLOR_PRIMARY, COLOR_DANGER


def show_add_criterio_dialog(page: ft.Page, on_submit):
    """Muestra modal para registrar un nuevo criterio de evaluación."""
    nombre_field = ft.TextField(label="Nombre del Criterio", hint_text="Ej. Innovación", autofocus=True)
    desc_field = ft.TextField(label="Descripción (Opcional)", multiline=True, min_lines=2, max_lines=3)
    puntos_field = ft.TextField(label="Puntaje Máximo", hint_text="Ej. 30", keyboard_type=ft.KeyboardType.NUMBER)
    error_text = ft.Text("", color=COLOR_DANGER, size=12, visible=False)

    def close_dialog(e=None):
        dlg.open = False
        page.update()

    def handle_save(e):
        nombre = nombre_field.value.strip() if nombre_field.value else ""
        if not nombre:
            error_text.value = "El nombre del criterio es obligatorio."
            error_text.visible = True
            page.update()
            return

        try:
            pts = int(puntos_field.value)
            if pts <= 0:
                raise ValueError()
        except Exception:
            error_text.value = "El puntaje máximo debe ser un número entero mayor a 0."
            error_text.visible = True
            page.update()
            return

        error_text.visible = False
        close_dialog()
        on_submit({
            "nombre": nombre,
            "descripcion": desc_field.value or "",
            "puntaje_maximo": pts
        })

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Row([
            ft.Icon(ft.Icons.ADD_CIRCLE, color=COLOR_PRIMARY),
            ft.Text("Nuevo Criterio de Evaluación", weight=ft.FontWeight.BOLD, size=16),
        ]),
        content=ft.Container(
            content=ft.Column(
                controls=[
                    nombre_field,
                    desc_field,
                    puntos_field,
                    error_text,
                ],
                tight=True,
                spacing=10,
            ),
            width=400,
        ),
        actions=[
            ft.TextButton(content=ft.Text("Cancelar"), on_click=close_dialog),
            ft.FilledButton(
                content=ft.Text("Agregar Criterio"),
                icon=ft.Icons.CHECK,
                style=ft.ButtonStyle(bgcolor=COLOR_PRIMARY),
                on_click=handle_save,
            ),
        ],
    )

    page.overlay.append(dlg)
    dlg.open = True
    page.update()


def show_add_participante_dialog(page: ft.Page, on_submit):
    """Muestra modal para registrar un proyecto o equipo participante."""
    nombre_field = ft.TextField(label="Nombre del Proyecto o Equipo", hint_text="Ej. Proyecto Alfa", autofocus=True)
    desc_field = ft.TextField(label="Descripción (Opcional)", multiline=True, min_lines=2, max_lines=3)
    integrantes_field = ft.TextField(
        label="Integrantes del Equipo (Opcional)",
        hint_text="Ej. Juan Pérez, María Gómez, Carlos Rojas",
        multiline=True,
        min_lines=2,
    )
    error_text = ft.Text("", color=COLOR_DANGER, size=12, visible=False)

    def close_dialog(e=None):
        dlg.open = False
        page.update()

    def handle_save(e):
        nombre = nombre_field.value.strip() if nombre_field.value else ""
        if not nombre:
            error_text.value = "El nombre del proyecto o equipo es obligatorio."
            error_text.visible = True
            page.update()
            return

        error_text.visible = False
        close_dialog()
        on_submit({
            "nombre": nombre,
            "descripcion": desc_field.value or "",
            "integrantes": integrantes_field.value or "",
        })

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Row([
            ft.Icon(ft.Icons.GROUP_ADD, color=COLOR_PRIMARY),
            ft.Text("Registrar Proyecto / Participante", weight=ft.FontWeight.BOLD, size=16),
        ]),
        content=ft.Container(
            content=ft.Column(
                controls=[
                    nombre_field,
                    desc_field,
                    integrantes_field,
                    error_text,
                ],
                tight=True,
                spacing=10,
            ),
            width=420,
        ),
        actions=[
            ft.TextButton(content=ft.Text("Cancelar"), on_click=close_dialog),
            ft.FilledButton(
                content=ft.Text("Registrar"),
                icon=ft.Icons.CHECK,
                style=ft.ButtonStyle(bgcolor=COLOR_PRIMARY),
                on_click=handle_save,
            ),
        ],
    )

    page.overlay.append(dlg)
    dlg.open = True
    page.update()


def show_add_jurado_dialog(page: ft.Page, usuarios_disponibles: list, on_submit):
    """Muestra modal para asignar un usuario como jurado."""
    options = [
        ft.dropdown.Option(
            key=str(u["id"]),
            text=f"{u.get('full_name') or u.get('username')} (@{u.get('username')})"
        )
        for u in usuarios_disponibles
    ]

    dropdown = ft.Dropdown(
        label="Seleccionar Usuario",
        hint_text="Elige un usuario del sistema...",
        options=options,
        autofocus=True,
    )
    error_text = ft.Text("", color=COLOR_DANGER, size=12, visible=False)

    def close_dialog(e=None):
        dlg.open = False
        page.update()

    def handle_save(e):
        if not dropdown.value:
            error_text.value = "Debes seleccionar un usuario."
            error_text.visible = True
            page.update()
            return

        close_dialog()
        on_submit(int(dropdown.value))

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Row([
            ft.Icon(ft.Icons.PERSON_ADD, color=COLOR_PRIMARY),
            ft.Text("Asignar Miembro del Jurado", weight=ft.FontWeight.BOLD, size=16),
        ]),
        content=ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Solo se listan usuarios que no han sido asignados como jurado en este evento.",
                        size=12,
                        color=ft.Colors.GREY_700,
                    ),
                    dropdown if options else ft.Text("No hay usuarios adicionales disponibles.", color=COLOR_DANGER),
                    error_text,
                ],
                tight=True,
                spacing=10,
            ),
            width=420,
        ),
        actions=[
            ft.TextButton(content=ft.Text("Cancelar"), on_click=close_dialog),
            ft.FilledButton(
                content=ft.Text("Asignar"),
                icon=ft.Icons.CHECK,
                disabled=(len(options) == 0),
                style=ft.ButtonStyle(bgcolor=COLOR_PRIMARY),
                on_click=handle_save,
            ),
        ],
    )

    page.overlay.append(dlg)
    dlg.open = True
    page.update()


def show_confirm_dialog(page: ft.Page, title: str, message: str, on_confirm, is_danger: bool = False):
    """Muestra modal genérico de confirmación para eliminar o ejecutar acciones críticas."""
    def close_dialog(e=None):
        dlg.open = False
        page.update()

    def handle_action(e):
        close_dialog()
        on_confirm()

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Row([
            ft.Icon(ft.Icons.WARNING_AMBER, color=COLOR_DANGER if is_danger else COLOR_PRIMARY),
            ft.Text(title, weight=ft.FontWeight.BOLD, size=16),
        ]),
        content=ft.Text(message, size=14),
        actions=[
            ft.TextButton(content=ft.Text("Cancelar"), on_click=close_dialog),
            ft.FilledButton(
                content=ft.Text("Confirmar"),
                style=ft.ButtonStyle(bgcolor=COLOR_DANGER if is_danger else COLOR_PRIMARY),
                on_click=handle_action,
            ),
        ],
    )

    page.overlay.append(dlg)
    dlg.open = True
    page.update()
