from datetime import date

from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.models.budget import Budget


class FinanceRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_transaction(
        self,
        user_id: str,
        amount: float,
        transaction_type: str,
        category: str,
        transaction_date: date,
        description: str | None = None,
    ) -> Transaction:
        transaction = Transaction(
            user_id=user_id,
            amount=amount,
            transaction_type=transaction_type,
            category=category,
            description=description,
            transaction_date=transaction_date,
        )
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def get_transaction(self, transaction_id: str, user_id: str) -> Transaction | None:
        return self.db.query(Transaction).filter(
            Transaction.id == transaction_id,
            Transaction.user_id == user_id,
        ).first()

    def update_transaction(self, transaction: Transaction, **kwargs) -> Transaction:
        for key, value in kwargs.items():
            if value is not None:
                setattr(transaction, key, value)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def get_transactions(
        self,
        user_id: str,
        start_date: date | None = None,
        end_date: date | None = None,
        category: str | None = None,
        transaction_type: str | None = None,
    ) -> list[Transaction]:
        query = self.db.query(Transaction).filter(Transaction.user_id == user_id)
        if start_date:
            query = query.filter(Transaction.transaction_date >= start_date)
        if end_date:
            query = query.filter(Transaction.transaction_date <= end_date)
        if category:
            query = query.filter(Transaction.category.ilike(category))
        if transaction_type:
            query = query.filter(Transaction.transaction_type == transaction_type)
        return query.order_by(Transaction.transaction_date.desc()).all()

    def create_budget(
        self,
        user_id: str,
        amount: float,
        start_date: date,
        end_date: date,
    ) -> Budget:
        # deactivate any existing active budget
        self.db.query(Budget).filter(
            Budget.user_id == user_id,
            Budget.is_active == True,
        ).update({"is_active": False})

        budget = Budget(
            user_id=user_id,
            amount=amount,
            start_date=start_date,
            end_date=end_date,
            is_active=True,
        )
        self.db.add(budget)
        self.db.commit()
        self.db.refresh(budget)
        return budget

    def get_active_budget(self, user_id: str) -> Budget | None:
        return self.db.query(Budget).filter(
            Budget.user_id == user_id,
            Budget.is_active == True,
        ).first()

    def update_budget(self, budget: Budget, **kwargs) -> Budget:
        for key, value in kwargs.items():
            if value is not None:
                setattr(budget, key, value)
        self.db.commit()
        self.db.refresh(budget)
        return budget
