# Prueba Técnica OMC — API de Gestión de Leads

API REST construida con **FastAPI** y **PostgreSQL** para la gestión de leads de marketing digital. Incluye autenticación JWT, paginación, estadísticas y resumen inteligente de leads mediante IA (OpenAI).

---

## 🛠 Tecnologías utilizadas

| Tecnología | Rol | Por qué la elegí |
|---|---|---|
| **Python + FastAPI** | Framework principal | Es el lenguaje y ecosistema con el que más experiencia tengo. FastAPI permite construir APIs robustas y bien documentadas de forma rápida, con validación automática vía Pydantic. |
| **PostgreSQL** | Base de datos relacional | Es la base de datos que más he utilizado en proyectos profesionales. Ofrece solidez, soporte avanzado de tipos y excelente integración con SQLAlchemy async. |
| **SQLAlchemy 2.0 (async)** | ORM | Permite trabajar con la DB de forma asíncrona, aprovechando al máximo el modelo async de FastAPI. |
| **Alembic** | Migraciones | Gestión de esquemas de base de datos con trazabilidad de versiones. |
| **Pydantic v2** | Validación / Schemas | Validación de datos de entrada/salida con tipado estricto. |
| **PyJWT + Passlib** | Autenticación | Manejo seguro de tokens JWT y hashing de contraseñas con bcrypt. |
| **OpenAI SDK** | IA generativa | Generación de resúmenes inteligentes sobre el conjunto de leads. |
| **Docker + Docker Compose** | Contenerización | Entorno reproducible para desarrollo y despliegue. |
| **Scalar** | Documentación interactiva | Reemplaza Swagger UI con una interfaz más moderna en `/scalar`. |

---

## 📋 Requisitos previos

- [Docker](https://docs.docker.com/get-docker/) y [Docker Compose](https://docs.docker.com/compose/) instalados
- Git

> Si prefieres correr el proyecto sin Docker, necesitas Python 3.11+ y una instancia de PostgreSQL disponible.

---

## 🚀 Instalación y ejecución

### 1. Clonar el repositorio

```bash
git clone https://github.com/lmfreite/Prueba-OMC.git
cd Prueba-OMC
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
```

Edita el archivo `.env` con tus valores. Los campos obligatorios son:

```env
APP_NAME=prueba-omc
APP_ENV=development
CORS_ALLOWED_ORIGINS=http://localhost:3000

POSTGRES_DB_HOST=postgres
POSTGRES_DB_PORT=5432
POSTGRES_DB_NAME=omc_db
POSTGRES_DB_USER=omc_user
POSTGRES_DB_PASSWORD=tu_password
POSTGRES_DB_DRIVER=postgresql+asyncpg
POSTGRES_DB_DEBUG=false

JWT_SECRET_KEY=tu_clave_secreta_aqui
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

DEFAULT_USERNAME=admin
DEFAULT_PASSWORD=admin123

AI_API_KEY=sk-tu-api-key-de-openai
AI_MODEL=gpt-4o-mini
```

### 3. Levantar con Docker Compose

```bash
docker compose up --build
```

La API quedará disponible en: **http://localhost:8007**

| URL | Descripción |
|---|---|
| `http://localhost:8007/` | Root — info básica de la API |
| `http://localhost:8007/health` | Health check |
| `http://localhost:8007/scalar` | Documentación interactiva |

### 4. Ejecución sin Docker (entorno local)

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Asegúrate de tener .env configurado con POSTGRES_DB_HOST=localhost
uvicorn app.main:app --reload --port 8000
```

---

## 🌱 Seed de datos

> **El seed se ejecuta automáticamente al arrancar el proyecto.** No es necesario correr ningún comando adicional.

Al iniciar, `init_db` realiza las siguientes acciones en orden:

1. Crea la base de datos si no existe.
2. Aplica las migraciones de Alembic.
3. Inserta el **usuario administrador por defecto** (si no existe) usando `DEFAULT_USERNAME` y `DEFAULT_PASSWORD` del `.env`.
4. Inserta **10 leads de ejemplo** (si la tabla está vacía), cubriendo todos los tipos de fuente: `instagram`, `facebook`, `landing_page`, `referred` y `other`.

Si ya existen datos en la tabla, el seed no modifica ni duplica nada — es completamente idempotente.

---

## 📡 Endpoints

Base URL: `http://localhost:8007/api/v1`

### 🔓 Autenticación

Los endpoints de **leads son privados** y requieren estar autenticado. El sistema de autenticación funciona mediante **cookie HttpOnly**: al hacer login, el servidor establece automáticamente la cookie con el JWT. Todas las peticiones posteriores a endpoints protegidos deben enviar esa cookie.

En `curl` se maneja con los flags `-c` (guardar cookie) y `-b` (enviar cookie):

```
-c cookies.txt   ← guarda la cookie al hacer login
-b cookies.txt   ← envía la cookie en peticiones autenticadas
```

#### Login

```bash
curl -c cookies.txt -X POST http://localhost:8007/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

> ✅ Tras este paso, `cookies.txt` contiene el JWT. Úsalo en todas las llamadas a `/leads`.

#### Registro de usuario

```bash
curl -X POST http://localhost:8007/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "nuevo_usuario", "password": "mipassword123"}'
```

#### Logout

```bash
curl -b cookies.txt -X POST http://localhost:8007/api/v1/auth/logout
```

---

### 🔒 Leads (requieren autenticación)

> Todos los endpoints de leads requieren haber hecho login previamente. Incluye `-b cookies.txt` en cada petición.

#### Crear un lead

```bash
curl -b cookies.txt -X POST http://localhost:8007/api/v1/leads \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Pedro Suárez",
    "email": "pedro.suarez@example.com",
    "phone": "+573001112233",
    "source": "instagram",
    "product_interest": "Camisetas sublimadas",
    "budget": 180000
  }'
