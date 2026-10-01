"""JSON transport for the public, stateless inference API."""
import json
import logging
from functools import wraps

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pydantic import BaseModel, ValidationError

from errors import APIError

logger = logging.getLogger(__name__)


def serialize(value):
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, list):
        return [serialize(item) for item in value]
    return value


def endpoint(method, schema=None):
    def decorate(view):
        @csrf_exempt  # Public API: no cookies, sessions, or authenticated actions.
        @wraps(view)
        def dispatch(request, **kwargs):
            if request.method != method:
                response = JsonResponse({"detail": "Method Not Allowed"}, status=405)
                response["Allow"] = method
                return response
            try:
                if schema is not None:
                    try:
                        payload = json.loads(request.body)
                    except (ValueError, UnicodeDecodeError):
                        raise APIError(400, "Invalid JSON body")
                    try:
                        kwargs["req"] = schema.model_validate(payload)
                    except ValidationError as exc:
                        errors = json.loads(exc.json(include_url=False, include_context=False))
                        for error in errors:
                            error["loc"] = ["body", *error["loc"]]
                        return JsonResponse({"detail": errors}, status=422)
                result = serialize(view(**kwargs))
                return JsonResponse(result, safe=not isinstance(result, list))
            except APIError as exc:
                return JsonResponse({"detail": exc.detail}, status=exc.status_code)
            except Exception:
                logger.exception("Inference API request failed")
                return JsonResponse({"detail": "Internal server error"}, status=500)
        return dispatch
    return decorate
