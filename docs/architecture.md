# Human Advisor AI Architecture

```mermaid
flowchart TB
    human[Human user]
    service[Installed background service<br/>starts at user login<br/>task or Startup fallback]
    window[One visible Brosir AI window<br/>opens at user login]
    client[Browser or desktop voice client]
    consent[Explicit OS and app microphone consent]
    voice[Voice session boundary<br/>start, stop, visible status]
    wake[Brosir wake word<br/>starts continuous consented session]
    conversation[Continuous conversation<br/>automatic answers]
    memory[Encrypted memory store<br/>incidents, feelings as user context, facts, feedback]
    adviser[Local rule and memory adviser<br/>optional AI provider]
    discussion[General discussion module<br/>answer plus follow-up questions]
    proposal[Action proposal<br/>code, API, command]
    approval[Human approval queue]
    executor[Optional separately reviewed executor]
    api[External API or code workspace]

    service --> window --> human
    human --> client --> consent --> voice --> wake
    wake --> conversation --> memory --> adviser
    conversation --> discussion --> human
    adviser --> proposal --> approval --> executor --> api
    adviser -. ordinary answer .-> conversation
    approval -. reject or revise .-> human

    classDef human fill:#e8f1ff,stroke:#2457a6,color:#102a56
    classDef control fill:#fff2df,stroke:#a65b00,color:#5b3100
    classDef data fill:#eaf8ef,stroke:#237a44,color:#123d23
    class human,client,consent,approval human
    class voice,adviser,proposal,executor control
    class memory,api data
```

The API service can run continuously after installation and one visible Brosir AI window opens at user login. The local rule-and-memory adviser answers without an API key; an optional provider can improve wording but is not required. The voice path is opt-in and reversible. `Brosir` is recognized once after explicit consent starts a listening session; subsequent client-transcribed phrases continue in that session until Stop or disconnect. The service does not access a microphone by itself, does not claim to experience feelings, and does not execute critical proposals without a human decision.