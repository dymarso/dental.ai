# Arquitectura del Sistema Dental.AI

## 📋 Tabla de Contenidos

1. [Visión General](#visión-general)
2. [Arquitectura de Alto Nivel](#arquitectura-de-alto-nivel)
3. [Modelos de Base de Datos](#modelos-de-base-de-datos)
4. [API REST](#api-rest)
5. [Frontend](#frontend)
6. [Flujos de Usuario](#flujos-de-usuario)
7. [Seguridad](#seguridad)
8. [Escalabilidad](#escalabilidad)

## Visión General

Dental.AI es un sistema full-stack diseñado específicamente para la gestión integral de consultorios dentales. La arquitectura sigue un patrón de microservicios ligeros con separación clara entre frontend y backend.

### Stack Tecnológico

```
┌─────────────────────────────────────────────────┐
│              CLIENTE (Navegador)                 │
└─────────────────────────────────────────────────┘
                      ↓ HTTPS
┌─────────────────────────────────────────────────┐
│           Traefik (Reverse Proxy)                │
│  - Routing                                       │
│  - SSL/TLS                                       │
│  - Rate Limiting                                 │
│  - Compression                                   │
└─────────────────────────────────────────────────┘
         ↓                              ↓
┌────────────────────┐      ┌──────────────────────┐
│   Frontend         │      │   Backend            │
│   Next.js 15       │      │   Django 4.2         │
│   React 19         │      │   DRF 3.14           │
│   TypeScript       │      │   Python 3.12        │
│   Tailwind CSS     │      │                      │
└────────────────────┘      └──────────────────────┘
                                      ↓
                          ┌──────────────────────┐
                          │   PostgreSQL 17      │
                          │   (Base de Datos)    │
                          └──────────────────────┘
```

## Arquitectura de Alto Nivel

### Capas de la Aplicación

```
┌──────────────────────────────────────────────────┐
│           CAPA DE PRESENTACIÓN                   │
│  - Next.js App Router                            │
│  - React Server Components                       │
│  - Client Components                             │
│  - Tailwind CSS para estilos                     │
└──────────────────────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────────┐
│           CAPA DE API REST                       │
│  - Django REST Framework                         │
│  - ViewSets & Serializers                        │
│  - Autenticación & Permisos                      │
│  - Filtros & Paginación                          │
└──────────────────────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────────┐
│           CAPA DE LÓGICA DE NEGOCIO              │
│  - Modelos Django                                │
│  - Validaciones                                  │
│  - Cálculos automáticos                          │
│  - Signals & Hooks                               │
└──────────────────────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────────┐
│           CAPA DE PERSISTENCIA                   │
│  - PostgreSQL (datos estructurados)              │
│  - File System / S3 (archivos multimedia)        │
│  - Redis (cache - futuro)                        │
└──────────────────────────────────────────────────┘
```

## Modelos de Base de Datos

### Diagrama ER Simplificado

```
┌──────────────┐
│   Patient    │
└──────┬───────┘
       │ 1
       │
       │ n
   ┌───┴────────────┬─────────────┬──────────────┬─────────────┐
   │                │             │              │             │
┌──┴───────────┐ ┌──┴──────┐ ┌───┴────────┐ ┌───┴────────┐ ┌─┴────────┐
│ Treatment    │ │Appointmt│ │  Clinical  │ │  Payment   │ │  Budget  │
│              │ │         │ │  Records   │ │            │ │          │
└──┬───────────┘ └─────────┘ └────────────┘ └────────────┘ └──────────┘
   │ 1
   │
   │ n
┌──┴──────────────┐
│ TreatmentProgress│
└──┬──────────────┘
   │ 1
   │
   │ n
┌──┴──────────────┐
│ TreatmentFile   │
└─────────────────┘
```

### Esquema Detallado de Tablas Principales

#### patients_patient
```sql
CREATE TABLE patients_patient (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    gender CHAR(1) CHECK (gender IN ('M', 'F', 'O')),
    date_of_birth DATE NOT NULL,
    phone VARCHAR(17) NOT NULL,
    email VARCHAR(254),
    preferred_contact_method VARCHAR(10),
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_name (last_name, first_name),
    INDEX idx_phone (phone),
    INDEX idx_email (email)
);
```

#### treatments_treatment
```sql
CREATE TABLE treatments_treatment (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients_patient(id),
    treatment_type VARCHAR(200) NOT NULL,
    dentist_responsible VARCHAR(200) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    total_sessions INTEGER DEFAULT 1,
    completed_sessions INTEGER DEFAULT 0,
    total_price DECIMAL(10, 2) NOT NULL,
    amount_paid DECIMAL(10, 2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'in_progress',
    description TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_patient_status (patient_id, status),
    INDEX idx_start_date (start_date)
);
```

#### appointments_appointment
```sql
CREATE TABLE appointments_appointment (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients_patient(id),
    consultation_type VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    dental_unit VARCHAR(50),
    status VARCHAR(20) DEFAULT 'pending',
    notes TEXT,
    reminder_sent BOOLEAN DEFAULT FALSE,
    reminder_sent_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_date_time (date, start_time),
    INDEX idx_patient_date (patient_id, date),
    INDEX idx_status (status)
);
```

#### finances_payment
```sql
CREATE TABLE finances_payment (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients_patient(id),
    treatment_id INTEGER REFERENCES treatments_treatment(id),
    amount DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(20) NOT NULL,
    payment_date DATE NOT NULL,
    reference_number VARCHAR(100),
    notes TEXT,
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_payment_date (payment_date),
    INDEX idx_patient_date (patient_id, payment_date)
);
```

## API REST

### Estructura de URLs

```
/api/
├── health/                    # Health check
├── dashboard/                 # Dashboard summary
├── patients/                  # Patient CRUD
│   ├── {id}/                 # Patient detail
│   └── {id}/summary/         # Patient summary
├── treatments/                # Treatment CRUD
│   ├── {id}/                 # Treatment detail
│   ├── {id}/add_progress/    # Add progress
│   └── {id}/add_payment/     # Add payment
├── appointments/              # Appointment CRUD
│   ├── today/                # Today's appointments
│   ├── week/                 # Week's appointments
│   └── month/                # Month's appointments
├── finances/
│   ├── payments/             # Payment CRUD
│   │   └── summary/          # Payment summary
│   └── expenses/             # Expense CRUD
│       └── summary/          # Expense summary
└── budgets/                   # Budget CRUD
    └── {id}/convert_to_treatment/  # Convert to treatment
```

### Ejemplo de Respuesta API

**GET /api/dashboard/**
```json
{
  "today": {
    "appointments": 5,
    "patients_attended": 3,
    "income": 15000.00
  },
  "pending_debts": 45000.00,
  "active_treatments": 12,
  "total_patients": 150,
  "upcoming_appointments": 8,
  "monthly": {
    "income": 250000.00,
    "expenses": 80000.00,
    "net": 170000.00
  }
}
```

**GET /api/patients/**
```json
{
  "count": 150,
  "next": "/api/patients/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "full_name": "García López, Juan",
      "gender": "M",
      "age": 35,
      "phone": "+525512345678",
      "email": "juan@example.com",
      "is_active": true
    },
    ...
  ]
}
```

## Frontend

### Estructura de Componentes

```
app/
├── layout.tsx                 # Root layout
├── page.tsx                   # Dashboard (home)
├── globals.css               # Global styles
├── patients/
│   ├── page.tsx              # Patient list
│   ├── [id]/
│   │   ├── page.tsx          # Patient detail
│   │   └── edit/
│   │       └── page.tsx      # Edit patient
│   └── new/
│       └── page.tsx          # New patient
├── treatments/
│   ├── page.tsx              # Treatment list
│   └── [id]/
│       └── page.tsx          # Treatment detail
├── appointments/
│   ├── page.tsx              # Calendar view
│   └── new/
│       └── page.tsx          # New appointment
├── finances/
│   ├── page.tsx              # Finance dashboard
│   ├── payments/
│   │   └── page.tsx          # Payments list
│   └── expenses/
│       └── page.tsx          # Expenses list
└── components/
    ├── ui/                   # UI components
    ├── forms/                # Form components
    └── charts/               # Chart components
```

### Patrón de Componentes

**Server Components (por defecto):**
- Cargan datos del servidor
- No tienen interactividad
- Mejor rendimiento

**Client Components ('use client'):**
- Interactividad con useState, useEffect
- Event handlers
- Acceso a browser APIs

## Flujos de Usuario

### 1. Registrar Nuevo Paciente

```
Usuario → Dashboard → "Nuevo Paciente"
       ↓
   Formulario de registro
       ↓
   POST /api/patients/
       ↓
   Crear Patient en DB
       ↓
   Redirigir a detalle del paciente
```

### 2. Agendar Cita

```
Usuario → Calendario → Seleccionar fecha/hora
       ↓
   Formulario de cita
       ↓
   Seleccionar paciente
       ↓
   POST /api/appointments/
       ↓
   Crear Appointment en DB
       ↓
   Actualizar calendario
       ↓
   (Opcional) Enviar recordatorio
```

### 3. Crear Tratamiento desde Presupuesto

```
Usuario → Presupuestos → Seleccionar presupuesto
       ↓
   "Convertir a tratamiento"
       ↓
   POST /api/budgets/{id}/convert_to_treatment/
       ↓
   Backend:
     - Crear Treatment
     - Actualizar Budget.status = 'converted'
       ↓
   Redirigir a nuevo tratamiento
```

### 4. Registrar Pago

```
Usuario → Tratamiento → "Agregar Pago"
       ↓
   Formulario de pago
       ↓
   POST /api/treatments/{id}/add_payment/
       ↓
   Backend:
     - Crear Payment
     - Actualizar Treatment.amount_paid
     - Recalcular Treatment.status
       ↓
   Actualizar vista de tratamiento
```

## Seguridad

### Niveles de Seguridad Implementados

1. **Nivel de Red:**
   - Traefik como reverse proxy
   - Rate limiting
   - HTTPS en producción
   - CORS configurado

2. **Nivel de Aplicación:**
   - CSRF protection
   - Validación de entrada
   - Sanitización de datos
   - SQL injection prevention (ORM)

3. **Nivel de Datos:**
   - Contraseñas hasheadas (Django)
   - Timestamps en todos los modelos (auditoría)
   - Soft delete (is_active flag)

### Autenticación (Próxima Fase)

```
┌────────────┐
│  Usuario   │
└─────┬──────┘
      │ Login
      ↓
┌─────────────────────────┐
│  Django Authentication  │
│  - Session-based        │
│  - Token-based (DRF)    │
└─────────────────────────┘
      │
      ↓
┌─────────────────────────┐
│  Middleware             │
│  - CSRF                 │
│  - Auth check           │
│  - Permission check     │
└─────────────────────────┘
```

## Escalabilidad

### Optimizaciones Actuales

1. **Base de Datos:**
   - Índices en campos frecuentemente consultados
   - select_related() para reducir queries
   - prefetch_related() para relaciones many-to-many

2. **API:**
   - Paginación por defecto
   - Filtrado a nivel de base de datos
   - Serializers optimizados

3. **Frontend:**
   - Server-side rendering (Next.js)
   - Lazy loading de componentes
   - Static generation cuando sea posible

### Plan de Escalabilidad Futura

```
┌──────────────────────────────────────────┐
│         Load Balancer (Nginx)             │
└───────────────┬──────────────────────────┘
                │
        ┌───────┴────────┐
        │                │
┌───────▼───────┐ ┌─────▼──────────┐
│  Frontend 1   │ │  Frontend 2    │
│  (Next.js)    │ │  (Next.js)     │
└───────────────┘ └────────────────┘
        │                │
        └───────┬────────┘
                │
        ┌───────▼────────┐
        │  API Gateway   │
        └───────┬────────┘
                │
        ┌───────┴────────┐
        │                │
┌───────▼───────┐ ┌─────▼──────────┐
│  Backend 1    │ │  Backend 2     │
│  (Django)     │ │  (Django)      │
└───────────────┘ └────────────────┘
        │                │
        └───────┬────────┘
                │
        ┌───────▼────────┐
        │  PostgreSQL    │
        │  (Primary)     │
        └───────┬────────┘
                │
        ┌───────▼────────┐
        │  PostgreSQL    │
        │  (Replicas)    │
        └────────────────┘
```

### Métricas de Rendimiento Esperadas

- Tiempo de respuesta API: < 200ms (p95)
- Tiempo de carga página: < 2s (LCP)
- Soporte concurrente: 100+ usuarios
- Disponibilidad: 99.9%

---

**Última actualización:** Febrero 2026
