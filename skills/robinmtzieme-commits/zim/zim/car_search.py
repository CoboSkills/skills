"""Car rental search module for Zim.

Builds structured CarResult objects with affiliate deeplinks to
Rentalcars, Kayak, Discover Cars, and Economy Bookings.
No structured car API is available in MVP.
"""

from __future__ import annotations

import logging
from datetime import date
from urllib.parse import quote

from zim.core import CarResult, Policy, apply_policy_to_car
from zim.providers.travelpayouts import _get_marker

logger = logging.getLogger(__name__)


def _build_rentalcars_link(
    location: str,
    pickup: date,
    dropoff: date,
) -> str:
    """Build Rentalcars affiliate search deeplink."""
    marker = _get_marker()
    encoded = quote(location)
    return (
        f"https://www.rentalcars.com/search"
        f"?location={encoded}"
        f"&puDay={pickup.day}&puMonth={pickup.month}&puYear={pickup.year}"
        f"&doDay={dropoff.day}&doMonth={dropoff.month}&doYear={dropoff.year}"
        f"&driversAge=30"
        f"&affiliateCode={marker}"
    )


def _build_kayak_link(
    location: str,
    pickup: date,
    dropoff: date,
) -> str:
    """Build Kayak car search deeplink."""
    encoded = quote(location)
    return (
        f"https://www.kayak.com/cars/{encoded}"
        f"/{pickup.isoformat()}/{dropoff.isoformat()}"
        f"?sort=price_a"
    )


def _build_discover_cars_link(
    location: str,
    pickup: date,
    dropoff: date,
) -> str:
    """Build Discover Cars affiliate search deeplink."""
    marker = _get_marker()
    encoded = quote(location)
    return (
        f"https://www.discovercars.com/search"
        f"?location={encoded}"
        f"&pick_up_date={pickup.isoformat()}"
        f"&drop_off_date={dropoff.isoformat()}"
        f"&marker={marker}"
    )


def _build_economy_bookings_link(
    location: str,
    pickup: date,
    dropoff: date,
) -> str:
    """Build Economy Bookings search deeplink."""
    encoded = quote(location)
    return (
        f"https://www.economybookings.com/search"
        f"?location={encoded}"
        f"&pick_up={pickup.isoformat()}"
        f"&drop_off={dropoff.isoformat()}"
    )


def search(
    location: str,
    pickup: date,
    dropoff: date,
    car_class: str | None = None,
    policy: Policy | None = None,
) -> list[CarResult]:
    """Search car rentals and return structured results with affiliate deeplinks.

    In MVP, this returns deeplink-based results for four providers.
    No structured API is available, so prices are not populated.

    Args:
        location: Pickup city or airport name.
        pickup: Pickup date.
        dropoff: Drop-off date.
        car_class: Optional vehicle class filter (for future API use).
        policy: Optional travel policy for annotations.

    Returns:
        List of CarResult objects with affiliate deeplinks.
    """
    vehicle = car_class or "any"

    results: list[CarResult] = [
        CarResult(
            provider="Rentalcars",
            vehicle_class=vehicle,
            pickup_location=location,
            link=_build_rentalcars_link(location, pickup, dropoff),
            free_cancellation=True,
        ),
        CarResult(
            provider="Kayak",
            vehicle_class=vehicle,
            pickup_location=location,
            link=_build_kayak_link(location, pickup, dropoff),
            free_cancellation=False,
        ),
        CarResult(
            provider="Discover Cars",
            vehicle_class=vehicle,
            pickup_location=location,
            link=_build_discover_cars_link(location, pickup, dropoff),
            free_cancellation=True,
        ),
        CarResult(
            provider="Economy Bookings",
            vehicle_class=vehicle,
            pickup_location=location,
            link=_build_economy_bookings_link(location, pickup, dropoff),
            free_cancellation=False,
        ),
    ]

    # Apply policy annotations
    if policy:
        results = [apply_policy_to_car(r, policy) for r in results]

    return results
