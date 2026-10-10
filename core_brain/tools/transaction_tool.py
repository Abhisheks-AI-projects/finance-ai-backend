from datetime import date

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from app.db.postgres import SessionLocal
from app.repositories.finance_repository import FinanceRepository


class CreateTransactionInput(BaseModel):
    amount: float = Field(description="Transaction amount, must be greater than 0")
    transaction_type: str = Field(description="Either 'income' or 'expense'")
    category: str = Field(description="Category like 'food', 'salary', 'rent', etc.")
    description: str | None = Field(default=None, description="Optional description")
    transaction_date: str = Field(description="Date in YYYY-MM-DD format")


class UpdateTransactionInput(BaseModel):
    transaction_id: str = Field(description="The UUID of the transaction to update")
    amount: float | None = Field(default=None, description="New amount")
    transaction_type: str | None = Field(default=None, description="New type: 'income' or 'expense'")
    category: str | None = Field(default=None, description="New category")
    description: str | None = Field(default=None, description="New description")
    transaction_date: str | None = Field(default=None, description="New date in YYYY-MM-DD format")


class GetTransactionsInput(BaseModel):
    start_date: str | None = Field(default=None, description="Filter from date in YYYY-MM-DD format")
    end_date: str | None = Field(default=None, description="Filter to date in YYYY-MM-DD format")
    category: str | None = Field(default=None, description="Filter by category")
    transaction_type: str | None = Field(default=None, description="Filter by 'income' or 'expense'")


def make_transaction_tools(user_id: str):

    @tool(args_schema=CreateTransactionInput)
    def create_transaction(
        amount: float,
        transaction_type: str,
        category: str,
        transaction_date: str,
        description: str | None = None,
    ) -> str:
        """Create a new transaction entry (income or expense) in the database."""
        if transaction_type not in ("income", "expense"):
            return "Error: transaction_type must be 'income' or 'expense'"

        if amount <= 0:
            return "Error: amount must be greater than 0"

        db = SessionLocal()
        try:
            repo = FinanceRepository(db)
            transaction = repo.create_transaction(
                user_id=user_id,
                amount=amount,
                transaction_type=transaction_type,
                category=category,
                description=description,
                transaction_date=date.fromisoformat(transaction_date),
            )

            return (
                f"Transaction created successfully! "
                f"ID: {transaction.id},"
                f"Type: {transaction_type}, "
                f"Amount: {amount}, "
                f"Category: {category}, "
                f"Date: {transaction_date}"
            )
        except Exception as e:
            db.rollback()
            return f"Error creating transaction: {str(e)}"
        finally:
            db.close()

    @tool(args_schema=UpdateTransactionInput)
    def update_transaction(
        transaction_id: str,
        amount: float | None = None,
        transaction_type: str | None = None,
        category: str | None = None,
        description: str | None = None,
        transaction_date: str | None = None,
    ) -> str:
        """Update an existing transaction. Only the provided fields will be changed."""
        if transaction_type is not None and transaction_type not in ("income", "expense"):
            return "Error: transaction_type must be 'income' or 'expense'"

        if amount is not None and amount <= 0:
            return "Error: amount must be greater than 0"

        db = SessionLocal()
        try:
            repo = FinanceRepository(db)
            transaction = repo.get_transaction(transaction_id, user_id)
            if not transaction:
                return "Error: transaction not found"

            updates = {}
            if amount is not None:
                updates["amount"] = amount
            if transaction_type is not None:
                updates["transaction_type"] = transaction_type
            if category is not None:
                updates["category"] = category
            if description is not None:
                updates["description"] = description
            if transaction_date is not None:
                updates["transaction_date"] = date.fromisoformat(transaction_date)

            updated = repo.update_transaction(transaction, **updates)

            return (
                f"Transaction updated successfully! "
                f"Type: {updated.transaction_type}, "
                f"Amount: {updated.amount}, "
                f"Category: {updated.category}, "
                f"Date: {updated.transaction_date}"
            )
        except Exception as e:
            db.rollback()
            return f"Error updating transaction: {str(e)}"
        finally:
            db.close()

    @tool(args_schema=GetTransactionsInput)
    def get_transactions(
        start_date: str | None = None,
        end_date: str | None = None,
        category: str | None = None,
        transaction_type: str | None = None,
    ) -> str:
        """Get user's transactions with optional filters by date range, category, or type."""
        db = SessionLocal()
        try:
            repo = FinanceRepository(db)
            transactions = repo.get_transactions(
                user_id=user_id,
                start_date=date.fromisoformat(start_date) if start_date else None,
                end_date=date.fromisoformat(end_date) if end_date else None,
                category=category,
                transaction_type=transaction_type,
            )

            if not transactions:
                return "No transactions found."

            lines = []
            for t in transactions:
                lines.append(
                    f"ID: {t.id}, Type: {t.transaction_type}, "
                    f"Amount: {t.amount}, Category: {t.category}, "
                    f"Date: {t.transaction_date}, Description: {t.description or 'N/A'}"
                )
            return "\n".join(lines)
        except Exception as e:
            return f"Error fetching transactions: {str(e)}"
        finally:
            db.close()

    return [create_transaction, update_transaction, get_transactions]
