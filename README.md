# MoWAKi 3.0

Modern Web Application Kit 3.0

A starter project for quickly building modern web applications,
without framework lock-in.

## Stack

- Python API backend
  - Starlette, FastAPI
  - GraphQL API via Strawberry
  - SQLAlchemy database
- React web frontend
  - Typescript support
  - Built using Vite
  - React router
  - Material UI
- PostgreSQL
- Redis

## Features

- React "single page" frontend
- Python backend exposing a RESTful API
- Development environment via Docker compose
- Deployment configuration via Docker compose
- Modern authentication support
- Good (unit, integration) testing support

## Code organization

- ``api`` -- Python backend
  - ``app`` -- Main application package
    - ``api`` -- Web APIs
    - ``core`` -- Business logic
    - ``io`` -- Clients to 3rd parties
    - ``lib`` -- Generic "library" functions; no side-effects
    - ``repo`` -- Access to internal storage (eg. db)
    - ``svc`` -- Services, eg. background workers
- ``web`` -- React frontend
