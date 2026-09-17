# Human Advisor AI Architecture

```mermaid
flowchart TB
    human[Human user]
    service[Installed background service<br/>starts at user login]
    client[Browser or desktop voice client]
    consent[Explicit OS and app microphone consent]
    voice[Voice session boundary<br/>start, stop, visible status]
    wake[Brosir wake word<br/>local phrase detection]
    memory[Encrypted memory store<br/>incidents, feelings as user context, facts, feedback]
    adviser[Adviser and learning module]
    proposal[Action proposal<br/>code, API, command]
    approval[Human approval queue]
    executor[Optional separately reviewed executor]
    api[External API or code workspace]

    human --> service --> client --> consent --> voice --> wake
    wake --> memory --> adviser
    adviser --> proposal --> approval --> executor --> api
    approval -. reject or revise .-> human

    classDef human fill:#e8f1ff,stroke:#2457a6,color:#102a56
    classDef control fill:#fff2df,stroke:#a65b00,color:#5b3100
    classDef data fill:#eaf8ef,stroke:#237a44,color:#123d23
    class human,client,consent,approval human
    class voice,adviser,proposal,executor control
    class memory,api data
```

The API service can run continuously after installation and starts at user login, but the voice path is opt-in and reversible. `Brosir` is recognized only after explicit consent starts a listening session. The service does not access a microphone by itself, does not claim to experience feelings, and does not execute proposals without a human decision.