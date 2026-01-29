# AI Call Agent - Error Recovery & Resilience System 📞

## 🔹 Project Overview
This system is a robust middleware designed for an AI Call Agent that manages integrations with critical third-party services like ElevenLabs (TTS) and LLM providers. In a production environment, these services often experience transient network issues or rate limits. This system ensures that the agent can **detect failures**, **recover intelligently** via multi-stage retries, and **prevent cascading outages** using the Circuit Breaker pattern, all while keeping stakeholders informed via automated alerts and transparent logging.

## 🔹 Architecture Diagram
```ascii
[ Call Queue ] 
      |
      v
[ AICallAgent (Orchestrator) ] <---- [ HealthCheckManager (Background) ]
      |
      +------> [ BaseService Wrapper (Resilience Layer) ]
                   |
                   +-- [ Retry Handler (Exponential Backoff) ]
                   +-- [ Circuit Breaker (State Machine) ]
      |            |
      |            +--> [ External Service (ElevenLabs/LLM) ]
      |
      +------> [ Monitoring & Alerting ]
                   |
                   +-- [ Structured JSON Logs ]
                   +-- [ Google Sheets Mock ]
                   +-- [ Alerts: Email/Telegram/Webhook ]
```

## 🔹 Error Categorization
The system employs a custom exception hierarchy to treat different failure modes appropriately:
- **Transient Errors** (`TransientError`): Temporary issues like `ServiceUnavailable (503)`, `Timeouts`, or `NetworkFailures`. These trigger the retry mechanism.
- **Permanent Errors** (`PermanentError`): Final failures like `AuthenticationError (401)`, `InvalidPayload (400)`, or `QuotaExceeded`. These skip retries and trigger immediate alerts.

## 🔹 Retry Logic
Implemented from scratch to avoid external dependencies:
- **Initial Delay**: 5 seconds (configurable).
- **Exponential Backoff**: Multiplies delay by 2x after each failure.
- **Max Retries**: 3 attempts.
- **Selective**: Only applied to `TransientError` types.
- **Jitter**: Added to prevent "thundering herd" issues.

## 🔹 Circuit Breaker
Protects the system from repeated calls to a failing dependency:
- **Failure Threshold**: 3 consecutive failures trips the circuit.
- **States**:
    - `CLOSED`: Normal operation, calls pass through.
    - `OPEN`: Fail-fast mode. Calls are rejected immediately to allow the service to recover.
    - `HALF_OPEN`: After a recovery timeout, allows a single probe request to check service health.
- **Behavior**: Once `OPEN`, it stops all outgoing requests to that service for a configurable period.

## 🔹 Required Scenario: ElevenLabs 503 Flow
When ElevenLabs returns a **503 Service Unavailable**:
1. **Detection**: System catches the error and identifies it as a `TransientError`.
2. **Backoff**: Wait 5s, then retry. If failed, wait 10s, then retry. If failed, wait 20s.
3. **Exhaustion**: After 3 retries fail, the call to ElevenLabs is marked as failed.
4. **Trigger**: An alert is dispatched to the Admin (Email/Telegram/Webhook).
5. **Isolation**: The **Circuit Breaker** for ElevenLabs transitions to `OPEN`.
6. **Degradation**: The current call is skipped, and the agent moves to the next contact in the queue.
7. **Recovery**: The background `HealthCheckManager` continues polling. Once healthy, the circuit resets to `CLOSED`, and call processing for ElevenLabs resumes.

## 🔹 Logging & Observability
Provides full transparency into system internals:
- **File Logs**: `app_logs.json` (Structured JSON) and `app.log` (Readable).
- **Google Sheets Logs**: Mocked to show how non-technical users can monitor performance.
- **Fields**: Timestamp, Service Name, Event Category, Retry Count, and Circuit State.

## 🔹 Alerts
Automated notifications are sent via three channels:
- **Email**: For permanent failures and circuit state changes.
- **Telegram**: Real-time push notifications for critical outages.
- **Webhook**: Generic HTTP POST to integrate with other tools.
- **Triggers**: When a circuit opens, stays down, or when a call permanently fails.

## 🔹 Graceful Degradation
The system is designed to "Keep Walking":
- **Skip & Move**: If a dependency is down, it identifies the failure, alerts, and immediately tries the next contact in the queue.
- **Non-Blocking**: The health check runs in a separate thread, ensuring checking for recovery doesn't slow down the main processing logic.

## 📸 Evidence
See the `/evidence` folder for technical proof of the system's performance, including:
- [Logs Screenshot](evidence/logs_screenshot.md): Execution trail showing retries and backoff.
- [Circuit Breaker State](evidence/circuit_breaker_state.md): Proof of the "Fail-Fast" behavior when the circuit is `OPEN`.
- [Alert Captures](evidence/alert_captures.md): Simulated email/telegram/webhook notifications.
- [Google Sheets Proof](evidence/google_sheets_proof.md): Proof of non-technical visibility.

## 🛠️ Setup & Running
1. **Local Simulation**:
   ```bash
   $env:PYTHONPATH = ".;src"
   python simulate_scenario.py
   ```
2. **Dashboard (Optional)**:
   ```bash
   pip install -r requirements.txt
   streamlit run streamlit_app.py
   ```
