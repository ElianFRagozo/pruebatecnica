# User API with FastAPI and MongoDB

Este proyecto es una API RESTful desarrollada con FastAPI y MongoDB que permite gestionar usuarios. La API proporciona endpoints para obtener información general, crear nuevos usuarios y listar todos los usuarios existentes.

## Tecnologías utilizadas

- **Python 3.12+**: Lenguaje de programación principal.
- **FastAPI**: Framework web para construir APIs con Python.
- **MongoDB**: Base de datos NoSQL para almacenar la información de usuarios.
- **Motor**: Driver asíncrono de MongoDB para Python.
- **Pydantic**: Validación de datos y serialización.
- **Uvicorn**: Servidor ASGI para ejecutar la aplicación.

## Requisitos previos

- Python 3.12 o superior.
- Acceso a una base de datos MongoDB (local o en la nube).
- Docker (opcional, para despliegue con contenedores).

## Instalación y configuración

### Opción 1: Instalación local

1. Clonar el repositorio:

```bash
git clone https://github.com/tu-usuario/user-api.git
cd user-api
```

2. Crear un entorno virtual e instalar dependencias:

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Configurar la URL de MongoDB:

```bash
export MONGODB_URI="tu_url_de_mongodb"  # En Windows: set MONGODB_URI=tu_url_de_mongodb
```

4. Ejecutar la aplicación:

```bash
uvicorn main:app --reload
```

### Opción 2: Usando Docker

1. Clonar el repositorio:

```bash
git clone https://github.com/tu-usuario/user-api.git
cd user-api
```

2. Construir la imagen de Docker:

```bash
docker build -t user-api .
```

3. Ejecutar el contenedor:

```bash
docker run -p 8000:8000 -e MONGODB_URI="tu_url_de_mongodb" user-api
```

## Endpoints de la API

### `GET /`

Devuelve un mensaje de bienvenida y la fecha/hora actual.

**Ejemplo de respuesta:**

```json
{
  "mensaje": "Bienvenido a la API de usuarios",
  "fecha_hora": "2023-11-15T12:34:56.789012"
}
```

### `POST /users`

Crea un nuevo usuario en la base de datos.

**Cuerpo de la solicitud:**

```json
{
  "nombre": "Juan",
  "email": "juan@example.com"
}
```

**Ejemplo de respuesta:**

```json
{
  "id": "5f8a7b6c5d4e3f2a1b0c9d8e",
  "nombre": "Juan",
  "email": "juan@example.com"
}
```

### `GET /users`

Obtiene todos los usuarios almacenados en la base de datos.

**Ejemplo de respuesta:**

```json
[
  {
    "id": "5f8a7b6c5d4e3f2a1b0c9d8e",
    "nombre": "Juan",
    "email": "juan@example.com"
  },
  {
    "id": "6a7b8c9d0e1f2a3b4c5d6e7f",
    "nombre": "María",
    "email": "maria@example.com"
  }
]
```

## Variables de entorno

- `MONGODB_URI`: URL de conexión a la base de datos MongoDB.

## Documentación de la API

FastAPI genera automáticamente documentación interactiva para la API:

- **Swagger UI**: Accesible en `/docs` (por ejemplo, [http://localhost:8000/docs](http://localhost:8000/docs)).
- **ReDoc**: Accesible en `/redoc` (por ejemplo, [http://localhost:8000/redoc](http://localhost:8000/redoc)).

## Opciones de despliegue

### Vercel

1. Instala Vercel CLI:

```bash
npm install -g vercel
```

2. Despliega la aplicación:

```bash
vercel
```

## Pruebas

### Pruebas manuales con Postman

- **`GET /` - Obtener mensaje y fecha/hora:**
  - Método: `GET`
  - URL: `http://localhost:8000/`

- **`POST /users` - Crear un nuevo usuario:**
  - Método: `POST`
  - URL: `http://localhost:8000/users`
  - Headers: `Content-Type: application/json`
  - Body:

```json
{
  "nombre": "Juan",
  "email": "juan@example.com"
}
```

- **`GET /users` - Obtener todos los usuarios:**
  - Método: `GET`
  - URL: `http://localhost:8000/users`

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo LICENSE para más detalles.

## Autor

Elian Fragozo Ruiz - elianenriquefragozoruiz@gmail.com
## Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue primero para discutir lo que te gustaría cambiar.

