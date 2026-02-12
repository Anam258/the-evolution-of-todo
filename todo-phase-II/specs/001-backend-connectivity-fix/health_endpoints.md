# Health Check Endpoints Documentation

## Overview
This document describes the health check endpoints that have been implemented as part of the backend connectivity and startup fixes.

## Available Endpoints

### Basic Health Check
- **Endpoint**: `GET /health`
- **Purpose**: Provides a basic health status of the application
- **Response**:
  ```json
  {
    "status": "healthy",
    "service": "todo-api"
  }
  ```
- **Status Codes**:
  - `200`: Service is healthy
  - `500`: Service is unhealthy

### Detailed Health Check
- **Endpoint**: `GET /monitoring/health`
- **Purpose**: Provides detailed health status including system resources and authentication configuration
- **Response**:
  ```json
  {
    "status": "healthy",
    "service": "todo-api",
    "timestamp": "2026-01-23T10:00:00Z",
    "version": "1.0.0",
    "system": {
      "cpu_percent": 15.2,
      "memory_percent": 45.6,
      "disk_usage_percent": 23.1,
      "uptime_seconds": 3600
    },
    "auth_config_valid": true,
    "auth_status": {
      "configured": true,
      "secret_length": 32,
      "validation_passed": true
    }
  }
  ```
- **Status Codes**:
  - `200`: Service is healthy
  - `500`: Service is unhealthy

## Purpose
These endpoints are designed to:
- Allow monitoring systems to check the health of the API
- Provide detailed diagnostic information for troubleshooting
- Verify authentication configuration is valid
- Monitor system resource usage

## Usage
Health check endpoints are automatically available when the backend is running and can be used by:
- Container orchestration platforms (Docker, Kubernetes)
- Monitoring services (Prometheus, Datadog, etc.)
- Load balancers for health checking
- Manual diagnostics by developers and system administrators