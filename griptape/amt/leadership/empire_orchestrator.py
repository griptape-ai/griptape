"""
Empire Orchestrator Module

Coordinates cross-company operations across AMT's 12-company empire.
Manages resource allocation, strategic alignment, and performance monitoring
across all portfolio companies.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Sequence

logger = logging.getLogger(__name__)


class CompanyStatus(Enum):
    """Operational status of portfolio companies."""

    ACTIVE = "active"
    SCALING = "scaling"
    OPTIMIZATION = "optimization"
    MAINTENANCE = "maintenance"
    STRATEGIC_REVIEW = "strategic_review"


class ResourceType(Enum):
    """Types of resources that can be allocated."""

    CAPITAL = "capital"
    TALENT = "talent"
    TECHNOLOGY = "technology"
    INFRASTRUCTURE = "infrastructure"
    STRATEGIC_SUPPORT = "strategic_support"


@dataclass
class Company:
    """Represents a portfolio company in the AMT empire."""

    company_id: str
    name: str
    status: CompanyStatus
    primary_focus: str
    leadership_contact: str | None = None
    allocated_resources: dict[ResourceType, float] | None = None
    performance_metrics: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        """Initialize default values."""
        if self.allocated_resources is None:
            self.allocated_resources = {}
        if self.performance_metrics is None:
            self.performance_metrics = {}


@dataclass
class ResourceAllocation:
    """Represents a resource allocation decision."""

    allocation_id: str
    resource_type: ResourceType
    amount: float
    target_companies: list[str]
    allocated_by: str
    justification: str
    timestamp: datetime
    duration_months: int | None = None


@dataclass
class PerformanceReport:
    """Performance monitoring report for companies."""

    report_id: str
    company_ids: list[str]
    reporting_period: str
    metrics: dict[str, Any]
    generated_at: datetime
    generated_by: str


class EmpireOrchestrator:
    """
    Coordinates operations across AMT's 12-company portfolio.

    This class manages empire-wide coordination including resource allocation,
    strategic alignment, performance monitoring, and cross-company collaboration.
    It enables the leadership hierarchy to make decisions that span multiple
    companies and ensure optimal portfolio performance.

    Attributes:
        companies: Dictionary mapping company_id to Company objects
        allocations: List of ResourceAllocation objects
        performance_reports: List of PerformanceReport objects

    Example:
        >>> orchestrator = EmpireOrchestrator()
        >>> orchestrator.register_company(
        ...     company_id="amt_analytics",
        ...     name="AMT Analytics Platform",
        ...     status=CompanyStatus.ACTIVE,
        ...     primary_focus="Sports Analytics & Data Science"
        ... )
        >>> allocation = orchestrator.allocate_resources(
        ...     resource_type=ResourceType.TECHNOLOGY,
        ...     amount=100000.0,
        ...     target_companies=["amt_analytics", "amt_scouting"],
        ...     allocated_by="denauld_brown",
        ...     justification="AI infrastructure upgrade"
        ... )
    """

    def __init__(self) -> None:
        """Initialize EmpireOrchestrator."""
        self.companies: dict[str, Company] = {}
        self.allocations: list[ResourceAllocation] = []
        self.performance_reports: list[PerformanceReport] = []

        logger.info("EmpireOrchestrator initialized")

    def register_company(
        self,
        company_id: str,
        name: str,
        status: CompanyStatus,
        primary_focus: str,
        leadership_contact: str | None = None,
    ) -> None:
        """
        Register a portfolio company in the empire.

        Args:
            company_id: Unique company identifier
            name: Company name
            status: Current operational status
            primary_focus: Primary business focus
            leadership_contact: Optional contact for company leadership

        Example:
            >>> orchestrator.register_company(
            ...     company_id="amt_scouting",
            ...     name="AMT Scouting Solutions",
            ...     status=CompanyStatus.SCALING,
            ...     primary_focus="Player Scouting & Evaluation"
            ... )
        """
        company = Company(
            company_id=company_id,
            name=name,
            status=status,
            primary_focus=primary_focus,
            leadership_contact=leadership_contact,
        )

        self.companies[company_id] = company
        logger.info(f"Registered company: {name} ({company_id}) - Status: {status.value}")

    def coordinate_companies(
        self, company_ids: Sequence[str], coordination_type: str, metadata: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Coordinate operations across multiple companies.

        Args:
            company_ids: List of company IDs to coordinate
            coordination_type: Type of coordination (e.g., "strategic_alignment", "resource_sharing")
            metadata: Optional metadata about the coordination

        Returns:
            Dictionary with coordination results

        Example:
            >>> result = orchestrator.coordinate_companies(
            ...     company_ids=["amt_analytics", "amt_scouting", "amt_training"],
            ...     coordination_type="strategic_alignment",
            ...     metadata={"quarter": "Q1", "theme": "AI Integration"}
            ... )
        """
        logger.info(f"Coordinating {len(company_ids)} companies for {coordination_type}")

        # Validate all companies exist
        missing = [cid for cid in company_ids if cid not in self.companies]
        if missing:
            logger.warning(f"Companies not found: {missing}")

        valid_companies = [cid for cid in company_ids if cid in self.companies]

        result = {
            "coordination_type": coordination_type,
            "companies_involved": valid_companies,
            "companies_missing": missing,
            "timestamp": datetime.now(UTC).isoformat(),
            "metadata": metadata or {},
            "status": "coordinated" if valid_companies else "failed",
        }

        # Log coordination metrics
        result["metrics"] = {
            "total_companies": len(company_ids),
            "successful_coordination": len(valid_companies),
            "failed_coordination": len(missing),
        }

        logger.info(
            f"Coordination result: {len(valid_companies)}/{len(company_ids)} companies successfully coordinated"
        )

        return result

    def allocate_resources(
        self,
        resource_type: ResourceType,
        amount: float,
        target_companies: Sequence[str],
        allocated_by: str,
        justification: str,
        duration_months: int | None = None,
    ) -> ResourceAllocation:
        """
        Allocate resources to one or more companies.

        Args:
            resource_type: Type of resource being allocated
            amount: Amount of resource (dollars, headcount, etc.)
            target_companies: Companies receiving the allocation
            allocated_by: Bot ID making the allocation
            justification: Reason for allocation
            duration_months: Optional duration in months

        Returns:
            ResourceAllocation object

        Example:
            >>> allocation = orchestrator.allocate_resources(
            ...     resource_type=ResourceType.CAPITAL,
            ...     amount=500000.0,
            ...     target_companies=["amt_analytics"],
            ...     allocated_by="denauld_brown",
            ...     justification="Series A funding for platform expansion"
            ... )
        """
        allocation_id = self._generate_allocation_id(resource_type, allocated_by)

        allocation = ResourceAllocation(
            allocation_id=allocation_id,
            resource_type=resource_type,
            amount=amount,
            target_companies=list(target_companies),
            allocated_by=allocated_by,
            justification=justification,
            timestamp=datetime.now(UTC),
            duration_months=duration_months,
        )

        # Update company allocated resources
        amount_per_company = amount / len(target_companies) if target_companies else 0.0

        for company_id in target_companies:
            if company_id in self.companies:
                company = self.companies[company_id]
                if company.allocated_resources is None:
                    company.allocated_resources = {}

                current = company.allocated_resources.get(resource_type, 0.0)
                company.allocated_resources[resource_type] = current + amount_per_company

        self.allocations.append(allocation)

        logger.info(
            f"Allocated {resource_type.value}: ${amount:,.2f} to {len(target_companies)} companies "
            f"by {allocated_by}"
        )

        return allocation

    def monitor_performance(
        self, company_ids: Sequence[str], reporting_period: str, generated_by: str
    ) -> PerformanceReport:
        """
        Generate performance monitoring report for companies.

        Args:
            company_ids: Companies to include in report
            reporting_period: Period being reported (e.g., "Q1 2025")
            generated_by: Bot ID generating the report

        Returns:
            PerformanceReport object

        Example:
            >>> report = orchestrator.monitor_performance(
            ...     company_ids=["amt_analytics", "amt_scouting"],
            ...     reporting_period="Q1 2025",
            ...     generated_by="alexandra_martinez"
            ... )
        """
        report_id = self._generate_report_id(reporting_period, generated_by)

        # Gather metrics for each company
        metrics: dict[str, Any] = {
            "companies": {},
            "empire_totals": {
                "total_companies": len(company_ids),
                "active_companies": 0,
                "total_allocations": 0.0,
            },
        }

        for company_id in company_ids:
            if company_id not in self.companies:
                continue

            company = self.companies[company_id]

            company_metrics = {
                "name": company.name,
                "status": company.status.value,
                "primary_focus": company.primary_focus,
                "allocated_resources": {
                    rt.value: amount for rt, amount in (company.allocated_resources or {}).items()
                },
                "performance_data": company.performance_metrics or {},
            }

            metrics["companies"][company_id] = company_metrics

            if company.status == CompanyStatus.ACTIVE:
                metrics["empire_totals"]["active_companies"] += 1

            # Sum total allocations
            total_company_allocations = sum((company.allocated_resources or {}).values())
            metrics["empire_totals"]["total_allocations"] += total_company_allocations

        report = PerformanceReport(
            report_id=report_id,
            company_ids=list(company_ids),
            reporting_period=reporting_period,
            metrics=metrics,
            generated_at=datetime.now(UTC),
            generated_by=generated_by,
        )

        self.performance_reports.append(report)

        logger.info(
            f"Generated performance report {report_id} for {len(company_ids)} companies "
            f"covering period {reporting_period}"
        )

        return report

    def get_company_status(self, company_id: str) -> dict[str, Any]:
        """
        Get detailed status of a company.

        Args:
            company_id: Company identifier

        Returns:
            Dictionary with company status and metrics

        Example:
            >>> status = orchestrator.get_company_status("amt_analytics")
            >>> print(status['name'])
            'AMT Analytics Platform'
        """
        if company_id not in self.companies:
            return {"error": "Company not found", "company_id": company_id}

        company = self.companies[company_id]

        # Find allocations for this company
        company_allocations = [
            {
                "allocation_id": alloc.allocation_id,
                "resource_type": alloc.resource_type.value,
                "amount": alloc.amount,
                "allocated_by": alloc.allocated_by,
                "timestamp": alloc.timestamp.isoformat(),
            }
            for alloc in self.allocations
            if company_id in alloc.target_companies
        ]

        return {
            "company_id": company.company_id,
            "name": company.name,
            "status": company.status.value,
            "primary_focus": company.primary_focus,
            "leadership_contact": company.leadership_contact,
            "allocated_resources": {
                rt.value: amount for rt, amount in (company.allocated_resources or {}).items()
            },
            "performance_metrics": company.performance_metrics or {},
            "recent_allocations": company_allocations[-5:],  # Last 5 allocations
            "total_allocations_count": len(company_allocations),
        }

    def get_empire_overview(self) -> dict[str, Any]:
        """
        Get high-level overview of the entire empire.

        Returns:
            Dictionary with empire-wide metrics

        Example:
            >>> overview = orchestrator.get_empire_overview()
            >>> print(f"Total companies: {overview['total_companies']}")
        """
        status_breakdown = {}
        for company in self.companies.values():
            status = company.status.value
            status_breakdown[status] = status_breakdown.get(status, 0) + 1

        total_allocated = {}
        for company in self.companies.values():
            for resource_type, amount in (company.allocated_resources or {}).items():
                rt_value = resource_type.value
                total_allocated[rt_value] = total_allocated.get(rt_value, 0.0) + amount

        return {
            "total_companies": len(self.companies),
            "status_breakdown": status_breakdown,
            "total_allocations": len(self.allocations),
            "total_performance_reports": len(self.performance_reports),
            "resource_allocation_totals": total_allocated,
            "companies": list(self.companies.keys()),
        }

    def _generate_allocation_id(self, resource_type: ResourceType, allocated_by: str) -> str:
        """Generate unique allocation ID."""
        timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
        return f"alloc_{resource_type.value}_{allocated_by}_{timestamp}"

    def _generate_report_id(self, reporting_period: str, generated_by: str) -> str:
        """Generate unique report ID."""
        timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
        period_safe = reporting_period.replace(" ", "_")
        return f"report_{period_safe}_{generated_by}_{timestamp}"

    def __repr__(self) -> str:
        """String representation of EmpireOrchestrator."""
        return (
            f"EmpireOrchestrator(companies={len(self.companies)}, "
            f"allocations={len(self.allocations)}, "
            f"reports={len(self.performance_reports)})"
        )
