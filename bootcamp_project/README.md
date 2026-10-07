# Carro de cursos con Django y DRF

MVP educativo con nombres de negocio en español. El pago es simulado: `aprobar: true` confirma la compra, y `false` la rechaza. No existe una pasarela ni movimiento real de dinero.

## Preparación

Desde `bootcamp_project`:

```powershell
..\venv\Scripts\python.exe -m pip install -r requirements.txt
..\venv\Scripts\python.exe manage.py migrate
..\venv\Scripts\python.exe manage.py createsuperuser
..\venv\Scripts\python.exe manage.py runserver
```

Se requieren `SECRET_KEY` y `DATABASE_URL` en `.env` (archivo local ignorado por Git). Por ejemplo, `DATABASE_URL=postgres://usuario:clave@localhost:5432/bootcamp`. Ejecuta las migraciones en la base indicada por esa URL. El superusuario es el único administrador. No se usa Django Admin.

## Páginas web

Con el servidor en marcha, abre `/` para ver el catálogo. La navegación cambia según la cuenta:

| Rol | Páginas |
| --- | --- |
| Estudiante | Catálogo, detalle del curso, carrito, órdenes y mis cursos. |
| Profesor | `/docencia/`: cursos asignados y estudiantes con inscripción confirmada en cada curso. |
| Superusuario | `/gestion/`: panel, cursos, profesores, inscripciones y órdenes. |

Las páginas usan sesiones de Django y comparten las reglas de compra con la API. La reserva dura 15 minutos y el pago desde la página de órdenes es simulado. El superusuario puede crear y editar cursos, asignar profesores desde el formulario de curso, crear cuentas de profesor e inscribir estudiantes directamente sin cobro.

El HTML reutilizable está en `templates/web/` y sus estilos en `static/web/site.css`. `templates/EsquemaMolde.html` y `templates/styles.css` quedan como boceto original.

## Recorrido

1. Crear un estudiante con `POST /api/registro/` usando `username`, `email` y `password`.
2. Iniciar sesión con `POST /api/token/` usando `username` y `password`. Enviar `Authorization: Bearer <access>` en las peticiones protegidas. Renovar con `POST /api/token/renovar/` y el `refresh`.
3. Crear profesores con el superusuario en `POST /api/gestion/usuarios/` (`rol: "profesor"`).
4. Crear un curso en `POST /api/gestion/cursos/` con `nombre`, `cupos`, `precio`, `fecha_inicio`, `fecha_termino`, `fecha_limite_inscripcion` y `estado: "publicado"`. `descripcion` y `objetivos` son opcionales. Fechas en formato ISO 8601 con zona horaria.
5. Asignar profesor con `POST /api/gestion/cursos/<id>/profesores/` y `profesor_id`.
6. El estudiante agrega con `POST /api/carrito/agregar/` y `curso_id`, crea una orden con `POST /api/ordenes/crear/` y paga con `POST /api/ordenes/<id>/pagar/` y `{"aprobar": true}`.
7. Consultar historial en `GET /api/ordenes/` y `GET /api/inscripciones/`. Cancelar antes del inicio con `POST /api/inscripciones/<id>/cancelar/`.

## Endpoints

| Público | Estudiante autenticado | Superusuario |
| --- | --- | --- |
| `GET /api/cursos/` | `GET /api/carrito/` | `GET/POST /api/gestion/cursos/` |
| `GET /api/cursos/<id>/` | `POST /api/carrito/agregar/` | `GET/PATCH /api/gestion/cursos/<id>/` |
| `POST /api/registro/` | `DELETE /api/carrito/quitar/<id>/` | `POST/DELETE /api/gestion/cursos/<id>/profesores/` |
| `POST /api/token/` | `POST /api/ordenes/crear/` | `GET/POST /api/gestion/usuarios/` |
| `POST /api/token/renovar/` | `POST /api/ordenes/<id>/pagar/` | `POST /api/gestion/inscripciones/` |
| | `GET /api/ordenes/`, `GET /api/inscripciones/` | `GET /api/gestion/ordenes/` |
| | `POST /api/inscripciones/<id>/cancelar/` | |

`POST /api/gestion/inscripciones/` recibe `estudiante_id` y `curso_id` para inscribir directamente sin cobro.

## Reglas

- Cada usuario tiene un rol único. Registro público crea estudiantes; solo el superusuario crea profesores.
- Un curso se compra solo si está publicado y aún no llegó su fecha de inicio o límite de inscripción.
- Cada ítem reserva un cupo durante 15 minutos. Al crear la orden se conserva el mismo vencimiento; agregar al carrito nuevamente no prolonga una reserva activa.
- Las reservas vencidas dejan de contar automáticamente, aunque permanezcan en el historial. No se requiere un proceso periódico para liberar cupos.
- Una inscripción confirmada bloquea compras duplicadas. Tras cancelar y reembolsar antes del inicio, se puede comprar otra vez.
- La cancelación actualiza el reembolso simulado y libera el cupo. En órdenes con varios cursos, el pago conserva el monto reembolsado y la orden pasa a `reembolsada` cuando todos sus ítems se reembolsan.

Para ejecutar las pruebas: `..\venv\Scripts\python.exe manage.py test apps.courses.tests`.

PostgreSQL permite los bloqueos de filas usados para reservar cupos con compradores simultáneos. Antes de un despliegue real conviene verificar ese comportamiento bajo concurrencia.
