def make_task(client, headers, **overrides):
    body = {"title": "Write report", "priority": "high", **overrides}
    res = client.post("/api/tasks", json=body, headers=headers)
    assert res.status_code == 201, res.text
    return res.json()


def test_task_crud(client, user_headers):
    task = make_task(client, user_headers)
    assert task["status"] == "todo"

    got = client.get(f"/api/tasks/{task['id']}", headers=user_headers)
    assert got.json()["title"] == "Write report"

    upd = client.put(f"/api/tasks/{task['id']}", json={"status": "done"}, headers=user_headers)
    assert upd.json()["status"] == "done" and upd.json()["title"] == "Write report"

    assert client.delete(f"/api/tasks/{task['id']}", headers=user_headers).status_code == 204
    assert client.get(f"/api/tasks/{task['id']}", headers=user_headers).status_code == 404


def test_task_validation(client, user_headers):
    assert client.post("/api/tasks", json={"title": ""}, headers=user_headers).status_code == 422
    assert client.post("/api/tasks", json={"title": "x", "status": "weird"}, headers=user_headers).status_code == 422
    assert client.post("/api/tasks", json={"title": "x", "due_date": "not-a-date"}, headers=user_headers).status_code == 422


def test_pagination_and_filters(client, user_headers):
    for i in range(12):
        make_task(client, user_headers, title=f"Task {i}", status="done" if i % 3 == 0 else "todo")

    first = client.get("/api/tasks?page=1&size=5", headers=user_headers).json()
    assert first["total"] == 12 and first["pages"] == 3 and len(first["items"]) == 5
    last = client.get("/api/tasks?page=3&size=5", headers=user_headers).json()
    assert len(last["items"]) == 2

    done = client.get("/api/tasks?status=done", headers=user_headers).json()
    assert done["total"] == 4
    found = client.get("/api/tasks?q=Task 7", headers=user_headers).json()
    assert found["total"] == 1
    assert client.get("/api/tasks?size=500", headers=user_headers).status_code == 422


def test_users_only_see_own_tasks(client, user_headers, other_headers, admin_headers):
    mine = make_task(client, user_headers, title="Mine")
    make_task(client, other_headers, title="Theirs")

    assert client.get("/api/tasks", headers=user_headers).json()["total"] == 1
    assert client.get(f"/api/tasks/{mine['id']}", headers=other_headers).status_code == 404
    assert client.put(f"/api/tasks/{mine['id']}", json={"title": "x"}, headers=other_headers).status_code == 404
    assert client.delete(f"/api/tasks/{mine['id']}", headers=other_headers).status_code == 404
    # admin sees everything
    assert client.get("/api/tasks", headers=admin_headers).json()["total"] == 2