```

#### Listar leads (con paginación y filtros)

```bash
# Página 1, 10 por página
curl -b cookies.txt "http://localhost:8007/api/v1/leads?Page=1&Page_size=10"

# Filtrar por fuente
curl -b cookies.txt "http://localhost:8007/api/v1/leads?source=instagram"

# Filtrar por nombre
curl -b cookies.txt "http://localhost:8007/api/v1/leads?name=Carlos"

# Filtrar por email
curl -b cookies.txt "http://localhost:8007/api/v1/leads?email=carlos.ramirez@example.com"
```

#### Obtener un lead por ID

```bash
curl -b cookies.txt http://localhost:8007/api/v1/leads/1
```

#### Actualizar un lead

```bash
curl -b cookies.txt -X PATCH http://localhost:8007/api/v1/leads/1 \
  -H "Content-Type: application/json" \
  -d '{"budget": 250000, "product_interest": "Gorras bordadas"}'
```

#### Eliminar un lead

```bash
curl -b cookies.txt -X DELETE http://localhost:8007/api/v1/leads/1
```

#### Estadísticas de leads

```bash
curl -b cookies.txt http://localhost:8007/api/v1/leads/stats
```

#### Resumen IA (requiere `AI_API_KEY` válida)

```bash
curl -b cookies.txt -X POST http://localhost:8007/api/v1/ai/summary \
  -H "Content-Type: application/json" \
  -d '{"source": "instagram"}'
```

---

## 📂 Estructura del proyecto

```
Prueba-OMC/
├── app/
│   ├── api/v1/routes/      # Controladores (auth, leads)
│   ├── core/               # Settings, seguridad, response handler
│   ├── db/                 # Sesión, init_db, seed
│   ├── models/             # Modelos SQLAlchemy
│   ├── repositories/       # Capa de acceso a datos
│   ├── schemas/            # DTOs Pydantic
│   ├── services/           # Lógica de negocio + cliente OpenAI
│   ├── middleware/         # SessionExpirationMiddleware
│   └── main.py             # Entrypoint FastAPI
├── alembic/                # Migraciones
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

---

## 📝 Notas adicionales

- La documentación interactiva completa está disponible en **`/scalar`** una vez levantado el proyecto.
- El puerto expuesto por Docker es **8007** (mapeado al 8000 interno del contenedor).
- PostgreSQL queda expuesto en el puerto **5437** para conexiones locales desde un cliente como DBeaver o TablePlus.
- Si una petición a `/leads` devuelve `401 Unauthorized`, asegúrate de haber hecho login primero y de estar enviando la cookie con `-b cookies.txt`.
