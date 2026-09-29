from tests.conftest import API


def test_create_and_list_categories(client, alice, make_category):
    make_category(alice, "Rent")
    make_category(alice, "Food")

    response = client.get(f"{API}/categories/all", headers=alice)

    assert response.status_code == 200
    assert [c["name"] for c in response.json()] == ["Food", "Rent"]


def test_categories_are_scoped_to_their_owner(client, alice, bob, make_category):
    make_category(alice, "Food")

    assert client.get(f"{API}/categories/all", headers=bob).json() == []


def test_duplicate_category_name_is_rejected(client, alice, make_category):
    make_category(alice, "Food")

    response = client.post(f"{API}/categories", json={"name": " food "}, headers=alice)

    assert response.status_code == 409


def test_same_category_name_is_allowed_for_different_users(alice, bob, make_category):
    make_category(alice, "Food")
    make_category(bob, "Food")


def test_category_name_is_validated(client, alice):
    for name in ("", "   ", "x" * 51):
        response = client.post(f"{API}/categories", json={"name": name}, headers=alice)
        assert response.status_code == 422


def test_category_name_is_trimmed(alice, make_category):
    assert make_category(alice, "  Travel ")["name"] == "Travel"
