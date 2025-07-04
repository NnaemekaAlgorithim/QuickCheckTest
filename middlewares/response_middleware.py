import json
from django.http import JsonResponse


class APIResponseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Skip processing for redirect responses (300–399)
        if 300 <= response.status_code < 400:
            return response

        # Check if the response is already a JsonResponse
        if isinstance(response, JsonResponse):
            # Add standard fields if not already present
            if "response_status" not in response.content.decode():
                content = json.loads(response.content)
                standardized_response = {
                    "response_status": "success" if response.status_code <= 399 else "error",
                    "response_description": content.get("message", "Request processed"),
                    "response_data": content.get("data", {}),
                }
                return JsonResponse(standardized_response, status=response.status_code)
        
        # Handle other response types (e.g., HTML or other)
        if response.status_code > 399:
            standardized_response = {
                "response_status": "error",
                "response_description": response.reason_phrase,
                "response_data": {},
            }
            return JsonResponse(standardized_response, status=response.status_code)

        return response
