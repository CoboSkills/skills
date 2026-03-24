#!/usr/bin/env python3
"""
Search Google Hotels via SerpAPI.
Usage: python3 search_hotels.py --location "Barcelona" --check-in 2026-06-15 --check-out 2026-06-22 --adults 2 --key YOUR_KEY [--stars 4] [--amenities "pool,beach"] [--sort lowest_price]
"""

import argparse
import json
import sys
import requests


def search_hotels(location, check_in, check_out, adults=1, children=0,
                  min_stars=None, amenities=None, sort_by=None,
                  currency="GBP", api_key=None):
    """
    sort_by options: 3=Lowest price, 8=Highest rating, 13=Most reviewed
    amenities: list of strings e.g. ["pool", "free breakfast", "beach access"]
    """
    params = {
        "engine": "google_hotels",
        "q": location,
        "check_in_date": check_in,
        "check_out_date": check_out,
        "adults": adults,
        "children": children,
        "currency": currency,
        "hl": "en",
        "gl": "uk",
        "api_key": api_key,
    }

    if min_stars:
        params["min_star_rating"] = min_stars
    if sort_by:
        sort_map = {"lowest_price": 3, "highest_rating": 8, "most_reviewed": 13}
        params["sort_by"] = sort_map.get(sort_by, 3)

    resp = requests.get("https://serpapi.com/search", params=params)
    resp.raise_for_status()
    data = resp.json()

    if "error" in data:
        print(f"ERROR: {data['error']}", file=sys.stderr)
        sys.exit(1)

    results = []
    for prop in data.get("properties", []):
        rate = prop.get("rate_per_night", {})
        entry = {
            "name": prop.get("name"),
            "type": prop.get("type"),
            "stars": prop.get("hotel_class"),
            "rating": prop.get("overall_rating"),
            "reviews": prop.get("reviews"),
            "price_per_night": rate.get("lowest"),
            "price_before_taxes": rate.get("before_taxes_fees"),
            "amenities": prop.get("amenities", []),
            "nearby": [p.get("name") for p in prop.get("nearby_places", [])[:3]],
            "description": prop.get("description"),
            "link": prop.get("link"),
            "images": [img.get("thumbnail") for img in prop.get("images", [])[:2]],
        }

        # Filter by amenities if specified
        if amenities:
            hotel_amenities_lower = [a.lower() for a in entry["amenities"]]
            if not all(any(req.lower() in a for a in hotel_amenities_lower) for req in amenities):
                continue

        results.append(entry)

    print(json.dumps(results[:10], indent=2))


def main():
    parser = argparse.ArgumentParser(description="Search Google Hotels via SerpAPI")
    parser.add_argument("--location", required=True, help="Location to search (e.g. 'Barcelona')")
    parser.add_argument("--check-in", required=True, help="Check-in date YYYY-MM-DD")
    parser.add_argument("--check-out", required=True, help="Check-out date YYYY-MM-DD")
    parser.add_argument("--adults", type=int, default=1)
    parser.add_argument("--children", type=int, default=0)
    parser.add_argument("--stars", type=int, default=None, help="Minimum star rating (1-5)")
    parser.add_argument("--amenities", default=None, help="Comma-separated amenities to filter by (e.g. 'pool,beach')")
    parser.add_argument("--sort", default="lowest_price",
                        choices=["lowest_price", "highest_rating", "most_reviewed"])
    parser.add_argument("--currency", default="GBP")
    parser.add_argument("--key", required=True, help="SerpAPI key")

    args = parser.parse_args()

    amenities = [a.strip() for a in args.amenities.split(",")] if args.amenities else None

    search_hotels(
        location=args.location,
        check_in=args.check_in,
        check_out=args.check_out,
        adults=args.adults,
        children=args.children,
        min_stars=args.stars,
        amenities=amenities,
        sort_by=args.sort,
        currency=args.currency,
        api_key=args.key,
    )


if __name__ == "__main__":
    main()
