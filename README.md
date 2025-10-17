# Futuuri MVP - Medical Image Analysis Platform

A microservices-based medical image analysis platform using computer vision for thyroid imaging.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │  Vision Service │    │ Storage Service │
│   (Next.js)     │    │   (FastAPI)     │    │   (ML Model)    │    │   (Database)    │
│                 │    │                 │    │                 │    │                 │
│   Port: 3000    │────│   Port: 8000    │────│   Port: 8001    │    │   Port: 8002    │
│                 │    │                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Services

- **Frontend** (Port 3000): Next.js web interface for image upload and results
- **Backend** (Port 8000): FastAPI orchestration layer
- **Vision Service** (Port 8001): ML model for thyroid image segmentation
- **Storage Service** (Port 8002): File storage and SQLite database

## Quick Setup

1. **Prerequisites**: Docker & Docker Compose

2. **Start all services**:
   ```bash
   docker-compose up --build
   ```

3. **Access the application**:
   - Web UI: http://localhost:3000
   - API: http://localhost:8000
   - Vision API: http://localhost:8001  
   - Storage API: http://localhost:8002

4. **Development mode** (with live reload):
   ```bash
   docker-compose up --build
   ```

## Usage

1. Open http://localhost:3000
2. Upload a thyroid ultrasound image
3. View segmentation results and analysis