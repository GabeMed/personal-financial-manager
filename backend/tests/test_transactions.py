import time

from tests.conftest import API


def test_create_transaction_updates_balance(
    alice, make_category, make_transaction, balance
):
    food = make_category(alice)

    tx = make_transaction(alice, food["id"], type="expense", amount="12.50")
    make_transaction(alice, food["id"], type="income", amount="100")

    assert tx["amount"] == 12.5
    assert tx["category"] == {"id": food["id"], "name": "Food"}
    assert balance(alice) == 87.5


def test_default_date_is_set_per_request(alice, make_category, make_transaction):
    food = make_category(alice)

    first = make_transaction(alice, food["id"])
    time.sleep(0.01)
    second = make_transaction(alice, food["id"])

    assert first["date"] != second["date"]


def test_amount_must_be_positive_with_two_decimals(client, alice, make_category):
    food = make_category(alice)
    for amount in ("0", "-5", "1.234"):
        response = client.post(
            f"{API}/transactions",
            json={"type": "expense", "amount": amount, "category_id": food["id"]},
            headers=alice,
        )
        assert response.status_code == 422, amount


def test_type_must_be_income_or_expense(client, alice, make_category):
    food = make_category(alice)
    response = client.post(
        f"{API}/transactions",
        json={"type": "gift", "amount": "5", "category_id": food["id"]},
        headers=alice,
    )

    assert response.status_code == 422


def test_cannot_use_another_users_category(client, alice, bob, make_category):
    alices_food = make_category(alice)

    response = client.post(
        f"{API}/transactions",
        json={"type": "expense", "amount": "5", "category_id": alices_food["id"]},
        headers=bob,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"


def test_list_returns_only_own_transactions_newest_first(
    client, alice, bob, make_category, make_transaction
):
    food = make_category(alice)
    make_transaction(alice, food["id"], description="old", date="2025-01-01T10:00:00")
    make_transaction(alice, food["id"], description="new", date="2025-03-01T10:00:00")
    make_transaction(alice, food["id"], description="mid", date="2025-02-01T10:00:00")
    make_transaction(bob, make_category(bob)["id"], description="bob's")

    response = client.get(f"{API}/transactions/all", headers=alice)

    assert [t["description"] for t in response.json()] == ["new", "mid", "old"]


def test_list_is_paginated(client, alice, make_category, make_transaction):
    food = make_category(alice)
    for i in range(5):
        make_transaction(alice, food["id"], description=str(i))

    page = client.get(f"{API}/transactions/all?skip=1&limit=2", headers=alice).json()

    assert len(page) == 2
    assert (
        client.get(f"{API}/transactions/all?limit=0", headers=alice).status_code == 422
    )


def test_patch_amount_adjusts_balance(
    client, alice, make_category, make_transaction, balance
):
    food = make_category(alice)
    tx = make_transaction(alice, food["id"], type="expense", amount="30")

    response = client.patch(
        f"{API}/transactions/{tx['id']}", json={"amount": "50"}, headers=alice
    )

    assert response.status_code == 200
    assert response.json()["amount"] == 50
    assert balance(alice) == -50


def test_patch_without_amount_keeps_amount(
    client, alice, make_category, make_transaction, balance
):
    food = make_category(alice)
    tx = make_transaction(alice, food["id"], type="expense", amount="30")

    response = client.patch(
        f"{API}/transactions/{tx['id']}",
        json={"description": "lunch"},
        headers=alice,
    )

    assert response.status_code == 200
    assert response.json()["description"] == "lunch"
    assert response.json()["amount"] == 30
    assert balance(alice) == -30


def test_patch_type_flip_adjusts_balance(
    client, alice, make_category, make_transaction, balance
):
    food = make_category(alice)
    make_transaction(alice, food["id"], type="expense", amount="10")
    tx = make_transaction(alice, food["id"], type="income", amount="100")
    assert balance(alice) == 90

    response = client.patch(
        f"{API}/transactions/{tx['id']}", json={"type": "expense"}, headers=alice
    )

    assert response.status_code == 200
    assert balance(alice) == -110


def test_patch_can_move_to_own_category_only(
    client, alice, bob, make_category, make_transaction
):
    food = make_category(alice, "Food")
    rent = make_category(alice, "Rent")
    bobs = make_category(bob, "Bob's")
    tx = make_transaction(alice, food["id"])

    moved = client.patch(
        f"{API}/transactions/{tx['id']}",
        json={"category_id": rent["id"]},
        headers=alice,
    )
    stolen = client.patch(
        f"{API}/transactions/{tx['id']}",
        json={"category_id": bobs["id"]},
        headers=alice,
    )

    assert moved.json()["category"]["name"] == "Rent"
    assert stolen.status_code == 404


def test_patch_rejects_null_for_required_fields(
    client, alice, make_category, make_transaction
):
    food = make_category(alice)
    tx = make_transaction(alice, food["id"])

    for field in ("type", "amount", "date", "category_id"):
        response = client.patch(
            f"{API}/transactions/{tx['id']}", json={field: None}, headers=alice
        )
        assert response.status_code == 422, field

    cleared = client.patch(
        f"{API}/transactions/{tx['id']}", json={"description": None}, headers=alice
    )
    assert cleared.status_code == 200


def test_delete_restores_balance(
    client, alice, make_category, make_transaction, balance
):
    food = make_category(alice)
    make_transaction(alice, food["id"], type="income", amount="100")
    tx = make_transaction(alice, food["id"], type="expense", amount="40")

    response = client.delete(f"{API}/transactions/{tx['id']}", headers=alice)

    assert response.status_code == 204
    assert balance(alice) == 100
    assert len(client.get(f"{API}/transactions/all", headers=alice).json()) == 1


def test_other_users_transactions_are_not_found(
    client, alice, bob, make_category, make_transaction, balance
):
    tx = make_transaction(alice, make_category(alice)["id"], amount="10")

    patch = client.patch(
        f"{API}/transactions/{tx['id']}", json={"amount": "1"}, headers=bob
    )
    delete = client.delete(f"{API}/transactions/{tx['id']}", headers=bob)

    assert patch.status_code == 404
    assert delete.status_code == 404
    assert balance(alice) == -10


def test_unknown_transaction_is_not_found(client, alice):
    assert client.delete(f"{API}/transactions/999", headers=alice).status_code == 404
