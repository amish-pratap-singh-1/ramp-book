# Ramp Book - Aircraft Management & Reservation System

Ramp Book is a premium, full-stack web application designed for Flying Clubs to manage their fleet, handle member reservations, and track aircraft maintenance. It provides a seamless experience for club members, flight instructors, and administrators.

## 🚀 Key Features

### 📅 Advanced Reservation System
- **Interactive Calendar**: Resource-based view for all aircraft in the fleet using `react-big-calendar`.
- **Conflict Prevention**: Robust backend validation prevents double-booking of aircraft, members, or instructors.
- **Maintenance Awareness**: Automatically blocks reservations during scheduled aircraft maintenance windows.
- **Flight Logging**: Complete flight records by entering Hobbs meter readings upon return.

### 🏢 Club Management
- **Organization Control**: Manage club settings, home bases, and timezones.
- **Member Management**: Track member certificates and contact information.
- **Instructor Scheduling**: Manage instructor availability and ratings (CFI, CFII, MEI).

### ✅ MVP Requirements Mapping
To ensure the assignment criteria are met, the following core features are implemented:

| Requirement | Implementation Detail | Location |
| :--- | :--- | :--- |
| **RBAC** | Member/Instructor/Admin roles with role-based dashboard views. | `apps/server/src/decorators/auth.py` |
| **Fleet Monitoring** | Real-time status, Hobbs hours tracking, and model specifications. | `apps/client/src/pages/fleet.tsx` |
| **Double-Booking Prevention** | Server-side validation for Aircraft, Instructors, and Members. | `apps/server/src/core/reservationsvc.py` |
| **Maintenance Windows** | Specific time blocks that disable aircraft booking. | `apps/server/src/repositories/aircraft.py` |
| **Flight Completion** | Logging Hobbs end-time and updating aircraft total hours. | `apps/server/src/api/reservations.py` |

---

## 🛠 Tech Stack

### Frontend
- **Framework**: [Next.js](https://nextjs.org/) (React 19)
- **Styling**: [Tailwind CSS](https://tailwindcss.com/)
- **State Management**: [TanStack Query](https://tanstack.com/query/latest)
- **Components**: Sonner (Toasts), React Big Calendar, React Hook Form.

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **Database**: [PostgreSQL](https://www.postgresql.org/) with Alembic/SQLAlchemy
- **Dependency Management**: [Poetry](https://python-poetry.org/)

---

## 🚦 Getting Started

### Prerequisites
- Docker & Docker Compose
- Node.js (with `pnpm`)
- Python 3.10+ (with `poetry`)

### Quick Start
#### create .env from sample.env 
```bash
cp sample.env .env
```
```bash
cp apps/client/sample.env apps/client/.env.local
```
#### Run project
```bash
make run-project
```

---

## 📂 Project Structure

```text
.
├── apps/
│   ├── client/          # Next.js frontend
│   └── server/          # FastAPI backend
├── docs/
│   └── mvp/             # MVP specs & seed data
├── Makefile             # Automation scripts
└── docker-compose.yaml  # Container orchestration
```

---

## 📜 API Documentation
Interactive Swagger UI available at: `http://localhost:8000/docs`
