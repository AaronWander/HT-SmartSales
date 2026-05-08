#2027-04-28-zty-start
import json

import httpx

from tools import ragflow_tool


class _FakeResponse:
    def __init__(self, *, status_code=200, url="http://test", json_body=None, text="", lines=None, method="POST"):
        self.status_code = status_code
        self._json_body = json_body
        self.text = text
        self._lines = lines or []
        self.request = httpx.Request(method, url)

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                f"HTTP {self.status_code}",
                request=self.request,
                response=self,
            )

    def iter_lines(self):
        for line in self._lines:
            yield line

    def json(self):
        return self._json_body


def test_ragflow_completion_prefers_search_completion(monkeypatch):
    search_id = "search-123"
    base = "http://ragflow.local"

    class _FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def post(self, url, json=None, headers=None):
            assert url == f"{base}/api/v1/searches/{search_id}/completion"
            return _FakeResponse(
                status_code=200,
                url=url,
                lines=[
                    'data:{"code":0,"message":"","data":{"answer":"Refund window is 7 days.","reference":[{"doc":"a"}]}}',
                    'data:{"code":0,"message":"","data":true}',
                ],
            )

    monkeypatch.setattr(ragflow_tool.httpx, "Client", _FakeClient)

    raw = ragflow_tool.ragflow_completion(
        question="What is refund window?",
        search_id=search_id,
        base_url=base,
        api_token="tok",
    )
    payload = json.loads(raw)
    assert payload["success"] is True
    assert payload["mode"] == "search_completion"
    assert payload["result"]["answer"] == "Refund window is 7 days."
    assert payload["result"]["events"] == 2
    assert payload["result"]["reference"] == [{"doc_name": "a"}]
    assert payload["result"]["raw"] == {}


def test_ragflow_completion_falls_back_to_retrieval_test_on_404(monkeypatch):
    search_id = "search-456"
    base = "http://ragflow.local"

    class _FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def post(self, url, json=None, headers=None):
            if url == f"{base}/api/v1/searches/{search_id}/completion":
                return _FakeResponse(status_code=404, url=url, text="Not Found")
            if url == f"{base}/v1/chunk/retrieval_test":
                return _FakeResponse(
                    status_code=200,
                    url=url,
                    json_body={
                        "code": 0,
                        "data": {
                            "chunks": [
                                {
                                    "chunk_id": "c1",
                                    "doc_id": "d1",
                                    "docnm_kwd": "policy.md",
                                    "kb_id": "kb1",
                                    "content_with_weight": "Premium plan refund window is 7 days from payment date.",
                                    "similarity": 0.99,
                                }
                            ]
                        },
                    },
                )
            raise AssertionError(f"Unexpected POST url: {url}")

        def get(self, url, headers=None):
            assert url == f"{base}/api/v1/searches/{search_id}"
            return _FakeResponse(
                status_code=200,
                url=url,
                method="GET",
                json_body={
                    "code": 0,
                    "data": {
                        "search_config": {
                            "kb_ids": ["kb1"],
                        }
                    },
                },
            )

    monkeypatch.setattr(ragflow_tool.httpx, "Client", _FakeClient)

    raw = ragflow_tool.ragflow_completion(
        question="What is refund window?",
        search_id=search_id,
        base_url=base,
        api_token="tok",
    )
    payload = json.loads(raw)
    assert payload["success"] is True
    assert payload["mode"] == "retrieval_test_fallback"
    assert payload["result"]["reference"][0] == {
        "doc_name": "policy.md",
        "doc_id": "d1",
        "chunk_id": "c1",
        "dataset_id": "kb1",
    }
    assert "retrieval results only" in payload["result"]["warning"]
    assert "7 days" in payload["result"]["answer"]
    assert "similarity" not in payload["result"]["reference"][0]
    assert "content" not in payload["result"]["reference"][0]
    assert payload["result"]["raw"] == {}
#2027-04-28-zty-end
