# Guía de Usuario - Dental.AI

## 📚 Manual de Usuario para Consultorio Dental

### Contenido
1. [Primeros Pasos](#primeros-pasos)
2. [Panel de Control (Dashboard)](#panel-de-control)
3. [Gestión de Pacientes](#gestión-de-pacientes)
4. [Expediente Clínico](#expediente-clínico)
5. [Tratamientos](#tratamientos)
6. [Agenda de Citas](#agenda-de-citas)
7. [Finanzas](#finanzas)
8. [Presupuestos](#presupuestos)
9. [Reportes](#reportes)
10. [Perfil del Doctor](#perfil-del-doctor)

---

## Primeros Pasos

### Acceder al Sistema

1. Abrir navegador web (Chrome, Firefox, Safari, Edge)
2. Ir a la dirección: `http://localhost` (o la dirección proporcionada por su administrador)
3. Iniciar sesión con sus credenciales

**Credenciales por defecto (desarrollo):**
- Usuario: `admin`
- Contraseña: `admin`

### Navegación Principal

El sistema está organizado en módulos principales:
- **Dashboard**: Vista general del día
- **Pacientes**: Registro y gestión
- **Citas**: Calendario y agenda
- **Tratamientos**: Seguimiento de procedimientos
- **Finanzas**: Control de pagos y gastos
- **Presupuestos**: Cotizaciones
- **Reportes**: Estadísticas y análisis

---

## Panel de Control (Dashboard)

### ¿Qué veo en el Dashboard?

**Resumen del Día:**
- 📅 **Citas de Hoy**: Número de citas programadas
- 👥 **Pacientes Atendidos**: Citas completadas
- 💰 **Ingresos del Día**: Total de pagos recibidos

**Resumen General:**
- ⚠️ **Adeudos Pendientes**: Total de deudas de pacientes
- 🔧 **Tratamientos Activos**: Tratamientos en curso
- 👤 **Total de Pacientes**: Pacientes registrados
- 📆 **Citas Próximas**: Citas confirmadas futuras

**Resumen Mensual:**
- 📈 **Ingresos del Mes**: Total ingresado
- 📉 **Gastos del Mes**: Total de gastos
- 💵 **Balance Neto**: Diferencia (ingresos - gastos)

**Acceso Rápido:**
- Nuevo Paciente
- Nueva Cita
- Nuevo Tratamiento

---

## Gestión de Pacientes

### Registrar Nuevo Paciente

1. Click en "Nuevo Paciente" desde el Dashboard
2. Llenar el formulario:
   - **Nombre**: Nombre(s) del paciente
   - **Apellidos**: Apellidos completos
   - **Género**: Masculino, Femenino u Otro
   - **Fecha de Nacimiento**: Seleccionar del calendario
   - **Teléfono**: Con código de país (+52 para México)
   - **Email**: Correo electrónico (opcional)
   - **Método de Confirmación**: WhatsApp, SMS o Email
   - **Notas**: Información adicional relevante
3. Click en "Guardar"

### Buscar Pacientes

**Opciones de búsqueda:**
- Por nombre o apellido
- Por teléfono
- Por correo electrónico

**Filtros disponibles:**
- Género
- Estado (activo/inactivo)
- Método de contacto preferido

### Ver Ficha del Paciente

Al seleccionar un paciente verá:
- **Datos básicos**: Información de contacto y edad
- **Estadísticas**:
  - Número de tratamientos
  - Citas totales
  - Saldo pendiente
- **Botón de WhatsApp**: Contacto directo
- **Historial**: Todos los registros relacionados

---

## Expediente Clínico

### Historial Médico

**Información a registrar:**
- ✅ Enfermedades crónicas (diabetes, hipertensión, etc.)
- 💊 Medicamentos actuales
- ⚠️ Alergias (medicamentos, materiales dentales)
- 🦷 Tratamientos dentales previos
- 🚬 Hábitos (fumar, alcohol)
- 📝 Notas adicionales

### Notas Clínicas

**Crear nueva nota:**
1. En el expediente del paciente
2. Click "Nueva Nota Clínica"
3. Llenar:
   - Fecha
   - Título
   - Descripción detallada
   - Observaciones
4. Guardar

### Archivos Clínicos

**Tipos de archivos soportados:**
- 📸 Fotos clínicas
- 🔬 Radiografías
- 📄 Documentos PDF
- 📋 Otros documentos

**Subir archivos:**
1. Seleccionar tipo de archivo
2. Título descriptivo
3. Descripción (opcional)
4. Fecha de toma
5. Seleccionar archivo
6. Subir

---

## Tratamientos

### Crear Nuevo Tratamiento

1. Desde el perfil del paciente o menú principal
2. Completar información:
   - **Tipo de Tratamiento**: Ej. Ortodoncia, Implante, Endodoncia
   - **Dentista Responsable**: Nombre del doctor
   - **Fecha de Inicio**: Cuando comienza
   - **Número de Sesiones**: Total planificadas
   - **Precio Total**: Costo completo del tratamiento
   - **Descripción**: Detalles del procedimiento

### Estados del Tratamiento

- 🔄 **En Curso**: Tratamiento activo
- ✅ **Terminado**: Completado exitosamente
- ❌ **Cancelado**: Descontinuado
- 💰 **Con Adeudo**: Pendiente de pago

### Registrar Avances

**Por cada sesión:**
1. Click "Agregar Avance"
2. Completar:
   - Número de sesión
   - Fecha de la sesión
   - Comentarios del doctor
   - Subir fotos/documentos (opcional)
3. Marcar sesión como completada (opcional)

### Registrar Pagos

1. En el tratamiento, click "Agregar Pago"
2. Ingresar:
   - Monto
   - Método de pago
   - Número de referencia (opcional)
   - Notas
3. El sistema actualiza automáticamente el saldo pendiente

---

## Agenda de Citas

### Programar Nueva Cita

1. Click "Nueva Cita"
2. Completar:
   - **Paciente**: Seleccionar de la lista
   - **Tipo de Consulta**: 
     - Primera Visita
     - Seguimiento
     - Limpieza
     - Extracción
     - Empaste
     - Endodoncia
     - Ortodoncia
     - Implante
     - Emergencia
     - Otro
   - **Fecha**: Seleccionar del calendario
   - **Hora de Inicio**: Ej. 10:00
   - **Hora de Fin**: Ej. 11:00
   - **Sillón/Unidad**: Ej. Sillón 1
   - **Notas**: Información adicional

### Estados de Cita

- ⏳ **Pendiente**: Requiere confirmación
- ✅ **Confirmada**: Paciente confirmó asistencia
- ❌ **Cancelada**: Cita cancelada
- 🏁 **Completada**: Paciente atendido
- 🚫 **No Asistió**: Paciente no se presentó

### Vistas del Calendario

- **Hoy**: Citas del día actual
- **Semana**: Próximos 7 días
- **Mes**: Vista mensual completa

### Recordatorios

El sistema puede enviar recordatorios automáticos vía:
- WhatsApp
- SMS
- Email

(Configuración en desarrollo)

---

## Finanzas

### Registrar Pago

1. Ir a "Finanzas" → "Pagos"
2. Click "Nuevo Pago"
3. Completar:
   - Paciente
   - Tratamiento (opcional)
   - Monto
   - Método de pago: Efectivo, Transferencia, Tarjeta
   - Fecha
   - Número de referencia (para transferencias)
   - Notas

### Registrar Gasto

1. Ir a "Finanzas" → "Gastos"
2. Click "Nuevo Gasto"
3. Completar:
   - **Categoría**:
     - Materiales
     - Laboratorio
     - Renta
     - Sueldos
     - Servicios
     - Equipo
     - Mantenimiento
     - Marketing
     - Otros
   - Descripción
   - Monto
   - Fecha
   - Proveedor (opcional)
   - Número de factura (opcional)

### Ver Resumen Financiero

**Resumen de Pagos:**
- Total del día
- Total del mes
- Por método de pago
- Por paciente

**Resumen de Gastos:**
- Total del día
- Total del mes
- Por categoría
- Por proveedor

---

## Presupuestos

### Crear Presupuesto

1. Ir a "Presupuestos"
2. Click "Nuevo Presupuesto"
3. Completar:
   - Paciente
   - Título del presupuesto
   - Descripción general
   - Válido hasta (fecha de expiración)

### Agregar Items al Presupuesto

Para cada tratamiento o procedimiento:
- Tipo de tratamiento
- Descripción
- Cantidad
- Precio unitario
- (El subtotal se calcula automáticamente)

El **total del presupuesto** se calcula sumando todos los items.

### Estados del Presupuesto

- ⏳ **Pendiente**: Esperando respuesta del paciente
- ✅ **Aprobado**: Paciente aceptó
- ❌ **Rechazado**: Paciente declinó
- 🔄 **Convertido**: Ya se creó el tratamiento

### Convertir a Tratamiento

Cuando el paciente acepta:
1. Abrir el presupuesto
2. Click "Convertir a Tratamiento"
3. El sistema crea automáticamente un nuevo tratamiento
4. Redirige al tratamiento creado

---

## Reportes

### Tipos de Reportes Disponibles

**Ingresos:**
- Diarios
- Semanales
- Mensuales

**Gastos:**
- Diarios
- Semanales
- Mensuales

**Análisis:**
- Tratamientos más comunes
- Pacientes con adeudo

### Generar Reporte

1. Ir a "Reportes"
2. Seleccionar tipo de reporte
3. Definir rango de fechas
4. Click "Generar"
5. Elegir formato de exportación:
   - PDF
   - Excel
   - CSV

---

## Perfil del Doctor

### Configurar Perfil

1. Ir a "Perfil"
2. Completar/Actualizar:
   - **Nombre completo**
   - **Especialidad**: Ej. Odontología General, Ortodoncista
   - **Cédula profesional**: Número oficial
   - **Teléfono del consultorio**
   - **Email profesional**
   - **Nombre del consultorio**
   - **Dirección del consultorio**

### Subir Archivos

- **Firma Digital**: Imagen de firma para documentos
- **Logo del Consultorio**: Para encabezados y reportes

---

## Consejos y Mejores Prácticas

### 💡 Tips para Uso Diario

1. **Revisar Dashboard cada mañana** para planificar el día
2. **Actualizar estados de citas** conforme se atienden
3. **Registrar pagos inmediatamente** al recibirlos
4. **Tomar fotos del progreso** en cada sesión de tratamiento
5. **Mantener notas clínicas detalladas** para referencia futura
6. **Confirmar citas** el día anterior vía WhatsApp
7. **Generar reportes mensuales** para análisis financiero

### ⚠️ Recordatorios Importantes

- ✅ Actualizar expediente médico en cada visita
- ✅ Verificar alergias antes de cada procedimiento
- ✅ Documentar consentimientos informados
- ✅ Respaldar datos periódicamente
- ✅ Revisar adeudos pendientes semanalmente

### 🔒 Seguridad y Privacidad

- 🔐 No compartir credenciales de acceso
- 🔐 Cerrar sesión al terminar
- 🔐 Información médica es confidencial
- 🔐 No tomar capturas de pantalla de datos de pacientes
- 🔐 Reportar cualquier acceso no autorizado

---

## Soporte Técnico

### ¿Necesita Ayuda?

**Para problemas técnicos:**
- Contactar al administrador del sistema
- Reportar bugs o errores
- Solicitar nuevas funcionalidades

**Para capacitación:**
- Solicitar sesión de entrenamiento
- Manual de usuario disponible
- Videos tutoriales (próximamente)

---

## Glosario de Términos

- **Dashboard**: Panel de control principal
- **Expediente**: Registro médico completo de un paciente
- **Tratamiento**: Procedimiento dental planificado
- **Sesión**: Cada visita dentro de un tratamiento
- **Adeudo**: Saldo pendiente de pago
- **Presupuesto**: Cotización de tratamiento
- **Recordatorio**: Notificación automática de cita

---

**Última actualización:** Febrero 2026

**Sistema Dental.AI** - Gestión Profesional para Consultorios Dentales
