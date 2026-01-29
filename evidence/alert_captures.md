# Alert Notifications Proof
Simulated dispatch to multiple communication channels.

### Email Alert (Mock Output):
```text
[MOCK EMAIL] To: admin@example.com | Subject: Circuit Breaker OPEN for ElevenLabs | Body: The service ElevenLabs has hit the failure threshold and is now disabled.
```

### Telegram Alert (Mock Output):
```text
[MOCK TELEGRAM] Sending: Circuit Breaker OPEN for ElevenLabs - The service ElevenLabs has hit the failure threshold and is now disabled.
```

### Webhook Alert (Mock Output):
```text
[MOCK WEBHOOK] POST /alerts/webhook data: {'title': 'Circuit Breaker OPEN for ElevenLabs', 'message': 'The service ElevenLabs has hit the failure threshold and is now disabled.'}
```
