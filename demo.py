"""
HIR MVP — Demo Scenario
Simulates: H-Event → H-Stop → R-0 → Resolution

Run:
  1. Start server: uvicorn app.main:app --reload
  2. Run demo:    python demo.py
"""

import httpx
from datetime import datetime, timedelta, timezone

BASE = "http://localhost:8000/api/v1"


def main():
    client = httpx.Client()

    print("=" * 60)
    print("HIR MVP — Demo: Algorithmic Harm Scenario")
    print("=" * 60)

    # --- Step 1: Register H-Event ---
    print("\n[1] H-DETECT → H-RECORD: Registering harm event...")
    event = client.post(f"{BASE}/events", json={
        "harm_type": "systemic",
        "harm_domain": "ai_recommendation",
        "description": "Recommendation algorithm promoting increasingly extreme content to users under 18. Pattern detected across 50,000+ accounts over 14 days. Correlated with 340% increase in self-harm related searches in affected cohort.",
        "severity": "critical",
        "confidence": "high",
        "affected_scope": "population",
        "affected_count": 50000,
        "horizon": "ongoing",
        "source_type": "automated",
        "source_id": "monitor-fairness-v2",
    }).json()
    h_id = event["h_id"]
    print(f"  ✓ H-Event created: {h_id}")
    print(f"    Status: {event['status']}")
    print(f"    Severity: {event['severity']}")
    print(f"    Affected: {event['affected_count']} users")

    # --- Step 2: Activate H-Stop ---
    print("\n[2] H-THRESHOLD → H-STOP: Halting harm scaling...")
    deadline = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
    stop = client.post(f"{BASE}/stop", json={
        "h_id": h_id,
        "measure": "scope_reduction",
        "scope_target": "recommendation-engine-v3",
        "reason": "Critical harm threshold exceeded. Recommendation amplification disabled for affected cohort pending review.",
        "initiated_by": "system",
        "review_deadline": deadline,
    }).json()
    stop_id = stop["stop_id"]
    print(f"  ✓ H-Stop activated: {stop_id}")
    print(f"    Measure: {stop['measure']}")
    print(f"    Review deadline: {stop['review_deadline']}")

    # --- Step 3: Check event status ---
    print("\n[3] Checking event status after H-Stop...")
    event = client.get(f"{BASE}/events/{h_id}").json()
    print(f"  ✓ Event status: {event['status']}")

    # --- Step 4: Initiate R-0 ---
    print("\n[4] R-0: Initiating immediate recovery...")
    recovery = client.post(f"{BASE}/recovery", json={
        "h_id": h_id,
        "affected_count": 50000,
        "measures": [
            {"type": "access_restoration", "description": "Reset recommendation profiles for affected accounts", "status": "in_progress"},
            {"type": "emergency_aid", "description": "Deploy mental health resources to affected users", "status": "planned"},
            {"type": "public_acknowledgment", "description": "Notify affected users about the issue and actions taken", "status": "planned"},
        ],
        "notes": "Recovery initiated before investigation. Priority: stabilize affected users.",
    }).json()
    recovery_id = recovery["recovery_id"]
    print(f"  ✓ Recovery initiated: {recovery_id}")
    print(f"    Affected: {recovery['affected_count']} users")
    print(f"    Measures: {len(recovery['measures'])} planned")

    # --- Step 5: Update recovery ---
    print("\n[5] Updating recovery progress...")
    recovery = client.patch(f"{BASE}/recovery/{recovery_id}", json={
        "status": "in_progress",
        "notes": "Recommendation profiles reset for 48,000 of 50,000 accounts. Mental health resources deployed.",
    }).json()
    print(f"  ✓ Recovery status: {recovery['status']}")

    # --- Step 6: Release H-Stop ---
    print("\n[6] Releasing H-Stop after review...")
    stop = client.post(f"{BASE}/stop/{stop_id}/release", json={
        "reason": "Root cause identified: reward function weight on engagement-time was 3x higher than safety score. Weights rebalanced. New threshold added to H-Detect.",
        "released_by": "operator-lead",
    }).json()
    print(f"  ✓ H-Stop released: {stop['status']}")
    print(f"    Reason: {stop['release_reason'][:80]}...")

    # --- Step 7: Resolve event ---
    print("\n[7] Resolving H-Event...")
    event = client.patch(f"{BASE}/events/{h_id}/status", json={
        "status": "resolved",
        "reason": "Root cause fixed. Recovery completed. New monitoring thresholds deployed.",
    }).json()
    print(f"  ✓ Event status: {event['status']}")

    # --- Step 8: System stats ---
    print("\n[8] System statistics:")
    stats = client.get(f"{BASE}/observe/stats").json()
    for key, value in stats.items():
        print(f"    {key}: {value}")

    # --- Step 9: Audit trail ---
    print("\n[9] HIR-OBSERVE: Full audit trail:")
    logs = client.get(f"{BASE}/observe/logs?limit=20").json()
    for log in reversed(logs):
        print(f"    [{log['timestamp'][:19]}] {log['module']}.{log['action']} → {log['target_id']}")

    print("\n" + "=" * 60)
    print("Demo complete.")
    print("Principle: Recovery before blame. Halt before discussion.")
    print("=" * 60)

    client.close()


if __name__ == "__main__":
    main()
