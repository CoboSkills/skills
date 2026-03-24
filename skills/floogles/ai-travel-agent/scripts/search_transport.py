#!/usr/bin/env python3
"""
Search ground transport options between two cities via SerpAPI Google Maps Directions.
Returns trains, buses, ferries with duration, price, operator and booking links.

Usage: python3 search_transport.py --from "Rome, Italy" --to "Florence, Italy" --key YOUR_KEY
"""

import argparse
import json
import sys
import requests


def search_transport(origin, destination, api_key, currency=None):
    params = {
        "engine": "google_maps_directions",
        "start_addr": origin,
        "end_addr": destination,
        "travel_mode": 3,  # Transit
        "hl": "en",
        "api_key": api_key,
    }

    resp = requests.get("https://serpapi.com/search", params=params)
    resp.raise_for_status()
    data = resp.json()

    if "error" in data:
        print(f"ERROR: {data['error']}", file=sys.stderr)
        sys.exit(1)

    results = []
    seen = set()  # deduplicate by operator + duration

    for route in data.get("directions", []):
        trips = route.get("trips", [])
        if not trips:
            continue

        trip = trips[0]
        operator = trip.get("service_run_by", {}).get("name", "Unknown")
        booking_link = trip.get("service_run_by", {}).get("link", "")
        duration = route.get("formatted_duration", "")
        cost = route.get("cost")
        route_currency = route.get("currency", "")
        distance = route.get("formatted_distance", "")

        # Determine transport type from icon or title
        icon = trip.get("icon", "").lower()
        if "bus" in icon:
            transport_type = "Bus"
        elif "rail" in icon or "train" in icon or "subway" in icon:
            transport_type = "Train"
        elif "ferry" in icon or "boat" in icon:
            transport_type = "Ferry"
        else:
            transport_type = "Transit"

        # Also infer from known operators
        known_trains = ["trenitalia", "italo", "renfe", "sncf", "db ", "eurostar",
                        "thalys", "avlo", "ouigo", "trainline", "cp ", "comboios"]
        if any(t in operator.lower() for t in known_trains):
            transport_type = "Train"

        dedup_key = f"{operator}|{duration}"
        if dedup_key in seen:
            continue
        seen.add(dedup_key)

        entry = {
            "type": transport_type,
            "operator": operator,
            "duration": duration,
            "distance": distance,
            "price": f"{route_currency}{cost}" if cost else None,
            "price_raw": cost,
            "currency": route_currency,
            "departs": trip.get("start_stop", {}).get("time"),
            "from_stop": trip.get("start_stop", {}).get("name"),
            "arrives": trip.get("end_stop", {}).get("time"),
            "to_stop": trip.get("end_stop", {}).get("name"),
            "booking_link": booking_link,
        }
        results.append(entry)

    # Sort: trains first, then by duration
    type_order = {"Train": 0, "Ferry": 1, "Bus": 2, "Transit": 3}
    results.sort(key=lambda x: (type_order.get(x["type"], 9),
                                 _parse_minutes(x["duration"])))

    print(json.dumps(results, indent=2))


def _parse_minutes(duration_str):
    """Convert '1 hr 26 min' or '3 hr 15 min' to total minutes for sorting."""
    if not duration_str:
        return 9999
    total = 0
    if "hr" in duration_str:
        parts = duration_str.split("hr")
        total += int(parts[0].strip()) * 60
        if "min" in parts[1]:
            total += int(parts[1].replace("min", "").strip())
    elif "min" in duration_str:
        total = int(duration_str.replace("min", "").strip())
    return total


def main():
    parser = argparse.ArgumentParser(
        description="Search ground transport between two cities via SerpAPI")
    parser.add_argument("--from", dest="origin", required=True,
                        help="Origin city/place (e.g. 'Rome, Italy')")
    parser.add_argument("--to", dest="destination", required=True,
                        help="Destination city/place (e.g. 'Florence, Italy')")
    parser.add_argument("--key", required=True, help="SerpAPI key")
    parser.add_argument("--currency", default=None,
                        help="Preferred currency for display (informational only)")

    args = parser.parse_args()
    search_transport(args.origin, args.destination, args.key, args.currency)


if __name__ == "__main__":
    main()
