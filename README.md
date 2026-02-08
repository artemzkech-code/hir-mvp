# HIR MVP — Harm–Integrity–Recovery

Minimum viable implementation of the HIR protocol.

**Detect → Halt → Recover.** Before blame. Before investigation. Before sanctions.

---

## Quickstart

### Option 1: Local

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Server starts at http://localhost:8000  
API docs at http://localhost:8000/docs

### Option 2: Docker

```bash
docker build -t hir-mvp .
docker run -p 8000:8000 hir-mvp
```

---

## Demo

Start the server, then:

```bash
python demo.py
```

This runs a full scenario: harm detection → H-Stop → R-0 recovery → resolution.

---

## API

| Module | Endpoint | Method | Description |
|---|---|---|---|
| **H-Event** | `/api/v1/events` | POST | Register harm event |
| | `/api/v1/events/{h_id}` | GET | Get event by ID |
| | `/api/v1/events/{h_id}/status` | PATCH | Update status |
| | `/api/v1/events` | GET | List events (filterable) |
| **H-Stop** | `/api/v1/stop` | POST | Activate halt |
| | `/api/v1/stop/{stop_id}/release` | POST | Release halt |
| | `/api/v1/stop` | GET | List stops |
| **R-0** | `/api/v1/recovery` | POST | Initiate recovery |
| | `/api/v1/recovery/{recovery_id}` | PATCH | Update recovery |
| | `/api/v1/recovery` | GET | List recoveries |
| **Observe** | `/api/v1/observe/logs` | GET | Audit trail |
| | `/api/v1/observe/stats` | GET | System statistics |

Full interactive docs: http://localhost:8000/docs

---

## What This Is

HIR is an open protocol for harm accountability. This MVP implements the core loop:

1. **H-Event** — something harmful is detected and recorded (not accused — recorded)
2. **H-Stop** — if harm is scaling, the process is paused (temporary, reversible, reviewable)
3. **R-0** — affected people get help immediately (before investigation, before blame)
4. **HIR-Observe** — every action is logged, traceable, auditable

---

## What This Is Not

- Not a moral arbiter
- Not a censorship tool
- Not a punishment system
- Not permanent — every decision is reversible

---

## Specification

Full protocol documentation: [github.com/artemzkech-code/HIR](https://github.com/artemzkech-code/HIR)  
DOI: [10.5281/zenodo.18528379](https://doi.org/10.5281/zenodo.18528379)

---

## License

CC BY-SA 4.0

**Author:** Artem Bykov (Kech)  
artemzkech@gmail.com  
ORCID: 0009-0006-4660-7635
