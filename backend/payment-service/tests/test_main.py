def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Payment Service is running!"}

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "payment-service"}
