from backend.app.crud.crud_user import get_user_by_username
from backend.app.seed import DEMO_TRANSACTIONS, DEMO_USERNAME, seed_demo_data


def test_seed_creates_consistent_demo_data_once(db):
    assert seed_demo_data(db) is True
    assert seed_demo_data(db) is False

    user = get_user_by_username(db, DEMO_USERNAME)
    expected = sum(
        float(amount) if type_ == "income" else -float(amount)
        for _, type_, amount, _, _ in DEMO_TRANSACTIONS
    )
    assert len(user.transactions) == len(DEMO_TRANSACTIONS)
    assert float(user.balance) == round(expected, 2)
