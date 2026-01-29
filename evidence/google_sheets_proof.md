# Google Sheets Visibility Proof
Simulated non-technical logging for visibility.

### Log Entry Examples:
```text
[MOCK GOOGLE SHEETS] Logging: 2026-01-29T13:47:05.212336 | LLMProvider | REQUEST_START
[MOCK GOOGLE SHEETS] Logging: 2026-01-29T13:47:40.966701 | ElevenLabs | REQUEST_FAILURE
[MOCK GOOGLE SHEETS] Logging: 2026-01-29T13:55:39.072642 | ElevenLabs | REQUEST_SUCCESS
```

**Observation**: These events are logged concurrently with standard file logging to ensure non-technical stakeholders (e.g., product managers) can see the service health dashboard.
