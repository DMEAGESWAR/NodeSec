
 # NodeSec : Attack Surface Intelligence for Non-Experts



NodeSec is a modern attack surface intelligence platform designed to help organizations understand what is publicly exposed on the internet — without requiring a dedicated cybersecurity team.

Most colleges, SMEs, startups, and local organizations struggle to interpret complex security tools and raw vulnerability reports. NodeSec bridges that gap by transforming scattered OSINT data into clear attack graphs, understandable risk insights, and actionable remediation guidance.

Instead of overwhelming users with technical logs, NodeSec focuses on answering three simple questions:

* What is exposed?
* How serious is the risk?
* What should be fixed first?

> Built with FastAPI, React, PostgreSQL, and Docker.



## Why NodeSec?

Traditional security tools are often designed for experienced security engineers and produce outputs that are difficult for non-experts to interpret.

NodeSec simplifies cybersecurity visibility by combining:

* Passive OSINT-based intelligence gathering
* Visual attack surface mapping
* Deterministic attack chain detection
* Severity-based risk scoring
* Plain-language explanations
* Actionable remediation guidance

The goal is to make cybersecurity visibility more accessible for resource-constrained organizations and non-specialist administrators.



## Core Features

* Passive subdomain discovery using public intelligence sources
* DNS, SSL, and exposure analysis
* Visual attack graph generation
* Attack chain detection engine
* Severity-based risk scoring
* Human-readable explanations and fix recommendations
* Interactive dashboard experience
* Dockerized local development setup



## System Architecture


<img width="1793" height="988" alt="Screenshot 2026-05-18 214231" src="https://github.com/user-attachments/assets/41130edf-7bbe-4b88-bd33-56cb9798bfbd" />


## Tech Stack

| Layer            | Technology                                           |
| ---------------- | ---------------------------------------------------- |
| Frontend         | React, Vite, Tailwind CSS, React Flow, Framer Motion |
| Backend          | FastAPI, SQLAlchemy, Pydantic                        |
| Database         | PostgreSQL                                           |
| Authentication   | JWT + bcrypt                                         |
| OSINT Sources    | crt.sh, CertSpotter, OTX, DNS, SSL                   |
| Containerization | Docker + Docker Compose                              |


## Scalability & Future Vision

NodeSec is designed with modular scalability in mind.

The architecture separates:

* OSINT collection
* attack analysis
* scoring
* reporting
* frontend visualization

This enables future scaling into:

* distributed scan workers
* real-time monitoring
* enterprise multi-tenant deployments
* cloud-native orchestration
* AI-assisted remediation guidance
* SIEM integrations
* automated alerting pipelines

The backend is containerized using Docker and can be horizontally scaled with orchestration platforms such as Kubernetes in production environments.


## Workflow
<img width="1774" height="887" alt="12c197ae-8dd0-48c8-9484-5b3eff2e7554" src="https://github.com/user-attachments/assets/04135b6c-f920-4c59-aa1e-bc3b478363f6" />





## Project Structure

```text
NodeSec/
├── nodesec-backend/
│   ├── routers/
│   ├── services/
│   ├── osint/
│   ├── rule_engine/
│   ├── scoring/
│   ├── workers/
│   ├── models/
│   └── schemas/
│
├── nodesec-frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── api/
│   │   ├── hooks/
│   │   └── store/
│
├── docker-compose.yml
└── README.md
```



## Example Workflow

1. User enters a domain
2. NodeSec collects public OSINT data
3. Backend analyzes attack relationships
4. Risk engine scores vulnerabilities
5. Dashboard visualizes findings
6. User receives explanations and remediation steps



## Screenshots

<img width="1920" height="1200" alt="Screenshot (317)" src="https://github.com/user-attachments/assets/4c82231a-cb5a-4b73-80ab-26a781f84209" />

<img width="1920" height="1200" alt="image" src="https://github.com/user-attachments/assets/889996fe-6625-4ab8-8f42-330e8265f9f9" />



## License

MIT License




  ## 1. K.BarathRaj - Backend developer
  ## 2. D.Meageswar - Frontend developer
  ## 3. R.Santhosh - Search engineer 
