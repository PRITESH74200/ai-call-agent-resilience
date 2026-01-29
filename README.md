# AI Call Agent - Error Recovery & Resilience System

This repository implements a robust Error Recovery and Resilience System for an AI Call Agent, designed to handle failures in third-party services like ElevenLabs and LLM providers.

## Architecture Decisions

The system is built with a focus on **Separation of Concerns** and **Configuration-Driven Behavior**:

- **Core Resilience**: Custom implementations of Retry (Exponential Backoff) and Circuit Breaker patterns.
- **Service Layer**: An abstract `BaseService` handles the orchestration of retries and circuit breaking, ensuring specialized services only implement their specific logic.
- **Monitoring & Observability**: 
    - **Structured Logging**: Events are logged to a local JSON file for machine readability and to a mock Google Sheets implementation for human visibility.
    - **Alerting System**: Multi-channel alerts (Email, Telegram, Webhook) for critical failures and state changes.
    - **Health Monitoring**: A background manager periodically checks service health and updates status.
- **Exception Hierarchy**: Differentiates between `TransientError` (retryable) and `PermanentError` (non-retryable).

## Error Flow

1. **Detection**: The service wrapper executes a call and catches exceptions.
2. **Classification**: 
    - If `TransientError`, it initiates the **Retry Logic**.
    - If `PermanentError`, it fails immediately and triggers an alert.
3. **Resilience Execution**:
    - **Retry**: Retries the call with an exponential backoff (e.g., 5s, 10s, 20s).
    - **Circuit Breaker**: If failures exceed the `failure_threshold`, the circuit opens, failing-fast subsequent requests to protect the system and the service.
4. **Graceful Degradation**: If a service call ultimately fails, the orchestrator logs the error, sends an alert, and moves to the next contact in the queue without blocking the system.

## Retry & Circuit Breaker Behavior

- **Retry**: Configurable `initial_delay`, `backoff_factor`, and `max_retries`. Includes jitter to prevent synchronized retries.
- **Circuit Breaker States**:
    - **CLOSED**: Normal operation.
    - **OPEN**: Fail-fast mode. Stays open for `recovery_timeout`.
    - **HALF-OPEN**: Allows a single test request after the timeout. Success closes the circuit; failure re-opens it.

## Alerting Logic

Alerts are triggered in the following scenarios:
- **Circuit Breaker Opens/Closes**: Notifies admins of service availability changes.
- **Permanent Failures**: Immediate notification for errors that require manual intervention (e.g., Auth failure).
- **Persistent Transient Failures**: Notification when all retries are exhausted.

## Setup & Simulation

1. **Install Dependencies**: No external libraries required (uses standard Python 3.x).
2. **Run Simulation**:
   ```bash
   python simulate_scenario.py
   ```
   This script simulates ElevenLabs returning 503 errors, demonstrates retries, circuit breaker tripping, health check monitoring, and automatic recovery.

## Example Logs

Structured logs are saved to `app_logs.json`. General execution logs are in `app.log`.
Mock outputs for Google Sheets, Email, Telegram, and Webhooks are printed to the console during execution.
