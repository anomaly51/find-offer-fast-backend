import pytest

from app.sockets import connect
from tests.conftest import _session_maker, reg_and_login


@pytest.mark.asyncio
async def test_socket_rejects_access_token_after_logout(async_client, monkeypatch):
    session = await reg_and_login(async_client)
    entered_rooms: list[tuple[str, str]] = []

    async def enter_room(sid: str, room: str) -> None:
        entered_rooms.append((sid, room))

    monkeypatch.setattr("app.sockets.SessionLocal", _session_maker)
    monkeypatch.setattr("app.sockets.sio.enter_room", enter_room)

    connected = await connect("socket-id", {}, {"token": session["access_token"]})
    assert connected is None
    assert entered_rooms == [("socket-id", f"user_{session['id']}")]

    logout = await async_client.post(
        "/auth/logout",
        headers=session["headers"],
        json={"refresh_token": session["refresh_token"]},
    )
    assert logout.status_code == 200

    rejected = await connect("revoked-socket", {}, {"token": session["access_token"]})
    assert rejected is False
    assert entered_rooms == [("socket-id", f"user_{session['id']}")]
