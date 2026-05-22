def test_list_chats_empty(client) -> None:
    response = client.get("/chats")
    assert response.status_code == 200
    assert response.json()["items"] == []


def test_create_chat_and_send_message(client) -> None:
    create = client.post("/chats", json={"channel": "web"})
    assert create.status_code == 201
    chat_id = create.json()["chat_id"]

    messages = client.get(f"/chats/{chat_id}/messages")
    assert messages.status_code == 200
    assert messages.json()["messages"] == []

    send = client.post(
        f"/chats/{chat_id}/messages",
        json={"content": "Olá", "model": "test-model"},
    )
    assert send.status_code == 200
    body = send.json()
    assert body["chat_id"] == chat_id
    assert body["user_message"]["content"] == "Olá"
    assert body["assistant_message"]["content"] == "resposta mock"


def test_unknown_chat_returns_404(client) -> None:
    response = client.post(
        "/chats/00000000-0000-0000-0000-000000000099/messages",
        json={"content": "x", "model": "test-model"},
    )
    assert response.status_code == 404
