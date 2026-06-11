# SupportDesk AI

AI-powered support ticket triage and workflow automation platform built with React, TypeScript, FastAPI, PostgreSQL, Docker, and LLM-based agent workflows.

> Status: Ongoing portfolio project, approximately 70–80% complete. Core ticket handling and AI triage functionality are implemented locally. Final phases focus on automation polish, deployment, screenshots, and README/demo completion.

---

## Short Description

SupportDesk AI is a full-stack support ticket platform that helps support teams process incoming requests more efficiently. The system provides ticket intake, ticket management, AI-assisted classification, priority detection, missing-information analysis, routing suggestions, internal summaries, and response draft generation.

The project is built as a CV-ready portfolio project for software engineering, full-stack development, backend development, AI automation, process automation, DevOps/software quality, and internal tools roles.

---

## Project Status

Current status: **Ongoing, around 70–80% complete**

### Completed

- Full-stack project structure with React, TypeScript, FastAPI, PostgreSQL, and Docker
- Ticket intake and ticket management flow
- Admin dashboard for viewing tickets
- Ticket detail view with status updates
- Backend models and database persistence for tickets, messages, agent runs, generated responses, automation events, and attachments
- AI-assisted multi-agent ticket triage workflow
- AI-generated classification, priority, routing suggestion, internal summary, missing-information detection, and response draft
- Agent execution tracking and generated response storage
- Local Docker-based development setup
- pytest-based backend tests for implemented core features
- Structured backend service layers and API routes

### In progress / remaining

- Final workflow automation polish
- Attachment-aware ticket intake and AI context handling
- Email/workflow automation hardening
- UI cleanup and final product copy
- Deployment preparation
- Final README, screenshots, and demo documentation
- Optional CI/CD and frontend test improvements

---

## Key Features

- Support ticket creation through a web form
- Ticket dashboard for support/admin users
- Ticket detail page with status management
- AI-assisted ticket triage
- Multi-agent workflow execution tracking
- Generated support response drafts
- Persistent ticket messages, agent runs, and generated responses
- PostgreSQL-backed data storage
- Docker-based local development setup
- pytest-based backend validation
- Planned automation and deployment-ready improvements in final phases

---

## Tech Stack

### Frontend

- React
- TypeScript
- Vite
- Tailwind CSS
- shadcn/ui
- Axios

### Backend

- FastAPI
- Python
- SQLModel / SQLAlchemy
- Pydantic
- PostgreSQL
- pytest
- Structured service-layer architecture

### AI / Automation

- LLM API integration
- Multi-agent ticket processing workflow
- AI-generated summaries and response drafts
- Workflow automation direction with n8n integration

### Infrastructure / Tooling

- Docker
- Docker Compose
- Git / GitHub
- Local environment-based configuration

---

## Architecture Overview

```text
User / Support Request
        |
        v
React + TypeScript Frontend
        |
        v
FastAPI Backend API
        |
        +-----------------------------+
        |                             |
        v                             v
PostgreSQL Database          AI Processing Service
        |                             |
        v                             v
Tickets, Messages,           Multi-Agent Workflow
Agent Runs, Responses,       Classification, Priority,
Automation Events            Routing, Summary, Draft

The backend is structured around API routes, schemas, models, and service layers. Ticket creation and AI processing are separated into dedicated backend services to keep the codebase easier to extend and test.

---

## AI Workflow Overview

The AI triage workflow processes a ticket through multiple logical steps:

1. **Intake Analysis**
   Extracts the main user request and useful entities from the ticket.

2. **Classification**
   Assigns a category such as technical, billing, account, document, or general.

3. **Priority Detection**
   Estimates the urgency of the ticket based on issue content and impact.

4. **Routing Suggestion**
   Suggests the most relevant support department or team.

5. **Missing Information Detection**
   Identifies details that the requester should provide for faster resolution.

6. **Internal Summary Generation**
   Creates a concise internal summary for support staff.

7. **Response Draft Generation**
   Generates a draft response that a support agent can review before sending.

Each agent step is stored as an agent run, making the AI workflow traceable and easier to inspect during debugging and demos.

---

## Screenshots

Screenshots will be added during the final polish phase.

### Planned screenshots

```text
screenshots/
├── dashboard.png
├── ticket-detail-ai-result.png
├── agent-timeline.png
├── submit-ticket-form.png
└── automation-events.png
```

Example README layout:

```markdown
### Dashboard

![Dashboard](screenshots/dashboard.png)

### AI Ticket Detail

![Ticket Detail](screenshots/ticket-detail-ai-result.png)

### Agent Execution Timeline

![Agent Timeline](screenshots/agent-timeline.png)
```

---

## Local Setup

### Prerequisites

* Python 3.10+
* Node.js 18+
* Docker
* Docker Compose
* PostgreSQL through Docker Compose
* Git

Clone the repository:

```bash
git clone https://github.com/iayushmahajan/supportdesk-ai.git
cd supportdesk-ai
```

---

## Environment Variables

Create backend environment file:

```bash
cp backend/.env.example backend/.env
```

Example backend `.env` structure:

```env
APP_NAME=SupportDesk AI
APP_ENV=development

