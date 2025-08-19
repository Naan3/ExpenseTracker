import json
import os
from datetime import datetime
from tabulate import tabulate
from colorama import Fore, Style
import pandas as pd
import matplotlib.pyplot as plt


DATA_FILE = "expenses.json"

# ----------------- Data Handling -----------------
def load_expenses():
    # Check if the expenses file exists; if not, return an empty list
    if not os.path.exists(DATA_FILE):
        return []
    try:
        # Open the file and read its content
        with open(DATA_FILE, "r") as file:
            content = file.read().strip()  # Remove leading/trailing whitespace
            # If the file is empty, return an empty list
            if not content:
                return []
            # Parse JSON content and return it as a Python list of dicts
            return json.loads(content)
    except json.JSONDecodeError:
        # Handle case where JSON is invalid/corrupted
        print(Fore.RED + "⚠️ Corrupted expenses file. Starting fresh." + Style.RESET_ALL)
        return []  # Return an empty list so the program can continue


def save_expenses(expenses):
    with open(DATA_FILE, "w") as file:
        json.dump(expenses, file, indent=4)

# ----------------- Features -----------------

def search(expenses): # allows user to search through their expenses using the category they saved it under
    if not expenses:
        print(Fore.YELLOW + "No expenses found." + Style.RESET_ALL)
        return
    else:
        dict_of_categories = {}
        for e in expenses:
            # initialize the count for this category (set to 0)
            dict_of_categories[e['category'].lower()] = 0
            # loop through all expenses again to count how many belong to this category
            for x in expenses:
                if e["category"].lower() == x['category'].lower():
                    dict_of_categories[e['category'].lower()] += 1  # increment the count
        # after counting, print each category with its total number of expenses
        for i in dict_of_categories:
            print(f"{i}: {dict_of_categories[i]}")
        category_choice = input("please choose a category to view: ").lower()
        filtered_expenses = [
            expense.copy()  # makes a shallow copy of each expense (so we don't modify the original dicts)
            for expense in expenses  # loops through all expenses
            if expense["category"].lower() == category_choice # only keeps expenses where the category matches the user's choice
        ]
        view_expenses(filtered_expenses)




def add_expense(expenses):
    try:
        amount = float(input("Enter amount: £"))
        category = input("Enter category (e.g., Food, Travel, Bills): ").strip()
        description = input("Enter description: ").strip()
        date_input = input("Enter date (YYYY-MM-DD) or leave blank for today: ").strip()
        date = date_input if date_input else datetime.now().strftime("%Y-%m-%d")

        expense = {
            "id": len(expenses) + 1,
            "amount": amount,
            "category": category,
            "description": description,
            "date": date
        }
        expenses.append(expense)
        print(Fore.GREEN + "✅ Expense added successfully!" + Style.RESET_ALL)
    except ValueError:
        print(Fore.RED + "❌ Invalid amount entered!" + Style.RESET_ALL)

def view_expenses(expenses):
    if not expenses:
        print(Fore.YELLOW + "No expenses found." + Style.RESET_ALL)
        return
    # Create a 2D list (table) where each sublist represents one expense
    table = [[e["id"], f"£{e['amount']:.2f}", e["category"], e["description"], e["date"]] for e in expenses]
    print(tabulate(table, headers=["ID", "Amount", "Category", "Description", "Date"], tablefmt="grid"))

def view_summary(expenses):
    if not expenses:
        print(Fore.YELLOW + "No expenses to summarize." + Style.RESET_ALL)
        return
    # Calculate total amount spent
    total = sum(e["amount"] for e in expenses)
    # Calculate total spent per category
    category_totals = {}
    for e in expenses:
        category_totals[e["category"]] = category_totals.get(e["category"], 0) + e["amount"]
    # Display overall total
    print(Fore.CYAN + f"💰 Total spent: £{total:.2f}" + Style.RESET_ALL)
    # Display totals per category
    for category, amount in category_totals.items():
        print(f" - {category}: £{amount:.2f}")


def delete_expense(expenses):
    try:
        # Ask user for the ID of the expense to delete
        expense_id = int(input("Enter ID of expense to delete: "))
        # Search for the expense and remove it
        for e in expenses:
            if e["id"] == expense_id:
                expenses.remove(e)
                print(Fore.GREEN + "✅ Expense deleted." + Style.RESET_ALL)
                return
        # If no matching ID was found
        print(Fore.RED + "❌ Expense not found." + Style.RESET_ALL)
    except ValueError:
        # Handle non-integer input
        print(Fore.RED + "❌ Invalid ID!" + Style.RESET_ALL)


def view_charts(expenses):
    if not expenses:
        print(Fore.YELLOW + "No expenses to display charts." + Style.RESET_ALL)
        return

    # Spending by category
    category_totals = {}
    for e in expenses:
        category_totals[e["category"]] = category_totals.get(e["category"], 0) + e["amount"]

    categories = list(category_totals.keys())
    amounts = list(category_totals.values())

    plt.figure(figsize=(8, 5))
    plt.bar(categories, amounts, color='skyblue')
    plt.title("Spending by Category")
    plt.ylabel("Amount (£)")
    plt.xlabel("Category")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def export_to_excel(expenses):
    while True:
        # Ask user for the month in MM format
        month = input("Enter the month of which expenses you would like to export (MM): ")
        # Validate input: must be digits, exactly 2 characters, and between 01–12
        if month.isdigit() and len(month) == 2 and 1 <= int(month) <= 12:
            expenses_of_specific_month = []  # list to store only expenses from that month
            # Loop through all expenses
            for e in expenses:
                # Check if the month in the expense date matches the user input
                if e["date"][5:7] == str(month):
                    expenses_of_specific_month.append(e)  # add to the filtered list
            # Convert filtered expenses to DataFrame
            df = pd.DataFrame(expenses_of_specific_month)
            # Export DataFrame to an Excel file
            df.to_excel('expenses.xlsx', index=False)
            break  # exit the loop once done
        else:
            # Print error message if input is invalid
            print(Fore.RED + "Please enter a valid 2-digit month between 01 and 12." + Style.RESET_ALL)


# ----------------- Main Menu -----------------
def main():
    expenses = load_expenses()

    while True:
        print("\n" + Fore.BLUE + "=== Expense Tracker ===" + Style.RESET_ALL)
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. View Summary")
        print("4. Delete Expense")
        print("5. Export to excel")
        print("6. Search by category")
        print("7. View Charts")
        print("8. Exit")

        choice = input("Choose an option (1-8): ").strip()

        if choice == "1":
            add_expense(expenses)
            save_expenses(expenses)
        elif choice == "2":
            view_expenses(expenses)
        elif choice == "3":
            view_summary(expenses)
        elif choice == "4":
            delete_expense(expenses)
            save_expenses(expenses)
        elif choice == "5":
            export_to_excel(expenses)
        elif choice == "6":
            search(expenses)
        elif choice == "7":
            view_charts(expenses)
        elif choice == "8":
            save_expenses(expenses)
            print(Fore.MAGENTA + "Goodbye! 👋" + Style.RESET_ALL)
            break
        else:
            print(Fore.RED + "❌ Invalid choice!" + Style.RESET_ALL)

if __name__ == "__main__":
    main()
