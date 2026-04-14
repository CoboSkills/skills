"""Hotel search module for Zim.

Builds structured HotelResult objects with affiliate deeplinks to
Hotellook, Booking.com, and Google Hotels. No structured API is
available in MVP — results are deeplink-based with estimated pricing.
"""

from __future__ import annotations

import logging
from datetime import date
from typing import Optional
from urllib.parse import quote, urlencode

from zim.core import HotelResult, Policy, apply_policy_to_hotel
from zim.providers.travelpayouts import _get_marker

logger = logging.getLogger(__name__)


def _build_hotellook_link(
    location: str,
    checkin: date,
    checkout: date,
    adults: int = 2,
) -> str:
    """Build Hotellook affiliate search deeplink."""
    marker = _get_marker()
    params = urlencode({
        "destination": location,
        "checkIn": checkin.isoformat(),
        "checkOut": checkout.isoformat(),
        "adults": adults,
        "marker": marker,
    })
    return f"https://search.hotellook.com/search?{params}"


def _build_booking_link(
    location: str,
    checkin: date,
    checkout: date,
    adults: int = 2,
) -> str:
    """Build Booking.com search deeplink."""
    marker = _get_marker()
    params = urlencode({
        "ss": location,
        "checkin": checkin.isoformat(),
        "checkout": checkout.isoformat(),
        "group_adults": adults,
        "aid": marker,
    })
    return f"https://www.booking.com/searchresults.html?{params}"


def _build_google_hotels_link(
    location: str,
    checkin: date,
    checkout: date,
) -> str:
    """Build Google Hotels search deeplink."""
    encoded = quote(location)
    return (
        f"https://www.google.com/travel/hotels/{encoded}"
        f"?q={encoded}"
        f"&dates={checkin.isoformat()},{checkout.isoformat()}"
    )


def search(
    location: str,
    checkin: date,
    checkout: date,
    currency: str = "USD",
    adults: int = 2,
    policy: Policy | None = None,
    stars_min: int = 0,
) -> list[HotelResult]:
    """Search hotels and return structured results with affiliate deeplinks.

    In MVP, this returns deeplink-based results for three providers
    (Hotellook, Booking.com, Google Hotels) since no structured hotel
    API is available. Price estimates are not included (set to 0).

    Args:
        location: City or destination name.
        checkin: Check-in date.
        checkout: Check-out date.
        currency: Price currency (for future API use).
        adults: Number of adult guests.
        policy: Optional travel policy for annotations.
        stars_min: Minimum star rating filter.

    Returns:
        List of HotelResult objects with affiliate deeplinks.
    """
    results: list[HotelResult] = []

    # Hotellook (Travelpayouts partner)
    results.append(
        HotelResult(
            name=f"Hotels in {location} (Hotellook)",
            location=location,
            link=_build_hotellook_link(location, checkin, checkout, adults),
            stars=0,
            nightly_rate_usd=0.0,
        )
    )

    # Booking.com
    results.append(
        HotelResult(
            name=f"Hotels in {location} (Booking.com)",
            location=location,
            link=_build_booking_link(location, checkin, checkout, adults),
            stars=0,
            nightly_rate_usd=0.0,
        )
    )

    # Google Hotels
    results.append(
        HotelResult(
            name=f"Hotels in {location} (Google Hotels)",
            location=location,
            link=_build_google_hotels_link(location, checkin, checkout),
            stars=0,
            nightly_rate_usd=0.0,
        )
    )

    # Apply star filter
    if stars_min > 0:
        results = [r for r in results if r.stars >= stars_min or r.stars == 0]

    # Apply policy annotations
    if policy:
        results = [apply_policy_to_hotel(r, policy) for r in results]

    return results
