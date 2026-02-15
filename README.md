# Dental.AI - Sistema de Gestión de Consultorio Dental

Sistema profesional completo para la gestión de consultorios dentales, diseñado para uso diario real con enfoque en gestión de pacientes, agenda, expedientes clínicos y control financiero.

## 🎯 Características Principales

### Módulos Implementados

1. **Dashboard (Página Principal)**
   - Resumen del día: citas, pacientes atendidos, ingresos
   - Estadísticas generales: adeudos pendientes, tratamientos activos
   - Resumen mensual: ingresos, gastos, balance neto
   - Acceso rápido a funciones principales

2. **Registro de Pacientes**
   - Datos básicos: nombre, apellidos, género, fecha de nacimiento
   - Información de contacto: teléfono, email
   - Método de confirmación preferido (WhatsApp, SMS, Email)
   - Link directo a WhatsApp
   - Notas generales del paciente

3. **Expediente Clínico**
   - Historial médico completo
   - Registro de alergias
   - Medicamentos actuales
   - Enfermedades crónicas
   - Notas clínicas con archivos adjuntos
   - Subida de fotos clínicas, radiografías y documentos PDF

4. **Gestión de Tratamientos**
   - Tipo de tratamiento y dentista responsable
   - Control de sesiones (planificadas vs completadas)
   - Seguimiento financiero (precio total, pagos, saldo pendiente)
   - Estados: en curso, terminado, cancelado, con adeudo
   - Registro de avances por sesión
   - Archivos adjuntos por sesión (fotos, reportes, radiografías)

5. **Agenda/Calendario**
   - Vista de citas diarias, semanales y mensuales
   - Tipos de consulta predefinidos
   - Asignación de sillón/unidad
   - Estados de cita: pendiente, confirmada, cancelada, completada
   - Sistema de recordatorios

6. **Presupuestos**
   - Creación de presupuestos detallados por tratamiento
   - Desglose por items con cantidad y precio unitario
   - Estados: pendiente, aprobado, rechazado
   - Conversión directa de presupuesto a tratamiento

7. **Finanzas**
   - **Ingresos**: registro de pagos por paciente y tratamiento
   - Métodos de pago: efectivo, transferencia, tarjeta
   - **Gastos**: control por categoría (materiales, laboratorio, renta, sueldos, etc.)
   - Reportes financieros diarios y mensuales

8. **Reportes**
   - Sistema de generación de reportes personalizables
   - Exportación en múltiples formatos (PDF, Excel, CSV)
   - Tipos: ingresos, gastos, tratamientos comunes, adeudos

9. **Perfiles de Doctor**
   - Nombre completo y especialidad
   - Cédula profesional
   - Datos del consultorio
   - Firma digital y logo

## 🏗️ Arquitectura del Sistema

### Backend (Django REST Framework)

```
backend/
├── _config/              # Configuración del proyecto
│   ├── settings.py       # Configuración Django
│   ├── urls.py          # URLs principales
│   └── dashboard.py     # API del dashboard
├── patients/            # Gestión de pacientes
├── clinical/           # Expedientes clínicos
├── treatments/         # Tratamientos
├── appointments/       # Agenda y citas
├── finances/          # Pagos y gastos
├── budgets/           # Presupuestos
├── reports/           # Reportes
└── profiles/          # Perfiles de doctores
```

#### Modelos de Base de Datos

**Pacientes:**
- Patient: Información básica y contacto

**Clínico:**
- MedicalHistory: Historial médico
- ClinicalNote: Notas clínicas
- ClinicalFile: Archivos clínicos (fotos, PDFs, radiografías)

**Tratamientos:**
- Treatment: Información del tratamiento
- TreatmentProgress: Avances por sesión
- TreatmentFile: Archivos de seguimiento

**Citas:**
- Appointment: Información de citas
- AppointmentReminder: Log de recordatorios

**Finanzas:**
- Payment: Pagos recibidos
- Expense: Gastos del consultorio

**Presupuestos:**
- Budget: Presupuesto general
- BudgetItem: Items individuales

**Otros:**
- DoctorProfile: Perfil del doctor
- Report: Reportes generados

### Frontend (Next.js + TypeScript + Tailwind CSS)

```
frontend/
├── app/
│   ├── layout.tsx       # Layout principal
│   ├── page.tsx         # Dashboard
│   ├── globals.css      # Estilos globales
│   └── components/      # Componentes reutilizables
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.ts
```

## 🚀 Instalación y Uso

### Requisitos Previos

- Docker y Docker Compose
- Git

### Despliegue en Producción

