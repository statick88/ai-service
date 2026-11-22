#!/usr/bin/env python3
"""Validate the public Docker Compose development contract."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP_SOURCE = (ROOT / "app").resolve()


def compose_config(*, project_name: str, port: str | None = None) -> dict[str, object]:
    environment = os.environ.copy()
    environment["COMPOSE_DISABLE_ENV_FILE"] = "1"
    if port is None:
        environment.pop("AI_SERVICE_PORT", None)
    else:
        environment["AI_SERVICE_PORT"] = port

    result = subprocess.run(
        [
            "docker",
            "compose",
            "--profile",
            "ci",
            "-p",
            project_name,
            "-f",
            "compose.yaml",
            "config",
            "--format",
            "json",
        ],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(
            "docker compose config failed:\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return json.loads(result.stdout)


class ComposeContractTests(unittest.TestCase):
    def config(self, *, project_name: str = "ai-compose-contract", port: str | None = None) -> dict[str, object]:
        return compose_config(project_name=project_name, port=port)

    def service(self, config: dict[str, object], name: str) -> dict[str, object]:
        services = config["services"]
        self.assertIsInstance(services, dict)
        service = services[name]
        self.assertIsInstance(service, dict)
        return service

    def test_development_service_mounts_only_read_only_app_source(self) -> None:
        config = self.config()
        service = self.service(config, "ai-service")

        volumes = service.get("volumes")
        self.assertEqual(
            volumes,
            [
                {
                    "type": "bind",
                    "source": str(APP_SOURCE),
                    "target": "/app/app",
                    "read_only": True,
                }
            ],
        )
        self.assertEqual(service["build"]["target"], "development")
        self.assertEqual(service["ports"], [{"mode": "ingress", "host_ip": "127.0.0.1", "target": 8000, "published": "8000", "protocol": "tcp"}])

    def test_check_container_has_no_host_mounts(self) -> None:
        config = self.config()
        service = self.service(config, "ai-check")

        self.assertNotIn("volumes", service)
        self.assertEqual(service["build"]["target"], "check")

    def test_port_override_remains_loopback_only(self) -> None:
        config = self.config(port="18081")
        service = self.service(config, "ai-service")

        self.assertEqual(service["ports"], [{"mode": "ingress", "host_ip": "127.0.0.1", "target": 8000, "published": "18081", "protocol": "tcp"}])

    def test_project_names_are_independent(self) -> None:
        first = self.config(project_name="ai-worktree-one")
        second = self.config(project_name="ai-worktree-two")

        self.assertEqual(first["name"], "ai-worktree-one")
        self.assertEqual(second["name"], "ai-worktree-two")


if __name__ == "__main__":
    unittest.main()
