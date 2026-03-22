# ERP Fenix Soft

Sistema ERP (Enterprise Resource Planning) moderno construido con Django 6+, Unfold Admin y Tailwind CSS 4.

## 🚀 Tecnologías

| Backend | Frontend | Base de Datos |
|---------|----------|---------------|
| Python 3.12+ | Tailwind CSS 4 | SQLite (dev) |
| Django 6.0+ | Unfold Admin | PostgreSQL (prod) |
| Django REST Framework | HTMX | |
| Django Allauth | | |

## 📁 Estructura del Proyecto

```
ERP Fenix Soft/
├── .env.local              # Variables de entorno (desarrollo) - NO commitear
├── .env.production         # Variables de entorno (producción) - NO commitear
├── .env.example            # Plantilla de ejemplo - SÍ commitear
├── manage.py
├── pyproject.toml
├── package.json
├── core/
│   ├── settings/
│   │   ├── base.py         # Configuración base
│   │   ├── local.py        # Desarrollo local
│   │   └── production.py   # Producción
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── products/           # Gestión de productos
│   ├── users/              # Gestión de usuarios
│   ├── purchases/          # Compras
│   └── sales/              # Ventas
├── templates/
├── statics/
└── logs/                   # Logs de producción
```

## ⚙️ Configuración Inicial

### 1. Instalar dependencias

```bash
# Python
uv sync

# Node.js
npm install
```

### 2. Configurar variables de entorno

```bash
# Copiar plantilla
cp .env.example .env.local
```

Editar `.env.local` con tus credenciales de desarrollo.

### 3. Migrar base de datos

```bash
# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser
```

### 4. Compilar CSS (Tailwind)

```bash
# Desarrollo (watch mode)
npm run watch

# Producción (minificado)
npm run build
```

### 5. Ejecutar servidor de desarrollo

```bash
python manage.py runserver
```

Accede a: http://localhost:8000/admin

## 🔐 Variables de Entorno

### Desarrollo (`.env.local`)
### Producción (`.env.production`)


## 🛡️ Seguridad

- ✅ Variables de entorno con `django-environ`
- ✅ `.env` excluido de Git
- ✅ HTTPS obligatorio en producción
- ✅ Cookies seguras (HTTPOnly, Secure)
- ✅ HSTS habilitado
- ✅ Logging de errores en producción

## 📦 Módulos Principales

| Módulo | Estado | Descripción |
|--------|--------|-------------|
| Users | ✅ | Gestión de usuarios con email como username |
| Products | ✅ | Catálogo de productos con categorías |
| Purchases | 🚧 | Módulo de compras (pendiente) |
| Sales | 🚧 | Módulo de ventas (pendiente) |

## 🎨 Admin Panel

El admin panel utiliza **Unfold** con personalización premium:

- Dashboard moderno con Tailwind CSS
- Avatares con gradiente personalizado
- Dark mode soportado
- Sidebar de navegación colapsable
- Auditoría de cambios con `django-simple-history`

## 📝 Comandos Útiles

```bash
# Ejecutar tests
python manage.py test

# Recopilar estáticos (producción)
python manage.py collectstatic

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Shell de Django
python manage.py shell

# Check de configuración
python manage.py check
```

## 📄 Licencia

Propietario - ERP Fenix Soft © 2026
