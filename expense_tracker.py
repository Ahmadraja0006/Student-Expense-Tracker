"""
Student Expense Tracker
Author: Ahmad Raja Ansari
Description: A console-based expense tracking application that allows students
             to manage their daily expenses with category-wise analysis and
             monthly summaries. Data is persisted using JSON file storage.
"""

import json
import os
from datetime import datetime


# ─── Constants ────────────────────────────────────────────────────────────────

DATA_FILE = "expenses.json"

CATEGORIES = [
    "Food",
    "Transport",
    "Education",
    "Entertainment",
    "Health",
    "Shopping",
    "Other"
]


# ─── Data Layer ───────────────────────────────────────────────────────────────

def load_expenses():
    """Load expenses from the JSON file. Returns an empty list if file doesn't exist."""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_expenses(expenses):
    """Save the expenses list to the JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(expenses, f, indent=4)


# ─── Core Features ────────────────────────────────────────────────────────────

def add_expense(expenses):
    """Prompt user to enter a new expense and add it to the list."""
    print("\n─── Add New Expense ───")

    # Get amount
    while True:
        try:
            amount = float(input("Enter amount (₹): "))
            if amount <= 0:
                print("  Amount must be greater than 0.")
                continue
            break
        except ValueError:
            print("  Invalid input. Please enter a number.")

    # Get category
    print("\nCategories:")
    for i, cat in enumerate(CATEGORIES, 1):
        print(f"  {i}. {cat}")
    while True:
        try:
            choice = int(input("Choose category (1-7): "))
            if 1 <= choice <= len(CATEGORIES):
                category = CATEGORIES[choice - 1]
                break
            else:
                print(f"  Please enter a number between 1 and {len(CATEGORIES)}.")
        except ValueError:
            print("  Invalid input. Please enter a number.")

    # Get description
    description = input("Enter description (e.g., Lunch at canteen): ").strip()
    if not description:
        description = "No description"

    # Get date
    date_input = input("Enter date (DD-MM-YYYY) or press Enter for today: ").strip()
    if not date_input:
        date = datetime.today().strftime("%d-%m-%Y")
    else:
        try:
            datetime.strptime(date_input, "%d-%m-%Y")
            date = date_input
        except ValueError:
            print("  Invalid date format. Using today's date.")
            date = datetime.today().strftime("%d-%m-%Y")

    # Build and save the expense record
    expense = {
        "id": len(expenses) + 1,
        "amount": amount,
        "category": category,
        "description": description,
        "date": date
    }
    expenses.append(expense)
    save_expenses(expenses)
    print(f"\n  ✓ Expense of ₹{amount:.2f} added under '{category}'.")


def view_all_expenses(expenses):
    """Display all expenses in a formatted table."""
    print("\n─── All Expenses ───")
    if not expenses:
        print("  No expenses recorded yet. Start by adding one!")
        return

    print(f"\n  {'ID':<5} {'Date':<14} {'Category':<15} {'Amount':>10}  Description")
    print("  " + "─" * 65)
    for e in expenses:
        print(f"  {e['id']:<5} {e['date']:<14} {e['category']:<15} ₹{e['amount']:>9.2f}  {e['description']}")

    total = sum(e["amount"] for e in expenses)
    print("  " + "─" * 65)
    print(f"  {'Total':<35} ₹{total:>9.2f}")


def monthly_summary(expenses):
    """Show a summary of expenses grouped by month."""
    print("\n─── Monthly Summary ───")
    if not expenses:
        print("  No expenses to summarize.")
        return

    monthly = {}
    for e in expenses:
        # Parse month-year key from date string (DD-MM-YYYY)
        month_key = e["date"][3:]  # "MM-YYYY"
        monthly.setdefault(month_key, []).append(e)

    for month, records in sorted(monthly.items(), key=lambda x: datetime.strptime(x[0], "%m-%Y")):
        month_name = datetime.strptime(month, "%m-%Y").strftime("%B %Y")
        total = sum(r["amount"] for r in records)
        print(f"\n  📅 {month_name}  —  Total: ₹{total:.2f}  ({len(records)} expense{'s' if len(records) > 1 else ''})")

        # Category breakdown
        cat_totals = {}
        for r in records:
            cat_totals[r["category"]] = cat_totals.get(r["category"], 0) + r["amount"]

        for cat, amt in sorted(cat_totals.items(), key=lambda x: -x[1]):
            bar_len = int((amt / total) * 20)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            print(f"    {cat:<15} {bar}  ₹{amt:.2f}")


def category_summary(expenses):
    """Show total spending per category across all time."""
    print("\n─── Spending by Category ───")
    if not expenses:
        print("  No expenses recorded.")
        return

    cat_totals = {}
    for e in expenses:
        cat_totals[e["category"]] = cat_totals.get(e["category"], 0) + e["amount"]

    total = sum(cat_totals.values())
    print(f"\n  {'Category':<18} {'Amount':>10}   {'% Share':<10}")
    print("  " + "─" * 45)
    for cat, amt in sorted(cat_totals.items(), key=lambda x: -x[1]):
        pct = (amt / total) * 100
        print(f"  {cat:<18} ₹{amt:>9.2f}   {pct:.1f}%")
    print("  " + "─" * 45)
    print(f"  {'Total':<18} ₹{total:>9.2f}")


def delete_expense(expenses):
    """Delete an expense by its ID."""
    print("\n─── Delete Expense ───")
    if not expenses:
        print("  No expenses to delete.")
        return

    view_all_expenses(expenses)
    while True:
        try:
            exp_id = int(input("\nEnter the ID of the expense to delete (0 to cancel): "))
            if exp_id == 0:
                print("  Cancelled.")
                return
            match = next((e for e in expenses if e["id"] == exp_id), None)
            if match:
                confirm = input(f"  Delete ₹{match['amount']} — {match['description']}? (y/n): ").lower()
                if confirm == "y":
                    expenses.remove(match)
                    save_expenses(expenses)
                    print("  ✓ Expense deleted.")
                else:
                    print("  Cancelled.")
                return
            else:
                print(f"  No expense found with ID {exp_id}.")
        except ValueError:
            print("  Invalid input. Please enter a number.")


def search_expenses(expenses):
    """Search expenses by category or keyword in description."""
    print("\n─── Search Expenses ───")
    if not expenses:
        print("  No expenses to search.")
        return

    print("  1. Search by category")
    print("  2. Search by keyword in description")
    choice = input("  Choose (1/2): ").strip()

    if choice == "1":
        print("\nCategories:", ", ".join(CATEGORIES))
        keyword = input("  Enter category: ").strip().capitalize()
        results = [e for e in expenses if e["category"].lower() == keyword.lower()]
    elif choice == "2":
        keyword = input("  Enter keyword: ").strip()
        results = [e for e in expenses if keyword.lower() in e["description"].lower()]
    else:
        print("  Invalid choice.")
        return

    if not results:
        print(f"  No expenses found.")
    else:
        print(f"\n  Found {len(results)} result(s):\n")
        print(f"  {'ID':<5} {'Date':<14} {'Category':<15} {'Amount':>10}  Description")
        print("  " + "─" * 65)
        for e in results:
            print(f"  {e['id']:<5} {e['date']:<14} {e['category']:<15} ₹{e['amount']:>9.2f}  {e['description']}")
        total = sum(e["amount"] for e in results)
        print(f"\n  Subtotal: ₹{total:.2f}")


# ─── Main Menu ────────────────────────────────────────────────────────────────

def main():
    """Main application loop."""
    print("\n" + "═" * 50)
    print("      💰 Student Expense Tracker")
    print("═" * 50)

    expenses = load_expenses()

    while True:
        print("\n  What would you like to do?")
        print("  1. Add expense")
        print("  2. View all expenses")
        print("  3. Monthly summary")
        print("  4. Category breakdown")
        print("  5. Search expenses")
        print("  6. Delete an expense")
        print("  7. Exit")

        choice = input("\n  Enter choice (1-7): ").strip()

        if choice == "1":
            add_expense(expenses)
        elif choice == "2":
            view_all_expenses(expenses)
        elif choice == "3":
            monthly_summary(expenses)
        elif choice == "4":
            category_summary(expenses)
        elif choice == "5":
            search_expenses(expenses)
        elif choice == "6":
            delete_expense(expenses)
        elif choice == "7":
            print("\n  Goodbye! Track your spending wisely. 👋\n")
            break
        else:
            print("  Invalid choice. Please enter a number between 1 and 7.")


if __name__ == "__main__":
    main()