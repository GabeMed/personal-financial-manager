from datetime import date

from backend.app.services.summary_service import get_summary
from tests.conftest import API


def test_summary_of_new_user_is_empty(client, alice):
    response = client.get(f"{API}/transactions/summary", headers=alice)

    assert response.status_code == 200
    assert response.json() == {
        "balance": 0,
        "income_total": 0,
        "expense_total": 0,
        "income_porcentage_by_category": {},
        "expense_porcentage_by_category": {},
    }


def test_summary_groups_totals_and_percentages_by_category(
    client, alice, make_category, make_transaction
):
    salary = make_category(alice, "Salary")
    food = make_category(alice, "Food")
    rent = make_category(alice, "Rent")
    make_transaction(alice, salary["id"], type="income", amount="1000")
    make_transaction(alice, food["id"], type="expense", amount="100")
    make_transaction(alice, food["id"], type="expense", amount="50")
    make_transaction(alice, rent["id"], type="expense", amount="250")

    summary = client.get(f"{API}/transactions/summary", headers=alice).json()

    assert summary["balance"] == 600
    assert summary["income_total"] == 1000
    assert summary["expense_total"] == 400
    assert summary["income_porcentage_by_category"] == {str(salary["id"]): 100.0}
    assert summary["expense_porcentage_by_category"] == {
        str(food["id"]): 37.5,
        str(rent["id"]): 62.5,
    }


def test_summary_date_range_includes_the_end_day(
    client, alice, make_category, make_transaction
):
    food = make_category(alice)
    make_transaction(alice, food["id"], amount="1", date="2025-01-31T23:00:00")
    make_transaction(alice, food["id"], amount="2", date="2025-02-10T12:00:00")
    make_transaction(alice, food["id"], amount="4", date="2025-02-28T18:30:00")
    make_transaction(alice, food["id"], amount="8", date="2025-03-01T00:00:00")

    summary = client.get(
        f"{API}/transactions/summary?start=2025-02-01&end=2025-02-28", headers=alice
    ).json()

    assert summary["expense_total"] == 6


def test_summary_service_ignores_other_users(
    db, client, alice, bob, make_category, make_transaction
):
    make_transaction(alice, make_category(alice)["id"], type="income", amount="10")
    make_transaction(bob, make_category(bob)["id"], type="income", amount="99")
    alice_id = client.get(f"{API}/users/me", headers=alice).json()["id"]

    summary = get_summary(db, alice_id, date(2000, 1, 1), None)

    assert summary["income_total"] == 10
