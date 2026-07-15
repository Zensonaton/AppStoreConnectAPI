# coding: utf-8

from unittest.mock import MagicMock

import pytest


class TestApiRequest:
    def test_returns_json_dict(self, client, mock_response):
        payload = {"data": {"id": "1"}}
        client.http_client.request = MagicMock(return_value=mock_response(payload))

        result = client._api_request_("GET", "/bundleIds")

        assert result == payload

    def test_sends_expected_request(self, client, mock_response):
        client.http_client.request = MagicMock(return_value=mock_response({"data": []}))

        client._api_request_(
            "POST",
            "/bundleIds",
            params={"limit": 10},
            data={"foo": "bar"},
        )

        client.http_client.request.assert_called_once()
        args, kwargs = client.http_client.request.call_args
        assert args[0] == "POST"
        assert args[1] == f"{client.base_url}/bundleIds"
        assert kwargs["json"] == {"foo": "bar"}
        assert kwargs["params"] == {"limit": 10}
        assert kwargs["headers"]["Authorization"] == f"Bearer {client.jwt_token}"

    def test_raises_on_non_dict_json(self, client, mock_response):
        client.http_client.request = MagicMock(return_value=mock_response(["not", "a", "dict"]))

        with pytest.raises(ValueError, match="Expected JSON response to be a dict"):
            client._api_request_("GET", "/bundleIds")

    def test_raises_on_api_errors(self, client, mock_response):
        payload = {
            "errors": [
                {
                    "code": "NOT_FOUND",
                    "title": "Resource not found",
                    "detail": "The bundle id does not exist",
                }
            ]
        }
        client.http_client.request = MagicMock(return_value=mock_response(payload))

        with pytest.raises(Exception) as exc_info:
            client._api_request_("GET", "/bundleIds")

        message = str(exc_info.value)
        assert "NOT_FOUND: Resource not found" in message
        assert "The bundle id does not exist" in message

    def test_uses_first_error(self, client, mock_response):
        payload = {
            "errors": [
                {"code": "FIRST", "title": "First error", "detail": "first detail"},
                {"code": "SECOND", "title": "Second error", "detail": "second detail"},
            ]
        }
        client.http_client.request = MagicMock(return_value=mock_response(payload))

        with pytest.raises(Exception, match="FIRST"):
            client._api_request_("GET", "/bundleIds")

    def test_empty_errors_list_does_not_raise(self, client, mock_response):
        payload = {"errors": [], "data": {"id": "1"}}
        client.http_client.request = MagicMock(return_value=mock_response(payload))

        assert client._api_request_("GET", "/bundleIds") == payload


class TestApiNamespaces:
    def test_client_exposes_every_namespace(self, client):
        assert client.apps._client is client
        assert client.app_store_versions._client is client
        assert client.bundle_ids._client is client
        assert client.certificates._client is client
        assert client.pre_release_versions._client is client
        assert client.profiles._client is client

    def test_get_returns_full_response(self, client, mock_response):
        payload = {"data": [{"id": "1"}], "included": [{"id": "2"}]}
        client.http_client.request = MagicMock(return_value=mock_response(payload))

        assert client._api_get_("/apps") == payload

    def test_post_returns_full_response(self, client, mock_response):
        payload = {"data": {"id": "1"}}
        client.http_client.request = MagicMock(return_value=mock_response(payload))

        assert client._api_post_("/profiles") == payload
