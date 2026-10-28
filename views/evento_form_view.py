import flet as ft
import threading
from datetime import datetime, date, time, timedelta
try:
    from ..theme import (
        COLOR_PRIMARY, COLOR_CARD, COLOR_BORDER, COLOR_TEXT_MAIN, COLOR_TEXT_MUTED, COLOR_DANGER, COLOR_SUCCESS, safe_update
    )
except (ImportError, ValueError):
    from theme import (
        COLOR_PRIMARY, COLOR_CARD, COLOR_BORDER, COLOR_TEXT_MAIN, COLOR_TEXT_MUTED, COLOR_DANGER, COLOR_SUCCESS, safe_update
    )


def _extract_date_str(val, event_data=None):
    """Extrae una cadena de fecha YYYY-MM-DD del valor o datos del evento de DatePicker."""
    if hasattr(val, "strftime"):
        return val.strftime("%Y-%m-%d")
    s = str(val or "").strip()
    if len(s) >= 10 and s[0:4].isdigit() and s[4] == "-" and s[7] == "-":
        return s[:10]
    ed = str(event_data or "").strip()
    if len(ed) >= 10 and ed[0:4].isdigit() and ed[4] == "-" and ed[7] == "-":
        return ed[:10]
    return datetime.now().strftime("%Y-%m-%d")


def _extract_time_str(val, event_data=None):
    """Extrae una cadena de hora HH:MM del valor o datos del evento de TimePicker."""
    if hasattr(val, "strftime"):
        return val.strftime("%H:%M")
    s = str(val or "").strip()
    if ":" in s:
        parts = s.split(":")
        try:
            h = int(parts[0].split()[-1])
            m = int(parts[1][:2])
            return f"{h:02d}:{m:02d}"
        except Exception:
            pass
    ed = str(event_data or "").strip()
    if ":" in ed:
        parts = ed.split(":")
        try:
            h = int(parts[0].split()[-1])
            m = int(parts[1][:2])
            return f"{h:02d}:{m:02d}"
        except Exception:
            pass
    return "12:00"


def _get_initial_datetime(field_value, default_dt=None):
    """Convierte el valor de texto actual a objetos datetime y time iniciales."""
    if default_dt is None:
        default_dt = datetime.now()
    s = str(field_value or "").strip()
    try:
        if "T" in s:
            parts = s.split("T")
            d_parts = [int(p) for p in parts[0].split("-")]
            t_parts = [int(p) for p in parts[1].split(":")[:2]]
            return datetime(d_parts[0], d_parts[1], d_parts[2]), time(t_parts[0], t_parts[1])
        elif len(s) >= 10:
            d_parts = [int(p) for p in s[:10].split("-")]
            return datetime(d_parts[0], d_parts[1], d_parts[2]), default_dt.time()
    except Exception:
        pass
    return default_dt, default_dt.time()


