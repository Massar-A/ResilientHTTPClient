import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from httpcore import ConnectError, TimeoutException, ReadTimeout
from httpx import Response, MockTransport, HTTPError
from resilient_http_client.client import ResilientHttpClient


@pytest.mark.asyncio
@pytest.mark.parametrize("method", ["get", "post", "put", "patch", "delete"])
async def test_retry_after_failures(method):
    def mock_transport(request):
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise ConnectError("Mocked connection error")
        if attempts == 2:
            raise TimeoutException("Mocked timeout exception")
        return Response(200, content=b"Success")

    attempts = 0
    transport = MockTransport(mock_transport)
    resilient_client = ResilientHttpClient(max_attempts=3, timeout=2.0)
    resilient_client.client._transport = transport

    # Dynamically call the HTTP method
    response = await getattr(resilient_client, method)("http://test.com")

    assert response.status_code == 200
    assert response.content == b"Success"
    assert attempts == 3  # 2 retries + 1 success

    await resilient_client.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("method", ["get", "post", "put", "patch", "delete"])
async def test_retry_exceeds_limit_of_attempts_connect_error(method):
    def mock_transport(request):
        nonlocal attempts
        attempts += 1
        raise ConnectError("Mocked connection error")

    attempts = 0
    transport = MockTransport(mock_transport)
    resilient_client = ResilientHttpClient(max_attempts=2, timeout=2.0)
    resilient_client.client._transport = transport

    with pytest.raises(ConnectError):
        await getattr(resilient_client, method)("http://test.com")

    assert attempts == 2
    await resilient_client.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("method", ["get", "post", "put", "patch", "delete"])
async def test_retry_exceeds_limit_of_attempts_timeout_error(method):
    def mock_transport(request):
        nonlocal attempts
        attempts += 1
        raise TimeoutException("Mocked timeout exception")

    attempts = 0
    transport = MockTransport(mock_transport)
    resilient_client = ResilientHttpClient(max_attempts=3, timeout=2.0)
    resilient_client.client._transport = transport

    with pytest.raises(TimeoutException):
        await getattr(resilient_client, method)("http://test.com")

    assert attempts == 3
    await resilient_client.close()

#We check if the request is retried after a http error
@pytest.mark.asyncio
@pytest.mark.parametrize("method", ["get", "post", "put", "patch", "delete"])
async def test_http_error(method):
    def mock_transport(request):
        nonlocal attempts
        attempts += 1
        raise HTTPError("Mocked HTTP error")

    attempts = 0
    transport = MockTransport(mock_transport)
    resilient_client = ResilientHttpClient(max_attempts=3, timeout=2.0)
    resilient_client.client._transport = transport

    with pytest.raises(HTTPError):
        await getattr(resilient_client, method)("http://test.com")

    assert attempts == 1  # No retries for HTTP errors
    await resilient_client.close()

@pytest.mark.asyncio
@pytest.mark.parametrize("method", ["get", "post", "put", "patch", "delete"])
async def test_custom_headers(method):
    def mock_transport(request):
        assert request.headers["Authorization"] == "Bearer my-token"
        return Response(200)

    transport = MockTransport(mock_transport)
    resilient_client = ResilientHttpClient()
    resilient_client.client._transport = transport

    response = await getattr(resilient_client, method)("http://test.com", headers={"Authorization": "Bearer my-token"})
    assert response.status_code == 200

@pytest.mark.asyncio
@pytest.mark.parametrize("method", ["get", "post", "put", "patch", "delete"])
async def test_query_params(method):
    def mock_transport(request):
        assert request.url.query == b"key=value"
        return Response(200)

    transport = MockTransport(mock_transport)
    resilient_client = ResilientHttpClient()
    resilient_client.client._transport = transport

    response = await getattr(resilient_client, method)("http://test.com", params={"key": "value"})
    assert response.status_code == 200

@pytest.mark.asyncio
@pytest.mark.parametrize("method", ["post", "put", "patch"])
async def test_payload(method):
    def mock_transport(request):
        assert request.content == b'{"key":"value"}'
        return Response(200)

    transport = MockTransport(mock_transport)
    resilient_client = ResilientHttpClient()
    resilient_client.client._transport = transport

    response = await getattr(resilient_client, method)("http://test.com", json={"key": "value"})
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_client_closing():
    resilient_client = ResilientHttpClient()
    await resilient_client.close()
    assert resilient_client.client.is_closed



