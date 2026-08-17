from __future__ import annotations

from dataclasses import dataclass

from video_editing_agent.application.ports.environment_doctor import (
    EnvironmentProbe,
    EnvironmentReport,
)


@dataclass(frozen=True, slots=True)
class EnvironmentDoctorResult:
    report: EnvironmentReport
    repair_report: str


class EnvironmentDoctor:
    def __init__(self, probes: tuple[EnvironmentProbe, ...]) -> None:
        self._probes = probes

    def inspect(self) -> EnvironmentDoctorResult:
        checks = tuple(item for probe in self._probes for item in probe.probe())
        report = EnvironmentReport(checks)
        return EnvironmentDoctorResult(report, self._repair_report(report))

    @staticmethod
    def _repair_report(report: EnvironmentReport) -> str:
        lines = [
            "video-editing-agent Environment Doctor",
            (
                "Use official/product-approved sources for repairs and do not disable "
                "security controls."
            ),
        ]
        for item in report.checks:
            lines.append(
                f"- [{item.status.value}] {item.capability.value}/{item.component}: {item.summary}"
            )
            for evidence in item.evidence:
                lines.append(f"  evidence: {evidence}")
            if item.repair_guidance is not None:
                lines.append(f"  repair: {item.repair_guidance}")
        lines.append(
            "After any repair, rerun video-editing-agent doctor to verify actual capability."
        )
        return "\n".join(lines)
