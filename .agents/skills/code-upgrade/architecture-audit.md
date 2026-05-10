# The Architecture Audit

Map the app, then answer follow-ups. Read-only.

## Discovery Strategy

Start your mapping by looking at `package.json`, `requirements.txt`, `docker-compose.yml`, and root routing or entry files (e.g., `app.py`, `main.go`, `index.js`).

## Output shape

Remember: target audience is non-technical, non-engineers. Keep it high-level, conceptual, and concise.

Avoid paths, filenames, line numbers, and specific libraries (e.g., say "Data Fetching" instead of "Axios"). Only mention major infrastructural choices like React, Python, or Postgres.

```
# What this app is
[One sentence]

# Core Entities
- [Entity 1]: [Brief description of what this data is, e.g., "Users: the people logging in"]
- [Entity 2]: [Brief description]
(List the 3-5 core nouns of the business logic)

# Architecture Diagram
```mermaid
graph TD
    %% Insert a simple, high-level mermaid flowchart showing how the main pieces connect.
```

# Main pieces
- Frontend: [what, including core tech]
- Backend: [what, including core tech]
- Database: [what, including core tech]
- Jobs: [what, including core tech]
- Outside services: [list, e.g., "Stripe (Payments)"]
(only include what exists)

# Main flows
1. [Flow name]: user → step → step → outcome
etc

# Worth grilling
- [Identify single points of failure]
- [Identify missing security/auth checks on core flows]
- [Identify architectural bottlenecks or unusual complexity]
```

End with:

```
## **"Ask me anything.*

- 'where does the X happen?'
- 'why is Y in two places?'"*
```

(generate 3 very very concise suggested follow-ups)

## Rules

- Plain English, for non-engineers. Use simple analogies where helpful.
- Don't propose code changes - point to the right tool (Code Minimizer, Bloat Audit, etc.).
