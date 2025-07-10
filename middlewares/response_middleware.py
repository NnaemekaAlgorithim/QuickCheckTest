# loan_app_backend/middlewares/response_middleware.py
import json
from django.http import JsonResponse
from rest_framework.exceptions import APIException

class APIResponseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Skip processing for redirect responses (300–399)
        if 300 <= response.status_code < 400:
            return response

        # Handle JsonResponse
        if isinstance(response, JsonResponse):
            try:
                content = json.loads(response.content)
                if "response_status" not in content:
                    return JsonResponse({
                        "response_status": "success" if response.status_code <= 399 else "error",
                        "response_description": content.get("response_description", content.get("message", "Request processed")),
                        "response_data": content.get("response_data", content.get("data", {})),
                    }, status=response.status_code)
            except json.JSONDecodeError:
                pass  # Handle non-JSON content below
        # Handle DRF errors or other responses
        if response.status_code > 399:
            try:
                content = json.loads(response.content) if hasattr(response, 'content') else {}
            except json.JSONDecodeError:
                content = {"detail": response.reason_phrase}
            return JsonResponse({
                "response_status": "error",
                "response_description": content.get("detail", "An error occurred"),
                "response_data": content,
            }, status=response.status_code)
        return response
