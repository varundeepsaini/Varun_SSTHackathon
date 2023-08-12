import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
import sqlite3


def get_table_names(cursor):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [table[0] for table in cursor.fetchall()]
    return tables


def query_database(root, cursor, table_name):
    cursor.execute(f'SELECT * FROM {table_name}')
    field_names = [i[0] for i in cursor.description]
    results = cursor.fetchall()
    display_table(root, table_name, field_names, results)
    messagebox.showinfo("Success", f"Displayed data from table '{table_name}'.")


def display_table(parent, table_name, field_names, results):
    top = tk.Toplevel(parent)
    top.title(table_name)
    tree = ttk.Treeview(top, columns=field_names)
    tree.pack()
    for i, field_name in enumerate(field_names):
        tree.heading(i, text=field_name)
        tree.column(i, width=100)
    for result in results:
        tree.insert('', 'end', values=result)


def run_custom_command(root, cursor, custom_command_entry):
    custom_command = custom_command_entry.get()
    cursor.execute(custom_command)
    field_names = [i[0] for i in cursor.description]
    results = cursor.fetchall()
    display_table(root, "Custom Command Result", field_names, results)
    messagebox.showinfo("Success", "Custom command executed successfully.")


def add_row_to_table(root, cursor, table_name, conn):
    top = tk.Toplevel(root)
    top.title(f'Add Row to {table_name}')
    cursor.execute(f'PRAGMA table_info({table_name})')
    field_info = cursor.fetchall()

    entries = []
    for i, field in enumerate(field_info):
        field_name = field[1]
        label = tk.Label(top, text=field_name)
        entry = tk.Entry(top)
        label.grid(row=i, column=0, padx=5, pady=5)
        entry.grid(row=i, column=1, padx=5, pady=5)
        entries.append(entry)

    def insert_row():
        values = [entry.get() for entry in entries]
        placeholders = ', '.join(['?'] * len(values))
        query = f'INSERT INTO {table_name} VALUES ({placeholders})'
        cursor.execute(query, values)
        conn.commit()
        top.destroy()
        messagebox.showinfo("Success", "Row added successfully.")

    button = tk.Button(top, text='Add Row', command=insert_row)
    button.grid(row=len(field_info), column=0, columnspan=2, padx=5, pady=5)


def delete_row_from_table(root, cursor, table_name, conn):
    cursor.execute(f'SELECT * FROM {table_name}')
    field_names = [i[0] for i in cursor.description]
    results = cursor.fetchall()
    if len(results) == 0:
        messagebox.showwarning("Warning", f"The table '{table_name}' is empty.")
    else:
        top = tk.Toplevel(root)
        top.title(f'Delete Row from {table_name}')
        tree = ttk.Treeview(top, columns=field_names, show='headings')
        tree.pack()
        for i, field_name in enumerate(field_names):
            tree.heading(i, text=field_name)
            tree.column(i, width=100)
        for result in results:
            tree.insert('', 'end', values=result)

        def delete_selected_row():
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showwarning("Warning", "Select a row to delete.")
            else:
                row_id = selected_item[0]
                values = tree.item(row_id, 'values')
                where_clause = ' AND '.join([f"{field}='{value}'" for field, value in zip(field_names, values)])
                delete_query = f"DELETE FROM {table_name} WHERE {where_clause}"
                cursor.execute(delete_query)
                conn.commit()
                top.destroy()
                messagebox.showinfo("Success", "Row deleted successfully.")

        delete_button = tk.Button(top, text='Delete Selected Row', command=delete_selected_row)
        delete_button.pack(pady=10)


def delete_column_from_table(root, cursor, table_name, conn):
    cursor.execute(f'PRAGMA table_info({table_name})')
    field_info = cursor.fetchall()

    if len(field_info) == 0:
        messagebox.showwarning("Warning", f"The table '{table_name}' is empty.")
        return

    top = tk.Toplevel(root)
    top.title(f'Delete Column from {table_name}')
    delete_column_label = tk.Label(top, text="Select column to delete:")
    delete_column_label.pack(pady=5)
    delete_column_var = tk.StringVar()
    delete_column_var.set(field_info[0][1])  # Default to the first column
    delete_column_option = ttk.OptionMenu(top, delete_column_var, *field_info)
    delete_column_option.pack(pady=5)

    def delete_selected_column():
        column_name = delete_column_var.get()
        delete_column_query = f"ALTER TABLE {table_name} DROP COLUMN {column_name}"
        cursor.execute(delete_column_query)
        conn.commit()
        top.destroy()
        messagebox.showinfo("Success", f"Column '{column_name}' deleted successfully.")

    delete_button = tk.Button(top, text='Delete Column', command=delete_selected_column)
    delete_button.pack(pady=10)


def create_new_table(root, cursor, conn):
    top = tk.Toplevel(root)
    top.title('Create New Table')
    table_name_label = tk.Label(top, text='Table Name:')
    table_name_label.pack(pady=5)
    table_name_entry = tk.Entry(top)
    table_name_entry.pack(pady=5)
    field_frame = tk.Frame(top)
    field_frame.pack(pady=5)

    fields = []

    def add_field():
        field_entry = tk.Entry(field_frame)
        field_entry.pack(pady=3)
        fields.append(field_entry)

    add_field_button = tk.Button(top, text='Add Field', command=add_field)
    add_field_button.pack(pady=5)

    def create_table():
        table_name = table_name_entry.get()
        if not table_name:
            messagebox.showwarning("Warning", "Enter a table name.")
            return

        field_definitions = [f"{field.get()} TEXT" for field in fields if field.get()]
        if not field_definitions:
            messagebox.showwarning("Warning", "Define at least one field.")
            return

        create_table_query = f"CREATE TABLE {table_name} ({', '.join(field_definitions)})"
        cursor.execute(create_table_query)
        conn.commit()
        top.destroy()
        messagebox.showinfo("Success", f"Table '{table_name}' created successfully.")

    create_button = tk.Button(top, text='Create Table', command=create_table)
    create_button.pack(pady=10)


def delete_table(root, cursor, conn, table_name):
    confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete the table '{table_name}'?")
    if confirm:
        delete_query = f"DROP TABLE {table_name}"
        cursor.execute(delete_query)
        conn.commit()
        messagebox.showinfo("Success", f"Table '{table_name}' deleted successfully.")