DATABASE_URL=postgresql+psycopg://supportdesk_user:supportdesk_password@localhost:5433/supportdesk_ai
TEST_DATABASE_URL=postgresql+psycopg://supportdesk_user:supportdesk_password@localhost:5433/supportdesk_ai_test

BACKEND_CORS_ORIGINS=http://localhost:5173
ENABLE_DEMO_SEED=true

LLM_API_KEY=<YOUR_LLM_API_KEY>
LLM_BASE_URL=<LLM_PROVIDER_BASE_URL>
LLM_MODEL=<MODEL_NAME>
LLM_TIMEOUT_SECONDS=30
ENABLE_LLM_FALLBACK=true

ENABLE_AUTO_AI_PROCESSING=true

ENABLE_N8N_AUTOMATION=false
N8N_WEBHOOK_TICKET_CREATED_URL=
N8N_WEBHOOK_AI_COMPLETED_URL=

UPLOAD_DIR=uploads
MAX_ATTACHMENT_SIZE_MB=5
```

Create frontend environment file if needed:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

Do not commit real `.env` files, API keys, email credentials, or webhook secrets.

---

## Database Setup

The local database runs through Docker Compose.

Start PostgreSQL and supporting services:

```bash
docker compose up -d
```

Check running containers:

```bash
docker compose ps
```

The project uses PostgreSQL locally. Database tables are created during backend startup based on the current SQLModel models.

If a full reset is needed during local development:

```bash
docker compose down -v
docker compose up -d
```

Warning: this removes local Docker volumes and deletes local database data.

---

## Running the Backend

```bash
cd backend

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

python -m uvicorn app.main:app --reload
```

Backend runs at:

```text
http://localhost:8000
```

API docs:

```text
http://localhost:8000/docs
```

---

## Running the Frontend

```bash
cd frontend

npm install
npm run dev
```

Frontend runs at:

```text
http://localhost:5173
```

Build check:

```bash
npm run build
```

---

## Running Tests

Backend tests:

```bash
cd backend
source .venv/bin/activate
pytest
```

Frontend build validation:

```bash
cd frontend
npm run build
```

Current testing focus:

* Backend API behavior
* Ticket creation and retrieval
* AI processing workflow behavior
* Duplicate AI processing handling
* Reprocessing behavior
* Automation event handling where implemented
* Email-intake endpoint behavior where implemented

---

## API Overview

Main API areas:

```text
GET    /api/v1/health
GET    /api/v1/health/db

POST   /api/v1/tickets
GET    /api/v1/tickets
GET    /api/v1/tickets/{ticket_id}
PATCH  /api/v1/tickets/{ticket_id}/status

POST   /api/v1/tickets/{ticket_id}/process-ai
POST   /api/v1/tickets/{ticket_id}/reprocess-ai

POST   /api/v1/tickets/email-intake

POST   /api/v1/automation/webhook-test
POST   /api/v1/automation/ticket-created/{ticket_id}
POST   /api/v1/automation/ai-completed/{ticket_id}
POST   /api/v1/automation/callback
```

Exact endpoints may change as the final phases are completed.

---

## Current Roadmap / Remaining Phases

### Phase 7 — Attachment-aware intake and automation polish

Planned focus:

* One-file attachment support for ticket intake
* File validation and local metadata storage
* Attachment display in ticket detail
* Attachment context for AI triage where supported
* Email/workflow automation polish
* Safer automation behavior and clearer admin UI

### Phase 8 — Deployment and final portfolio polish

Planned focus:

* Deployment preparation
* README finalization
* Screenshots and demo walkthrough
* Environment documentation cleanup
* Optional CI/CD workflow
* Final GitHub repository polish

---

## What I Learned

This project helped me practice:

* Designing a full-stack application with a separated frontend and backend
* Building REST APIs with FastAPI
* Modeling relational data with PostgreSQL and SQLModel
* Structuring backend code into routes, schemas, models, and services
* Integrating LLM-based AI workflows into a real application flow
* Tracking AI agent execution for transparency and debugging
* Writing backend tests with pytest
* Managing local services through Docker Compose
* Handling environment variables and development configuration
* Building a recruiter-friendly technical project with realistic product scope

---

## Future Improvements

Potential future improvements:

* Production deployment
* CI/CD pipeline with GitHub Actions
* More frontend tests
* Attachment-aware AI analysis for screenshots and PDFs
* Human-approved email reply sending
* Role-based authentication
* Ticket assignment to support agents
* Search and filtering in the dashboard
* More advanced workflow automation with n8n
* Cloud file storage instead of local uploads
* Better observability and error monitoring

---

## Repository Links / Demo Status

GitHub:

```text
https://github.com/iayushmahajan/supportdesk-ai.git
```

Demo:

```text
Not deployed yet. Deployment is planned for the final project phase.
```

```
```
