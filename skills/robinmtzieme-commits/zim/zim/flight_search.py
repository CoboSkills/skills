"""Flight search module for Zim.

Searches the Travelpayouts API for flights, applies policy annotations,
and returns structured FlightResult objects with affiliate deeplinks.
"""

from __future__ import annotations

import logging
from datetime import date, datetime
from typing import Optional

import httpx

from zim.core import Constraints, FlightResult, Policy, apply_policy_to_flight
from zim.providers import travelpayouts

logger = logging.getLogger(__name__)


def _parse_datetime(value: str | None) -> datetime | None:
    """Parse an ISO-ish datetime string, returning None on failure."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def _api_result_to_flight(raw: dict, marker: str) -> FlightResult:
    """Convert a single Travelpayouts API result dict into a FlightResult."""
    # The API link field is a relative path; prepend Aviasales base
    link = raw.get("link", "")
    if link and not link.startswith("http"):
        link = f"https://www.aviasales.com{link}&marker={marker}"
    elif not link:
        link = ""

    return FlightResult(
        airline=raw.get("airline", ""),
        flight_number=raw.get("flight_number", ""),
        origin=raw.get("origin", ""),
        destination=raw.get("destination", ""),
        depart_at=_parse_datetime(raw.get("departure_at")),
        arrive_at=_parse_datetime(raw.get("return_at")),
        transfers=raw.get("transfers", 0),
        cabin=_cabin_from_trip_class(raw.get("trip_class", 0)),
        price_usd=float(raw.get("price", 0)),
        refundable=False,  # Travelpayouts doesn't expose this field
        link=link,
    )


def _cabin_from_trip_class(trip_class: int | str) -> str:
    """Map Travelpayouts trip_class int to human-readable cabin."""
    mapping = {0: "economy", 1: "business", 2: "first"}
    if isinstance(trip_class, int):
        return mapping.get(trip_class, "economy")
    return str(trip_class) if trip_class else "economy"


def _apply_constraints(
    results: list[FlightResult],
    constraints: Constraints | None,
) -> list[FlightResult]:
    """Filter results based on per-search constraints."""
    if not constraints:
        return results

    filtered = results

    if constraints.direct_only:
        filtered = [r for r in filtered if r.transfers == 0]

    if constraints.cabin_class:
        cabin = constraints.cabin_class.lower()
        filtered = [r for r in filtered if r.cabin.lower() == cabin]

    if constraints.preferred_departure_window and constraints.preferred_departure_window[0] is not None:
        start_h, end_h = constraints.preferred_departure_window
        filtered = [
            r for r in filtered
            if r.depart_at and start_h <= r.depart_at.hour <= end_h
        ]

    return filtered


def search(
    origin: str,
    destination: str,
    departure: date,
    return_date: date | None = None,
    currency: str = "USD",
    limit: int = 10,
    policy: Policy | None = None,
    constraints: Constraints | None = None,
) -> list[FlightResult]:
    """Search for flights and return policy-annotated results.

    Strategy:
    1. Try Travelpayouts prices_for_dates endpoint (exact dates)
    2. If empty → fallback to get_cheap_prices (month-level cached)
    3. If API fails entirely → return a single deeplink-only result

    All results include affiliate deeplinks and policy annotations.
    """
    marker = travelpayouts._get_marker()
    results: list[FlightResult] = []

    # --- Attempt 1: Exact-date search ---
    try:
        data = travelpayouts.get_flight_prices_for_dates(
            origin=origin,
            destination=destination,
            departure=departure,
            return_date=return_date,
            currency=currency,
            limit=limit,
        )
        raw_results = data.get("data", [])
        results = [_api_result_to_flight(r, marker) for r in raw_results]
        logger.info("prices_for_dates returned %d results", len(results))
    except EnvironmentError:
        logger.warning("TRAVELPAYOUTS_TOKEN not set — falling back to deeplink only")
    except httpx.HTTPError as exc:
        logger.warning("Travelpayouts API error: %s — trying cheap prices fallback", exc)

    # --- Attempt 2: Cheap prices fallback ---
    if not results:
        try:
            month_str = departure.strftime("%Y-%m")
            data = travelpayouts.get_cheap_prices(
                origin=origin,
                destination=destination,
                departure_month=month_str,
                currency=currency,
            )
            raw_results = data.get("data", [])
            results = [_api_result_to_flight(r, marker) for r in raw_results[:limit]]
            logger.info("cheap prices fallback returned %d results", len(results))
        except (EnvironmentError, httpx.HTTPError) as exc:
            logger.warning("Cheap prices fallback failed: %s", exc)

    # --- Attempt 3: Pure deeplink fallback ---
    if not results:
        deeplink = travelpayouts.build_flight_deeplink(
            origin=origin,
            destination=destination,
            departure=departure,
            return_date=return_date,
        )
        results = [
            FlightResult(
                airline="",
                origin=origin.upper(),
                destination=destination.upper(),
                link=deeplink,
                policy_status="approved",
            )
        ]
        logger.info("Using deeplink-only fallback")

    # Apply constraints filtering
    if constraints:
        results = _apply_constraints(results, constraints)

    # Apply policy annotations
    if policy:
        results = [apply_policy_to_flight(r, policy) for r in results]

    return results