def build_evento_form_view(api_client, evento_id=None, on_success=None, on_cancel=None, page: ft.Page = None):
    """
    Construye la vista de formulario para crear o editar un evento.
    Permite seleccionar fecha y hora con un widget modal interactivo (DatePicker y TimePicker).
    """
    is_edit_mode = evento_id is not None
    title_text = "Editar Evento" if is_edit_mode else "Crear Nuevo Evento"

    now = datetime.now()
    default_inicio = now.strftime("%Y-%m-%dT%H:%M")
    default_fin = (now + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M")

    def resolve_page(e=None):
        if e is not None:
            if hasattr(e, "page") and e.page:
                return e.page
            if hasattr(e, "control") and e.control and hasattr(e.control, "page") and e.control.page:
                return e.control.page
        if page:
            return page
        if hasattr(view_container, "page") and view_container.page:
            return view_container.page
        return None

    def show_dialog_safe(p, dialog_ctrl):
        if not p:
            return
        try:
            if hasattr(p, "show_dialog"):
                p.show_dialog(dialog_ctrl)
            elif hasattr(p, "overlay"):
                p.overlay.append(dialog_ctrl)
                dialog_ctrl.open = True
                p.update()
        except Exception as err:
            print(f"Error mostrando diálogo: {err}")

    def open_datetime_picker(target_field, label_name, e=None):
        p = resolve_page(e)
        if not p:
            return
        init_date, init_time = _get_initial_datetime(target_field.value)

        def on_date_picked(ev):
            sel_date = _extract_date_str(date_picker.value, ev.data)
            current_val = target_field.value or ""
            _, curr_t = _get_initial_datetime(current_val)
            target_field.value = f"{sel_date}T{curr_t.strftime('%H:%M')}"
            safe_update(target_field)

            # Abrir selector de hora de forma encadenada
            def on_time_picked(tev):
                sel_time = _extract_time_str(time_picker.value, tev.data)
                target_field.value = f"{sel_date}T{sel_time}"
                safe_update(target_field)

            time_picker = ft.TimePicker(
                value=curr_t,
                help_text=f"Seleccionar Hora de {label_name}",
                confirm_text="Aceptar",
                cancel_text="Mantener hora",
                on_change=on_time_picked,
            )
            threading.Timer(0.15, lambda: show_dialog_safe(p, time_picker)).start()

        date_picker = ft.DatePicker(
            value=init_date,
            first_date=datetime(2020, 1, 1),
            last_date=datetime(2035, 12, 31),
            help_text=f"Seleccionar Fecha de {label_name}",
            confirm_text="Aceptar",
            cancel_text="Cancelar",
            on_change=on_date_picked,
        )
        show_dialog_safe(p, date_picker)

    def open_only_time_picker(target_field, label_name, e=None):
        p = resolve_page(e)
        if not p:
            return
        init_date, init_time = _get_initial_datetime(target_field.value)
        curr_d_str = init_date.strftime("%Y-%m-%d")

        def on_time_picked(tev):
            sel_time = _extract_time_str(time_picker.value, tev.data)
            target_field.value = f"{curr_d_str}T{sel_time}"
            safe_update(target_field)

        time_picker = ft.TimePicker(
            value=init_time,
            help_text=f"Seleccionar Hora de {label_name}",
            confirm_text="Aceptar",
            cancel_text="Cancelar",
            on_change=on_time_picked,
        )
        show_dialog_safe(p, time_picker)

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
        label="Fecha y Hora de Inicio *",
        hint_text="AAAA-MM-DDTHH:MM",
        helper="Toca para seleccionar fecha y hora con el calendario",
        value=default_inicio,
        read_only=True,
        prefix=ft.IconButton(
            icon=ft.Icons.CALENDAR_MONTH,
            icon_color=COLOR_PRIMARY,
            tooltip="Seleccionar Fecha",
            on_click=lambda e: open_datetime_picker(inicio_field, "Inicio", e),
        ),
        suffix=ft.IconButton(
            icon=ft.Icons.ACCESS_TIME,
            icon_color=COLOR_PRIMARY,
            tooltip="Seleccionar Hora",
            on_click=lambda e: open_only_time_picker(inicio_field, "Inicio", e),
        ),
        on_click=lambda e: open_datetime_picker(inicio_field, "Inicio", e),
    )
    fin_field = ft.TextField(
        label="Fecha y Hora de Cierre *",
        hint_text="AAAA-MM-DDTHH:MM",
        helper="Toca para seleccionar fecha y hora con el calendario",
        value=default_fin,
        read_only=True,
        prefix=ft.IconButton(
            icon=ft.Icons.EVENT_AVAILABLE,
            icon_color=COLOR_PRIMARY,
            tooltip="Seleccionar Fecha",
            on_click=lambda e: open_datetime_picker(fin_field, "Cierre", e),
        ),
        suffix=ft.IconButton(
            icon=ft.Icons.ACCESS_TIME,
            icon_color=COLOR_PRIMARY,
            tooltip="Seleccionar Hora",
            on_click=lambda e: open_only_time_picker(fin_field, "Cierre", e),
        ),
        on_click=lambda e: open_datetime_picker(fin_field, "Cierre", e),
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
                ft.Column([inicio_field, fin_field], spacing=14),
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
        bgcolor=COLOR_CARD,
        border=ft.Border.all(1, COLOR_BORDER),
        border_radius=12,
        padding=16,
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
                card,
            ],
            spacing=16,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=16,
        expand=True,
    )

    view_container.load_data = load_initial_data
    return view_container
