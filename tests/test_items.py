ITEM = {"sku": "abc-1", "name": "Desk lamp", "quantity": 3, "price": 500, "reorder_level": 5}


def test_admin_item_crud(client, admin_headers):
    res = client.post("/api/items", json=ITEM, headers=admin_headers)
    assert res.status_code == 201
    item = res.json()
    assert item["sku"] == "ABC-1"  # normalised to upper case

    upd = client.put(f"/api/items/{item['id']}", json={"quantity": 50}, headers=admin_headers)
    assert upd.json()["quantity"] == 50
    assert client.delete(f"/api/items/{item['id']}", headers=admin_headers).status_code == 204
    assert client.get(f"/api/items/{item['id']}", headers=admin_headers).status_code == 404


def test_duplicate_sku(client, admin_headers):
    assert client.post("/api/items", json=ITEM, headers=admin_headers).status_code == 201
    assert client.post("/api/items", json=ITEM, headers=admin_headers).status_code == 409


def test_regular_user_is_read_only(client, admin_headers, user_headers):
    created = client.post("/api/items", json=ITEM, headers=admin_headers).json()
    assert client.get("/api/items", headers=user_headers).status_code == 200
    assert client.post("/api/items", json={**ITEM, "sku": "zzz"}, headers=user_headers).status_code == 403
    assert client.put(f"/api/items/{created['id']}", json={"quantity": 1}, headers=user_headers).status_code == 403
    assert client.delete(f"/api/items/{created['id']}", headers=user_headers).status_code == 403


def test_item_validation(client, admin_headers):
    assert client.post("/api/items", json={**ITEM, "quantity": -1}, headers=admin_headers).status_code == 422
    assert client.post("/api/items", json={**ITEM, "price": -5}, headers=admin_headers).status_code == 422
    assert client.post("/api/items", json={**ITEM, "sku": "bad sku"}, headers=admin_headers).status_code == 422


def test_summary_search_and_low_stock(client, admin_headers):
    client.post("/api/items", json=ITEM, headers=admin_headers)  # low stock: 3 <= 5
    client.post("/api/items", json={**ITEM, "sku": "xyz-2", "name": "Chair", "quantity": 20, "price": 100}, headers=admin_headers)

    s = client.get("/api/items/summary", headers=admin_headers).json()
    assert s == {"skus": 2, "units": 23, "stock_value": 3500.0, "low_stock": 1}

    low = client.get("/api/items?low_stock=true", headers=admin_headers).json()
    assert low["total"] == 1 and low["items"][0]["sku"] == "ABC-1"
    assert client.get("/api/items?q=chair", headers=admin_headers).json()["total"] == 1
