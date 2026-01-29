import json
import time
import threading
from src.app import AICallAgent

def run_simulation():
    # Load configuration
    with open("config.json", "r") as f:
        config = json.load(f)

    agent = AICallAgent(config)
    agent.start()

    print("\n=== STARTING SIMULATION SCENARIO ===")
    print("Scenario: ElevenLabs returns 503 Service Unavailable")

    # 1. Trigger Service Failure
    print("\n--- Phase 1: Service goes down ---")
    agent.eleven_labs.is_down = True
    
    # 2. Process call queue
    contacts = ["Alice", "Bob", "Charlie", "David"]
    
    # We will process in a separate thread to see health checks if needed, 
    # but for sequential logic, we can just run it.
    
    print("\n[Simulating First Call to Alice]")
    try:
        agent.process_single_call("Alice")
    except Exception as e:
        print(f"Result: Alice's call failed as expected: {e}")

    print(f"\n[Circuit Breaker State after Alice]: {agent.eleven_labs.circuit_breaker.state.value}")
    
    print("\n[Simulating Second Call to Bob - Should trigger CB OPEN]")
    try:
        agent.process_single_call("Bob")
    except Exception as e:
        print(f"Result: Bob's call failed: {e}")

    print(f"\n[Circuit Breaker State after Bob]: {agent.eleven_labs.circuit_breaker.state.value}")

    print("\n[Simulating Third Call to Charlie - Should Fail Fast due to OPEN CB]")
    try:
        agent.process_single_call("Charlie")
    except Exception as e:
        print(f"Result: Charlie's call skipped (Fail Fast): {e}")

    # 3. Restore Service
    print("\n--- Phase 2: Restoring Service Health ---")
    print("Wait for health check to detect restoration or wait for recovery timeout...")
    agent.eleven_labs.is_down = False
    
    # Wait for recovery timeout (10s in config)
    time.sleep(11)
    
    print(f"\n[Circuit Breaker State before David]: {agent.eleven_labs.circuit_breaker.state.value}")
    print("[Simulating Fourth Call to David - Should recover to HALF_OPEN -> CLOSED]")
    try:
        agent.process_single_call("David")
    except Exception as e:
        print(f"Result: David's call unexpectedly failed: {e}")

    print(f"\n[Circuit Breaker State after David]: {agent.eleven_labs.circuit_breaker.state.value}")

    agent.stop()
    print("\n=== SIMULATION COMPLETED ===")

if __name__ == "__main__":
    run_simulation()
