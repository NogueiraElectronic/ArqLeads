"""
Load Testing with Locust for ArqLeads System.

Run with:
    locust -f locustfile.py --host=http://localhost:8000

Web UI available at: http://localhost:8089
"""

from locust import HttpUser, task, between, events
import random
import json


class ChatUser(HttpUser):
    """
    Simulates a user interacting with the chat system.
    """
    wait_time = between(2, 5)  # Wait 2-5 seconds between tasks

    def on_start(self):
        """Called when a user starts."""
        self.session_id = f"session-{random.randint(1000, 9999)}"
        self.messages_sent = 0

    @task(5)
    def send_chat_message(self):
        """
        Send a chat message (most common action).
        Weight: 5 (higher probability)
        """
        messages = [
            "Hola, necesito ayuda con un proyecto",
            "Quiero reformar mi piso",
            "Mi presupuesto es de 30000 euros",
            "Lo necesito en 2 meses",
            "Mi nombre es Juan Pérez",
            "Mi email es juan@example.com",
            "Mi teléfono es +34666777888",
            "Estoy en Vigo",
        ]

        payload = {
            "session_id": self.session_id,
            "message": random.choice(messages),
            "language": "es",
            "channel": "web"
        }

        with self.client.post(
            "/api/v1/chat/message",
            json=payload,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                self.messages_sent += 1
                response.success()
            elif response.status_code == 429:
                response.failure("Rate limited")
            else:
                response.failure(f"Unexpected status: {response.status_code}")

    @task(2)
    def get_leads(self):
        """
        Fetch leads list.
        Weight: 2 (moderate probability)
        """
        with self.client.get("/api/v1/leads/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to get leads: {response.status_code}")

    @task(1)
    def get_lead_stats(self):
        """
        Fetch lead statistics.
        Weight: 1 (lower probability)
        """
        with self.client.get("/api/v1/leads/stats", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to get stats: {response.status_code}")

    @task(1)
    def health_check(self):
        """
        Health check endpoint.
        Weight: 1 (lower probability)
        """
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    response.success()
                else:
                    response.failure("Unhealthy status")
            else:
                response.failure(f"Health check failed: {response.status_code}")


class AdminUser(HttpUser):
    """
    Simulates an admin user accessing the dashboard.
    """
    wait_time = between(5, 10)  # Admins check less frequently

    def on_start(self):
        """Login and get admin token."""
        self.login()

    def login(self):
        """Authenticate as admin."""
        payload = {
            "username": "admin",
            "password": "admin123"
        }

        response = self.client.post("/admin/login", json=payload)
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
        else:
            self.token = None

    @task(3)
    def view_dashboard(self):
        """
        View admin dashboard.
        Weight: 3 (higher probability)
        """
        if not self.token:
            return

        headers = {"Authorization": f"Bearer {self.token}"}

        with self.client.get(
            "/admin/dashboard",
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Dashboard failed: {response.status_code}")

    @task(2)
    def check_leads(self):
        """
        Check leads via API.
        Weight: 2 (moderate probability)
        """
        with self.client.get("/api/v1/leads/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to fetch leads: {response.status_code}")

    @task(1)
    def check_metrics(self):
        """
        Check Prometheus metrics.
        Weight: 1 (lower probability)
        """
        with self.client.get("/metrics", catch_response=True) as response:
            if response.status_code == 200:
                if "http_requests_total" in response.text:
                    response.success()
                else:
                    response.failure("Metrics missing")
            else:
                response.failure(f"Metrics failed: {response.status_code}")


class StressTestUser(HttpUser):
    """
    Aggressive stress testing user.
    Use sparingly to test system limits.
    """
    wait_time = between(0.1, 0.5)  # Very fast requests

    @task
    def spam_chat(self):
        """Rapid-fire chat messages."""
        session_id = f"stress-{random.randint(1, 100)}"

        payload = {
            "session_id": session_id,
            "message": f"Stress test message {random.randint(1, 1000)}",
            "language": "es",
            "channel": "web"
        }

        self.client.post("/api/v1/chat/message", json=payload)


# Event listeners for custom metrics
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when test starts."""
    print("🚀 Starting load test...")
    print(f"Target: {environment.host}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when test stops."""
    print("✅ Load test completed!")
    print(f"Total requests: {environment.stats.total.num_requests}")
    print(f"Total failures: {environment.stats.total.num_failures}")
    print(f"Average response time: {environment.stats.total.avg_response_time:.2f}ms")
    print(f"RPS: {environment.stats.total.total_rps:.2f}")
