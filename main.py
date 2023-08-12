import tkinter as tk
import tkinter.ttk as ttk
import sqlite3
from tkinter import filedialog
import functions


def select_file():
    file_path = filedialog.askopenfilename(title="Select an SQLite Database", filetypes=[("SQLite files", "*.sqlite")])
    if file_path:
        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()
        root.withdraw()  # Hide the file selection window
        create_main_window(root, conn, cursor)


def create_main_window(root, conn, cursor):
    # Create the Tkinter window
    main_window = tk.Tk()
    main_window.title('Supermarket Database Management Software')
    main_window.iconbitmap("icon.ico")

    def refresh_table_dropdown():
        table_names = functions.get_table_names(cursor)
        table_name_entry["values"] = table_names

    query_frame = tk.Frame(main_window)
    query_frame.pack(padx=20, pady=10)

    table_name_label = tk.Label(query_frame, text='Select Table:')
    table_name_label.grid(row=0, column=0, padx=5, pady=5, sticky='e')
    table_name_entry = ttk.Combobox(query_frame, values=functions.get_table_names(cursor))
    table_name_entry.grid(row=0, column=1, padx=5, pady=5)

    refresh_button = tk.Button(query_frame, text='Refresh', command=refresh_table_dropdown)
    refresh_button.grid(row=0, column=2, padx=5, pady=5)

    display_table_button = tk.Button(query_frame, text='Display Table',
                                     command=lambda: functions.query_database(main_window, cursor,
                                                                              table_name_entry.get()))
    display_table_button.grid(row=0, column=3, padx=5, pady=5)

    add_row_button = tk.Button(query_frame, text='Add Row',
                               command=lambda: functions.add_row_to_table(main_window, cursor, table_name_entry.get(),
                                                                          conn))
    add_row_button.grid(row=0, column=4, padx=5, pady=5)

    delete_row_button = tk.Button(query_frame, text='Delete Row',
                                  command=lambda: functions.delete_row_from_table(main_window, cursor,
                                                                                  table_name_entry.get(), conn))
    delete_row_button.grid(row=0, column=5, padx=5, pady=5)

    delete_column_button = tk.Button(query_frame, text='Delete Column',
                                     command=lambda: functions.delete_column_from_table(main_window, cursor,
                                                                                        table_name_entry.get(), conn))
    delete_column_button.grid(row=0, column=6, padx=5, pady=5)

    command_frame = tk.Frame(main_window)
    command_frame.pack(padx=20, pady=10)

    custom_command_label = tk.Label(command_frame, text='Custom Command:')
    custom_command_label.grid(row=0, column=0, padx=5, pady=5, sticky='e')
    custom_command_entry = tk.Entry(command_frame, width=50)  # Increase the width here
    custom_command_entry.grid(row=0, column=1, padx=5, pady=5)

    custom_command_button = tk.Button(command_frame, text='Execute',
                                      command=lambda: functions.run_custom_command(main_window, cursor,
                                                                                   custom_command_entry))
    custom_command_button.grid(row=0, column=2, padx=5, pady=5)

    buttons_frame = tk.Frame(main_window)
    buttons_frame.pack(pady=10)

    create_table_button = tk.Button(buttons_frame, text='Create New Table',
                                    command=lambda: functions.create_new_table(main_window, cursor, conn))
    create_table_button.pack(side='left', padx=10)

    delete_table_button = tk.Button(buttons_frame, text='Delete Table',
                                    command=lambda: functions.delete_table(main_window, cursor, conn,
                                                                           table_name_entry.get()))
    delete_table_button.pack(side='left', padx=10)

    exit_button = tk.Button(buttons_frame, text='Exit', command=main_window.quit)
    exit_button.pack(side='right', padx=10)

    main_window.mainloop()


root = tk.Tk()
root.title('Select SQLite Database')
root.geometry('600x300')

label = tk.Label(root, text="Select an SQLite database file:")
label.pack(pady=10)

select_button = tk.Button(root, text="Select File", command=select_file)
select_button.pack()

root.mainloop()
