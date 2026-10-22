# Project component diagram (text alternative)

```mermaid
flowchart TD
    P[Local policy or local LLM adapter] -->|one typed request| C[Controller]
    C -->|validated board operation| B[Board service]
    C -->|validated logical operation| K[Knowledge base]
    B -->|result| C
    K -->|result| C
    C -->|observation, trace, budget| P
    C -->|validated submission| V[Board completion validator]
    V -->|validity| C
```

**Accessible text description:** A local policy or local language-model adapter proposes one typed request to the controller. The controller validates it, routes board operations to the board service and logic operations to the knowledge base, then records the resulting observation and action budget. A submission is checked by the board validator, and only the controller sets terminal status. The next decision uses the recorded observation and trace.
