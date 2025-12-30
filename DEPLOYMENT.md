# Guía de Despliegue: Amparo - Asistente Virtual 🚀

Esta guía detalla los pasos para desplegar el asistente virtual en un servidor remoto con **Ubuntu** utilizando Docker.

## 1. Requisitos Previos en el Servidor
Asegúrate de tener instalados los siguientes componentes en tu servidor Ubuntu:

- **Docker**: `sudo apt update && sudo apt install docker.io -y`
- **Docker Compose**: `sudo apt install docker-compose -y`
- **Git** (opcional para clonar el repo): `sudo apt install git -y`

## 2. Preparación de Archivos
Copia la carpeta del proyecto a tu servidor (puedes usar `scp`, `rsync` o `git clone`). La estructura debe verse así:
```text
/mi-proyecto/
├── backend/
│   ├── Dockerfile
│   └── ...
├── frontend/
│   ├── Dockerfile
│   └── ...
├── docker-compose.yml
└── .env.example
```

## 3. Configuración del Entorno
1. Entra a la carpeta del proyecto:
   ```bash
   cd /ruta/a/tu/proyecto
   ```
2. Crea el archivo de variables de entorno definitivo:
   ```bash
   cp .env.example .env
   ```
3. Edita el archivo `.env` y coloca tu **API Key de Groq**:
   ```bash
   nano .env
   ```
   *Nota: Asegúrate de que `REDIS_URL` sea `redis://redis:6379` para que funcione dentro de la red de Docker.*

## 4. Despliegue con Docker Compose
Ejecuta el siguiente comando para construir las imágenes y levantar los servicios en segundo plano:
```bash
docker-compose up -d --build
```

Esto levantará 3 contenedores:
- **amparo_backend**: Servidor FastAPI (Puerto 8000 interno).
- **amparo_frontend**: Servidor Nginx (Puerto 80 externo).
- **amparo_redis**: Base de datos en memoria para sesiones.

## 5. Verificación
1. **Frontend**: Accede a la IP pública de tu servidor en el navegador: `http://tu-ip-publica`.
2. **Logs**: Si algo no funciona, revisa los logs del backend:
   ```bash
   docker-compose logs -f backend
   ```
3. **Seguridad**: Ejecuta los tests de seguridad dentro del contenedor (opcional):
   ```bash
   docker-compose exec backend python tests/security/test_adversarial.py
   ```

## 6. Recomendaciones de Producción
- **Firewall**: Abre solo el puerto 80 (y 443 si usas SSL) en el servidor.
  ```bash
  sudo ufw allow 80/tcp
  sudo ufw enable
  ```
- **HTTPS**: Te recomiendo usar **Nginx Proxy Manager** o **Certbot** para agregar un certificado SSL gratuito de Let's Encrypt.
- **Backups**: El volumen `redis_data` y la carpeta `backend/data` contienen el historial y la base de conocimiento. Asegúrate de respaldar `backend/data` si realizas cambios manuales.

---
¡Misión cumplida! Amparo ya está lista para ayudar a los ciudadanos desde la nube. 🛡️✨
