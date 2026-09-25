import flet as ft
from datetime import datetime, timedelta
from ..theme import (
    COLOR_PRIMARY, COLOR_CARD, COLOR_BORDER, COLOR_TEXT_MAIN, COLOR_TEXT_MUTED, COLOR_DANGER, COLOR_SUCCESS, safe_update
)


def build_evento_form_view(api_client, evento_id=None, on_success=None, on_cancel=None):
    """
    Construye la vista de formulario para crear o editar un evento.
    Replica todas las opciones de eventos/form_evento.html.
    """
    is_edit_mode = evento_id is not None
    title_text = "Editar Evento" if is_edit_mode else "Crear Nuevo Evento"

    now = datetime.now()
    default_inicio = now.strftime("%Y-%m-%dT%H:%M")
    default_fin = (now + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M")

    nombre_field = ft.TextField(
        label="Nombre del Evento *",
        hint_text="Ej. Feria de Ciencias 2026",
        autofocus=True,
    )
    desc_field = ft.TextField(
        label="Descripción del Evento",
        hint_text="Explica de qué trata el evento, objetivos y reglas básicas...",
        multiline=True,
        min_lines=3,
        max_lines=5,
    )
    inicio_field = ft.TextField(
        label="Fecha y Hora de Inicio (AAAA-MM-DDTHH:MM) *",
        value=default_inicio,
        prefix_icon=ft.Icons.CALENDAR_TODAY,
    )
    fin_field = ft.TextField(
        label="Fecha y Hora de Cierre (AAAA-MM-DDTHH:MM) *",
        value=default_fin,
        prefix_icon=ft.Icons.EVENT_AVAILABLE,
    )
    requiere_jurado_switch = ft.Switch(
        label="¿Este evento requiere evaluación de jurado?",
        value=True,
    )
    error_container = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.ERROR_OUTLINE, color=COLOR_DANGER, size=18),
            ft.Text("", color=COLOR_DANGER, size=13, expand=True),
        ], spacing=8),
        bgcolor="#FEE2E2",
        border_radius=8,
        padding=10,
        visible=False,
    )
    loading_ring = ft.ProgressRing(visible=False)

    def load_initial_data():
        if is_edit_mode:
            loading_ring.visible = True
            safe_update(loading_ring)
            res = api_client.get_evento(evento_id)
            loading_ring.visible = False
            safe_update(loading_ring)
            if res.get("success"):
                ev = res["data"]
                nombre_field.value = ev.get("nombre", "")
                desc_field.value = ev.get("descripcion", "")
                inicio_raw = ev.get("fecha_inicio", "")
                fin_raw = ev.get("fecha_fin", "")
                inicio_field.value = inicio_raw[:16] if inicio_raw else default_inicio
                fin_field.value = fin_raw[:16] if fin_raw else default_fin
                requiere_jurado_switch.value = ev.get("requiere_jurado", True)
                safe_update(nombre_field)
                safe_update(desc_field)
                safe_update(inicio_field)
                safe_update(fin_field)
                safe_update(requiere_jurado_switch)

    def handle_save(e):
        nombre = nombre_field.value.strip() if nombre_field.value else ""
        if not nombre:
            error_container.content.controls[1].value = "El nombre del evento es obligatorio."
            error_container.visible = True
            safe_update(error_container)
            return

        inicio = inicio_field.value.strip() if inicio_field.value else ""
        fin = fin_field.value.strip() if fin_field.value else ""

        if not inicio or not fin:
            error_container.content.controls[1].value = "Las fechas de inicio y cierre son obligatorias."
            error_container.visible = True
            safe_update(error_container)
            return

        payload = {
            "nombre": nombre,
            "descripcion": desc_field.value or "",
            "fecha_inicio": inicio,
            "fecha_fin": fin,
            "requiere_jurado": requiere_jurado_switch.value,
        }

        save_btn.disabled = True
        loading_ring.visible = True
        safe_update(save_btn)
        safe_update(loading_ring)

        if is_edit_mode:
            result = api_client.update_evento(evento_id, payload)
        else:
            result = api_client.create_evento(payload)

        save_btn.disabled = False
        loading_ring.visible = False
        safe_update(save_btn)
        safe_update(loading_ring)

        if result.get("success"):
            error_container.visible = False
            ev_data = result.get("data", {})
            saved_id = ev_data.get("id", evento_id)
            if on_success:
                on_success(saved_id)
        else:
            err = result.get("error", {})
            msg = ""
            if isinstance(err, dict):
                for k, v in err.items():
                    msg += f"{k}: {v} "
            else:
                msg = str(err)
            error_container.content.controls[1].value = msg or "Error al guardar el evento."
            error_container.visible = True
            safe_update(error_container)

    save_btn = ft.FilledButton(
        content=ft.Row([
            ft.Icon(ft.Icons.SAVE, color=ft.Colors.WHITE, size=18),
            ft.Text("Guardar Evento", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
        ], tight=True),
        style=ft.ButtonStyle(bgcolor=COLOR_PRIMARY),
        height=46,
        on_click=handle_save,
    )

    cancel_btn = ft.OutlinedButton(
        content=ft.Text("Cancelar", weight=ft.FontWeight.BOLD),
        height=46,
        on_click=lambda _: on_cancel(),
    )

    card = ft.Container(
        content=ft.Column(
            controls=[
                # Cabecera
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.CALENDAR_MONTH, color=COLOR_PRIMARY, size=24),
                        ft.Text(title_text, size=20, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MAIN),
                    ],
                    spacing=8,
                ),
                ft.Divider(color=COLOR_BORDER),
                error_container,
                nombre_field,
                desc_field,
                ft.Row([inicio_field, fin_field], spacing=16),
                ft.Container(
                    content=ft.Column([
                        requiere_jurado_switch,
                        ft.Text(
                            "Si está activado, podrás registrar jurados para calificar a los proyectos con criterios definidos.",
                            size=12,
                            color=COLOR_TEXT_MUTED,
                        ),
                    ], spacing=2),
                    bgcolor="#F8FAFC",
                    border=ft.Border.all(1, COLOR_BORDER),
                    border_radius=8,
                    padding=12,
                ),
                loading_ring,
                ft.Row(
                    controls=[cancel_btn, save_btn],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            ],
            spacing=16,
        ),
        width=640,
        bgcolor=COLOR_CARD,
        border=ft.Border.all(1, COLOR_BORDER),
        border_radius=12,
        padding=28,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=10,
            color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK),
            offset=ft.Offset(0, 2),
        ),
    )

    view_container = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row([
                    ft.TextButton(
                        content=ft.Row([ft.Icon(ft.Icons.ARROW_BACK, size=16), ft.Text("Regresar")]),
                        on_click=lambda _: on_cancel(),
                    )
                ]),
                ft.Row([card], alignment=ft.MainAxisAlignment.CENTER),
            ],
            spacing=16,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=24,
        expand=True,
    )

    view_container.load_data = load_initial_data
    return view_container
