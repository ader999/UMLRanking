# UMLRanking - Aplicación de Escritorio y Móvil en Python Flet

Aplicación construida con **Flet 1.0.1** conectada al backend Django mediante **Django REST Framework (DRF)** para la gestión y evaluación de eventos y rankings académicos.

---

## 🚀 Requisitos Previos

- Python 3.10 o superior (probado con Python 3.14)
- Dependencias instaladas:
  ```bash
  pip install -r requirements.txt
  ```

---

## 📱 Cómo Ejecutar la Aplicación

1. **Asegúrate de que el servidor Django esté corriendo:**
   ```bash
   cd ../plan_de_estudio
   python manage.py runserver
   ```

2. **Ejecutar la app de Flet:**
   ```bash
   cd UMLRanking
   python -m UMLRanking.app
   # O directamente:
   python app.py
   ```

3. **Iniciar Sesión:**
   - La pantalla de bienvenida permite configurar la URL del servidor backend (por defecto `http://127.0.0.1:8000`).
   - Ingresa tus credenciales de usuario registrado en Django.

---

## 🌟 Características y Opciones Incluidas

- **Autenticación Completa**:
  - Inicio de sesión con autenticación basada en Token DRF y soporte de sesión.
  - Indicador de usuario activo y botón de cierre de sesión seguro.
- **Explorador de Eventos**:
  - Búsqueda en tiempo real por nombre y descripción.
  - Filtros rápidos por estado: **Activos**, **Próximos**, **Finalizados** y **Todos**.
  - Tarjetas de eventos con imagen, estado (En Curso, Próximo, Finalizado), fechas, creador y métricas (proyectos, jurados, puntaje máximo).
- **Gestión Integral de Eventos (CRUD)**:
  - Formulario para crear y editar eventos con validación de fechas (cierre posterior a inicio).
  - Eliminación permanente de eventos con confirmación para creadores o superusuarios.
- **Gestión de Participantes**:
  - Listado de proyectos y equipos con sus integrantes y descripciones.
  - Modal para agregar nuevos participantes.
  - Opción para eliminar participantes con diálogo de confirmación.
- **Gestión de Criterios de Evaluación**:
  - Listado de criterios con sus descripciones y puntajes máximos.
  - Modal para agregar criterios personalizados.
  - Eliminación de criterios y recálculo automático del puntaje total del evento.
- **Gestión del Jurado**:
  - Asignación de jurados desde la lista de usuarios del sistema disponibles.
  - Remoción de jurados asignados con advertencia de borrado de calificaciones.
- **Panel de Evaluación del Jurado**:
  - Vista exclusiva para jurados asignados (y administradores) durante eventos activos.
  - Estado de evaluación por participante (**Completado**, **Incompleto**, **Pendiente**).
  - Formulario de calificación con **Sliders sincronizados e inputs numéricos** por criterio.
  - Cálculo dinámico en tiempo real del puntaje total acumulado vs. puntaje máximo.
- **Cuadro de Honor y Resultados**:
  - Podio interactivo de los primeros 3 lugares (Oro, Plata, Bronce).
  - Tabla detallada de clasificación general con puesto, promedios, jurados evaluadores y desglose por criterio.
  - Modo previsualización exclusivo para creadores/administradores en eventos en curso.

---

## 🧪 Ejecución de Pruebas

Para ejecutar la suite de pruebas unitarias de la app Flet:
```bash
python -m unittest UMLRanking.test_flet_app
```

Para ejecutar las pruebas del backend Django (incluyendo el test E2E en vivo con el cliente Flet):
```bash
cd ../plan_de_estudio
python manage.py test eventos
```
