from dataclasses import dataclass
from typing import Any

import httpx


class ApiError(RuntimeError):
    def __init__(self, detail: str, status_code: int = 1):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


@dataclass
class ApiClient:
    api_base_url: str
    api_key: str
    transport: httpx.BaseTransport | None = None

    def __post_init__(self):
        self.client = httpx.Client(
            base_url=self.api_base_url.rstrip('/'),
            transport=self.transport,
            timeout=30,
            headers={'Authorization': f'Bearer {self.api_key}'},
        )

    def close(self) -> None:
        self.client.close()

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> httpx.Response:
        response = self.client.request(
            method,
            path,
            params=params,
            json=json,
        )
        if response.is_error:
            raise ApiError(_extract_error_detail(response), response.status_code)
        return response

    def get_json(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> Any:
        return self.request('GET', path, params=params).json()

    def post_json(self, path: str, payload: dict[str, Any]) -> Any:
        return self.request('POST', path, json=payload).json()

    def put_json(self, path: str, payload: dict[str, Any]) -> Any:
        return self.request('PUT', path, json=payload).json()


def _extract_error_detail(response: httpx.Response) -> str:
    try:
        data = response.json()
    except ValueError:
        return f'API request failed with status {response.status_code}'
    detail = data.get('detail') if isinstance(data, dict) else None
    return detail or f'API request failed with status {response.status_code}'
