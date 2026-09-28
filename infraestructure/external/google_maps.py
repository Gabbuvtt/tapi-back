"""
Google Maps / Places API client.

Provides helpers for:
- Building Google Maps review deep links.
- Fetching business info from Google Places.
"""

import httpx

from core.config import settings
from core.exceptions import ExternalServiceError


class GoogleMapsClient:
    """Client for Google Maps / Places API interactions."""

    BASE_URL = "https://maps.googleapis.com/maps/api/place"

    def __init__(self):
        self._api_key = settings.GOOGLE_MAPS_API_KEY

    async def get_place_details(self, place_id: str) -> dict:
        """
        Fetch place details from Google Places API.

        Args:
            place_id: The Google Place ID.

        Returns:
            dict with place name, address, rating, etc.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/details/json",
                params={
                    "place_id": place_id,
                    "fields": "name,formatted_address,rating,user_ratings_total,url",
                    "key": self._api_key,
                },
            )

            if response.status_code != 200:
                raise ExternalServiceError(
                    service="Google Maps",
                    detail="Failed to fetch place details",
                )

            data = response.json()
            if data.get("status") != "OK":
                raise ExternalServiceError(
                    service="Google Maps",
                    detail=f"Google Places error: {data.get('status')}",
                )

            result = data["result"]
            return {
                "name": result.get("name"),
                "address": result.get("formatted_address"),
                "rating": result.get("rating"),
                "total_ratings": result.get("user_ratings_total"),
                "url": result.get("url"),
            }

    @staticmethod
    def build_review_url(place_id: str) -> str:
        """
        Build a deep link to Google Maps review form.

        Opens directly on the "Write a review" screen.
        """
        return f"https://search.google.com/local/writereview?placeid={place_id}"

    @staticmethod
    def build_place_url(place_id: str) -> str:
        """Build a link to the Google Maps place page."""
        return f"https://www.google.com/maps/place/?q=place_id:{place_id}"