El sistema está desplegado en:
- **Frontend:** Vercel (https://dientex.com)
- **Backend:** Railway (https://api.dientex.com)
- **Base de Datos:** PostgreSQL en Railway

**📖 Guías de Despliegue:**
- [DEPLOYMENT.md](DEPLOYMENT.md) - Guía completa de despliegue
- [VERCEL_SETUP.md](VERCEL_SETUP.md) - Configuración de Vercel paso a paso
- [CHANGES.md](CHANGES.md) - Cambios recientes y estructura de API

**🔧 Verificación:**
```bash
# Ejecutar script de verificación
./verify-deployment.sh
```

### Inicio Rápido (Desarrollo Local)

1. **Clonar el repositorio:**
```bash
git clone https://github.com/dymarso/dental.ai.git
cd dental.ai
```

2. **Construir e iniciar servicios:**
```bash
# Construir las imágenes
DOCKER_BUILDKIT=1 docker compose -f development.yml build --parallel

# Iniciar servicios
docker compose -f development.yml up -d
```

3. **Acceder a la aplicación:**
- Frontend: http://localhost (puerto 80)
- Backend API: http://localhost/api/
- Django Admin: http://localhost/admin/
  - Usuario: `admin`
  - Contraseña: `admin`

### Endpoints de la API

**Nota:** Todos los endpoints de API ahora usan el prefijo `/api/`

**Dashboard:**
- `GET /api/dashboard/` - Resumen del dashboard

**Pacientes:**
- `GET /api/patients/` - Lista de pacientes
- `POST /api/patients/` - Crear paciente
- `GET /api/patients/{id}/` - Detalle de paciente
- `PUT /api/patients/{id}/` - Actualizar paciente
- `DELETE /api/patients/{id}/` - Eliminar paciente
- `GET /api/patients/{id}/summary/` - Resumen del paciente

**Tratamientos:**
- `GET /api/treatments/` - Lista de tratamientos
- `POST /api/treatments/` - Crear tratamiento
- `GET /api/treatments/{id}/` - Detalle de tratamiento
- `POST /api/treatments/{id}/add_progress/` - Agregar avance
- `POST /api/treatments/{id}/add_payment/` - Agregar pago

**Citas:**
- `GET /api/appointments/` - Lista de citas
- `GET /api/appointments/today/` - Citas de hoy
- `GET /api/appointments/week/` - Citas de la semana
- `GET /api/appointments/month/` - Citas del mes
- `POST /api/appointments/` - Crear cita

**Finanzas:**
- `GET /api/finances/payments/` - Lista de pagos
- `GET /api/finances/payments/summary/` - Resumen de pagos
- `GET /api/finances/expenses/` - Lista de gastos
- `GET /api/finances/expenses/summary/` - Resumen de gastos

**Presupuestos:**
- `GET /api/budgets/` - Lista de presupuestos
- `POST /api/budgets/` - Crear presupuesto
- `POST /api/budgets/{id}/convert_to_treatment/` - Convertir a tratamiento

## 🛠️ Tecnologías Utilizadas

### Backend
- Python 3.12
- Django 4.2
- Django REST Framework 3.14
- PostgreSQL 17
- Pillow (procesamiento de imágenes)
- django-filter (filtrado avanzado)

### Frontend
- Next.js 15
- React 19
- TypeScript 5
- Tailwind CSS 4
- date-fns (manejo de fechas)

### Infraestructura
- Docker & Docker Compose
- Traefik (reverse proxy)
- PostgreSQL (base de datos)

## 📊 Funcionalidades Avanzadas

### Implementadas
- ✅ Modelos completos de base de datos con relaciones
- ✅ API RESTful completa con Django REST Framework
- ✅ Dashboard interactivo con estadísticas en tiempo real
- ✅ Sistema de filtros y búsqueda en todas las entidades
- ✅ Soporte para múltiples archivos (fotos, PDFs, radiografías)
- ✅ Cálculos automáticos (edad, saldo pendiente, progreso)
- ✅ Panel de administración Django configurado

### Próximas (Fase 3)
- 🔜 Sistema de recordatorios automáticos (WhatsApp, SMS, Email)
- 🔜 Integración con almacenamiento S3
- 🔜 Búsqueda global avanzada
- 🔜 Gestión de consentimientos informados
- 🔜 Auditoría de cambios en expedientes
- 🔜 Exportación completa de expedientes
- 🔜 Alertas de tratamientos incompletos
- 🔜 Modo oscuro
- 🔜 Cifrado de datos médicos sensibles

## 🔒 Seguridad

- CORS configurado correctamente
- CSRF protection habilitado
- Validación de datos en backend
- Índices de base de datos para rendimiento
- Preparado para HTTPS en producción
- Soporte para variables de entorno

## 📝 Buenas Prácticas Médicas y Legales

El sistema está diseñado considerando:
- Confidencialidad de datos médicos
- Trazabilidad de cambios (timestamps en todos los modelos)
- Respaldo de información
- Cumplimiento HIPAA-ready (con configuración adecuada)
- Soporte para firmas digitales
- Gestión de consentimientos

## 🤝 Contribuir

Este es un sistema profesional en desarrollo activo. Las contribuciones son bienvenidas.

## 📄 Licencia

Ver archivo LICENSE para más información.

## 👨‍⚕️ Autores

Desarrollado para consultorios dentales modernos que buscan eficiencia y profesionalismo.

---

**Nota:** Este sistema está diseñado para uso real en consultorios dentales. Asegúrese de cumplir con las regulaciones locales de privacidad y protección de datos médicos en su jurisdicción.
