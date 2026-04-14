"""Booking executor interface for Zim.

This module defines the abstract interface for executing bookings with
travel providers (airlines, hotels, car rental companies). The MVP ships
with a **placeholder implementation** that explicitly does NOT execute
real bookings — it returns a structured result indicating that provider
integration is pending.

Architecture:
    BookingExecutor (ABC)
        ├── PlaceholderExecutor  — MVP: returns "pending_provider_integration"
        ├── (future) AmadeusExecutor
        ├── (future) SabreExecutor
        └── (future) DirectApiExecutor

Each executor receives a confirmed, paid booking and attempts to create
the actual reservation with the provider. The result includes:
    - provider_confirmation_code: PNR / confirmation number (None if not booked)
    - provider_status: pending_provider_integration / confirmed / failed / ...
    - provider_raw_response: raw API response for debugging
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from datetime import datetime, UTC
from typing import Any, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class BookingExecutionRequest(BaseModel):
    """Input to a booking executor — everything needed to create a reservation."""

    booking_id: str
    category: str  # flight / hotel / car

    # Provider reference (from search result)
    provider_name: str = ""
    provider_link: str = ""  # affiliate/direct booking link
    search_result_id: str = ""  # ID of the selected search result

    # Traveler details (from TravelerInfo)
    traveler_first_name: str = ""
    traveler_last_name: str = ""
    traveler_email: str = ""
    traveler_phone: str = ""
    traveler_passport_number: Optional[str] = None

    # Payment reference
    stripe_session_id: str = ""
    amount_cents: int = 0

    # Trip details
    origin: str = ""
    destination: str = ""
    departure_date: Optional[str] = None
    return_date: Optional[str] = None

    extra: dict[str, Any] = Field(default_factory=dict)


class BookingExecutionResult(BaseModel):
    """Output from a booking executor — the provider's response."""

    booking_id: str
    category: str

    # Provider confirmation
    provider_confirmation_code: Optional[str] = None
    provider_status: str = "pending_provider_integration"
    provider_name: str = ""
    provider_raw_response: Optional[dict[str, Any]] = None

    # Timestamps
    executed_at: Optional[str] = None
    error_message: Optional[str] = None

    @property
    def is_confirmed(self) -> bool:
        return self.provider_status == "confirmed"

    @property
    def is_failed(self) -> bool:
        return self.provider_status == "failed"


class BookingExecutor(ABC):
    """Abstract base class for booking executors.

    Subclass this to integrate with a real travel provider API.
    """

    @abstractmethod
    def execute(self, request: BookingExecutionRequest) -> BookingExecutionResult:
        """Execute a booking with the provider.

        Args:
            request: All details needed to create the reservation.

        Returns:
            BookingExecutionResult with provider confirmation or failure.
        """
        ...

    @abstractmethod
    def check_status(self, booking_id: str, confirmation_code: str) -> BookingExecutionResult:
        """Check the status of a previously executed booking."""
        ...

    @abstractmethod
    def cancel(self, booking_id: str, confirmation_code: str) -> BookingExecutionResult:
        """Request cancellation of a confirmed booking."""
        ...


class PlaceholderExecutor(BookingExecutor):
    """MVP placeholder that does NOT execute real bookings.

    Returns structured results indicating that provider integration
    is pending. The booking link is preserved so the user can complete
    the booking manually via the affiliate/direct link.
    """

    def execute(self, request: BookingExecutionRequest) -> BookingExecutionResult:
        logger.info(
            "PlaceholderExecutor: booking %s (%s) — provider integration pending. "
            "User should complete booking via: %s",
            request.booking_id, request.category, request.provider_link,
        )

        return BookingExecutionResult(
            booking_id=request.booking_id,
            category=request.category,
            provider_confirmation_code=None,
            provider_status="pending_provider_integration",
            provider_name=request.provider_name,
            provider_raw_response={
                "message": (
                    "Automated booking execution is not yet available. "
                    "Payment has been collected. The user should complete "
                    "the booking manually using the provided link."
                ),
                "booking_link": request.provider_link,
                "manual_action_required": True,
            },
            executed_at=datetime.now(UTC).isoformat(),
        )

    def check_status(self, booking_id: str, confirmation_code: str) -> BookingExecutionResult:
        return BookingExecutionResult(
            booking_id=booking_id,
            category="unknown",
            provider_status="pending_provider_integration",
            error_message="Status check not available — provider integration pending",
        )

    def cancel(self, booking_id: str, confirmation_code: str) -> BookingExecutionResult:
        return BookingExecutionResult(
            booking_id=booking_id,
            category="unknown",
            provider_status="pending_provider_integration",
            error_message="Cancellation not available — provider integration pending",
        )


def get_executor(provider: str = "placeholder") -> BookingExecutor:
    """Factory: return the appropriate booking executor.

    Currently only returns PlaceholderExecutor. When real provider
    integrations are built, this will route by provider name.
    """
    # Future: match on provider name
    # if provider == "amadeus": return AmadeusExecutor(...)
    return PlaceholderExecutor()
