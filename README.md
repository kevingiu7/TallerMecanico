# Taller Mecánico — módulo de identidad

Módulo de registro, inicio de sesión, recuperación de contraseña y autorización por roles para el sistema del taller.

## Puesta en marcha

1. Cree una base de datos MySQL:
   ```sql
   CREATE DATABASE taller_mecanico CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
2. En `backend`, copie `.env.example` a `.env` y configure la conexión y el secreto JWT.
3. Inicie la API:
   ```powershell
   cd backend
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```
4. En otra terminal, inicie el cliente:
   ```powershell
   cd frontend
   npm install
   npm run dev
   ```

La API queda disponible en `http://localhost:8000` y la interfaz en `http://localhost:5173`.

## Roles

Los usuarios que se registran desde la interfaz reciben siempre el rol `cliente`. Los roles internos se asignan desde un proceso administrativo mediante `PATCH /api/users/{id}/role`, con un token de administrador de taller.

En desarrollo, el enlace de recuperación se devuelve en la respuesta del endpoint y aparece en el registro del servidor. En producción configure un proveedor de correo y no devuelva ese enlace al cliente.

