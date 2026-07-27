def test_metrics_rejects_missing_and_wrong_tokens(client):
    assert client.get("/metrics").status_code == 403
    assert client.get("/metrics", headers={"X-Metrics-Token": "wrong"}).status_code == 403
    assert client.get("/metrics", headers={"Authorization": "Bearer wrong"}).status_code == 403


def test_metrics_accepts_legacy_header(client):
    response = client.get("/metrics", headers={"X-Metrics-Token": "test-metrics-token"})
    assert response.status_code == 200
    assert "alo186_http_requests_total" in response.text


def test_metrics_accepts_bearer_for_grafana_alloy(client):
    response = client.get(
        "/metrics",
        headers={"Authorization": "Bearer test-metrics-token"},
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert "alo186_uptime_seconds" in response.text
