import curses
import os
import subprocess
import json
from sqlalchemy import create_engine, MetaData, Table, select, update
from sqlalchemy.orm import sessionmaker
from tabulate import tabulate
from pprint import pprint
import mysql
import sys

stdscr = None

# Function to truncate text while preserving whole words
def truncate_text(text, max_length):
    if isinstance(text, str):
        return text[:max_length] + "..." if len(text) > max_length else text
    return text  # Return unchanged if not a string

# Function to get database configuration from env.php
def get_db_config_from_env():
    """Run PHP command to get env.php configuration and extract database credentials."""
    try:
        # Run the PHP command
        cwd = os.getcwd()
        command = ['php', '-r', 'echo json_encode(include "' + cwd + '/app/etc/env.php");']
        result = subprocess.run(command, capture_output=True, text=True, check=True)

        if result.stderr:
            # Current working directory
            command = ['php', '-r', 'echo json_encode(include "'+cwd+'/../app/etc/env.php");']
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            
        if result.stderr:
            command = ['php', '-r', 'echo json_encode(include "'+cwd+'/../../app/etc/env.php");']
            result = subprocess.run(command, capture_output=True, text=True, check=True)
       
        # Parse the JSON output
        config = json.loads(result.stdout)
      
        # Extract database credentials
        db_config = config.get('db', {}).get('connection', {}).get('default', {})
        return {
            'host': db_config.get('host'),
            'user': db_config.get('username'),
            'password': db_config.get('password'),
            'database': db_config.get('dbname')
        }
    except subprocess.CalledProcessError as e:
        print(f"Error running PHP command: {e}")
        dd(e,True)
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        dd(e,True)
        return None

def dd(message, die=False):
    global stdscr
    if not isinstance(message, str):
        message = str(message)
    stdscr.addstr(0, 15, "dd():" + message)  # Display the message
    stdscr.refresh()  # Refresh the screen to show the message
    stdscr.getch()  # Wait for user input
    if die:
        sys.exit(1)  # Terminate the program

# Connect to MySQL database using SQLAlchemy
def connect_to_db():
    """Connect to the MySQL database using SQLAlchemy."""
    db_config = get_db_config_from_env()
    if not db_config:
        print("Failed to retrieve database configuration from env.php.")
        return None

    try:
        # Create a connection string
        connection_string = f"mysql+mysqlconnector://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}"

        # Create an engine and session
        engine = create_engine(connection_string)
        Session = sessionmaker(bind=engine)
        session = Session()

        return engine, session
    except Exception as e:
        print(f"Error connecting to MySQL: {e}")
        return None, None

def search_by_path(stdscr):
    """Search for records in the `core_config_data` table by path with pagination."""
    stdscr.clear()
    stdscr.addstr(0, 0, "Enter the path to search: ")
    curses.echo()  # Enable input echoing
    path = stdscr.getstr().decode('utf-8')
    curses.noecho()  # Disable input echoing

    engine, session = connect_to_db()
    if engine and session:
        metadata = MetaData()
        core_config_data = Table('core_config_data', metadata, autoload_with=engine)

        # Build the query
        query = select(core_config_data).where(core_config_data.c.path.like(f'%{path}%'))
        results = session.execute(query).fetchall()
        session.close()

        stdscr.clear()

        if not results:
            stdscr.addstr(0, 0, f"No records found for Path '{path}'.")
            stdscr.refresh()
            stdscr.getch()
            return

        # Table headers
        headers = ["ID", "Scope-ID", "Path", "Value", "Updated At"]

        # Process data with truncated columns
        table_data = [
            [row.config_id, f"{row.scope}-{row.scope_id}", 
             truncate_text(row.path, 40), 
             truncate_text(row.value, 40), 
             truncate_text(row.updated_at, 10)]
            for row in results
        ]

        # Generate ASCII table
        table = tabulate(table_data, headers, tablefmt="grid")
        table_lines = table.split("\n")

        # Get terminal size
        height, width = stdscr.getmaxyx()

        # Number of lines that fit per page (excluding headers and navigation info)
        max_lines_per_page = height - 4  # Leave room for instructions

        # Pagination Variables
        current_page = 0
        total_pages = (len(table_lines) // max_lines_per_page) + (1 if len(table_lines) % max_lines_per_page else 0)

        while True:
            stdscr.clear()
            stdscr.addstr(0, 0, f"Search Results for Path '{path}' (Page {current_page + 1}/{total_pages}):\n")

            # Get start and end index for pagination
            start_idx = current_page * max_lines_per_page
            end_idx = start_idx + max_lines_per_page

            # Display only the portion of the table that fits on the screen
            for i, line in enumerate(table_lines[start_idx:end_idx]):
                stdscr.addstr(i + 2, 0, line[:width - 1])  # Truncate long lines

            # Display Navigation Instructions at Bottom
            msg = "Use ↑/↓ to navigate, 'q' to exit"
            stdscr.addstr(height - 2, 0, msg[:width - 1])  # Truncate if necessary

            stdscr.refresh()

            # Get user input
            key = stdscr.getch()

            if key == curses.KEY_DOWN and current_page < total_pages - 1:
                current_page += 1  # Next page
            elif key == curses.KEY_UP and current_page > 0:
                current_page -= 1  # Previous page
            elif key == ord('q'):  # Quit when 'q' is pressed
                break

def show_all_records(stdscr):
    """Display all records in the `core_config_data` table with pagination."""
    engine, session = connect_to_db()
    
    if engine and session:
        metadata = MetaData()
        core_config_data = Table('core_config_data', metadata, autoload_with=engine)

        # Fetch all records
        query = select(core_config_data)
        results = session.execute(query).fetchall()
        session.close()

        stdscr.clear()

        if not results:
            stdscr.addstr(0, 0, "No records found in `core_config_data`.")
            stdscr.refresh()
            stdscr.getch()
            return

        # Table headers
        headers = ["ID", "Scope-ID", "Path", "Value", "Updated At"]

        # Process data with truncated columns
        table_data = [
            [row.config_id, f"{row.scope}-{row.scope_id}", 
             truncate_text(row.path, 40), 
             truncate_text(row.value, 40), 
             truncate_text(row.updated_at, 10)]
            for row in results
        ]

        # Generate ASCII table
        table = tabulate(table_data, headers, tablefmt="grid")
        table_lines = table.split("\n")

        # Get terminal size
        height, width = stdscr.getmaxyx()

        # Number of lines that fit per page (excluding headers and navigation info)
        max_lines_per_page = height - 4  # Leave room for instructions

        # Pagination Variables
        current_page = 0
        total_pages = (len(table_lines) // max_lines_per_page) + (1 if len(table_lines) % max_lines_per_page else 0)

        while True:
            stdscr.clear()
            stdscr.addstr(0, 0, "All Records in `core_config_data` (Page {}/{}):\n".format(current_page + 1, total_pages))

            # Get start and end index for pagination
            start_idx = current_page * max_lines_per_page
            end_idx = start_idx + max_lines_per_page

            # Display only the portion of the table that fits on the screen
            for i, line in enumerate(table_lines[start_idx:end_idx]):
                stdscr.addstr(i + 2, 0, line[:width - 1])  # Truncate long lines

            # Display Navigation Instructions at Bottom
            msg = "Use ↑/↓ to navigate, 'q' to exit"
            stdscr.addstr(height - 2, 0, msg[:width - 1])  # Truncate if necessary

            stdscr.refresh()

            # Get user input
            key = stdscr.getch()

            if key == curses.KEY_DOWN and current_page < total_pages - 1:
                current_page += 1  # Next page
            elif key == curses.KEY_UP and current_page > 0:
                current_page -= 1  # Previous page
            elif key == ord('q'):  # Quit when 'q' is pressed
                break

def edit_record_by_id(stdscr):
    """Allow the user to edit a record in the `core_config_data` table by ID."""
    stdscr.clear()
    stdscr.addstr(0, 0, "Enter the Config ID to edit: ")
    curses.echo()  # Enable input
    try:
        config_id = int(stdscr.getstr().decode('utf-8'))  # Read input & convert to int
    except ValueError:
        stdscr.addstr(2, 0, "Invalid ID. Press any key to return.")
        stdscr.getch()
        return
    
    curses.noecho()  # Disable input echoing

    engine, session = connect_to_db()
    if engine and session:
        metadata = MetaData()
        core_config_data = Table('core_config_data', metadata, autoload_with=engine)

        # Query the record by ID
        query = select(core_config_data).where(core_config_data.c.config_id == config_id)
        result = session.execute(query).fetchone()

        if not result:
            stdscr.addstr(2, 0, f"No record found with ID {config_id}. Press any key to return.")
            stdscr.getch()
            return

        # Display existing record
        stdscr.clear()
        stdscr.addstr(0, 0, f"Editing Record ID: {config_id}")
        stdscr.addstr(2, 0, f"Scope-ID: {result.scope}-{result.scope_id}")
        stdscr.addstr(3, 0, f"Path: {result.path}")
        stdscr.addstr(4, 0, f"Current Value: {result.value}")

        # Prompt for new value
        stdscr.addstr(6, 0, "Enter new value (Press ESC to cancel): ")
        curses.echo()
        height, width = stdscr.getmaxyx()
        new_value = ""
        while True:
            key = stdscr.getch()
            if key == 27:  # ESC key pressed
                stdscr.addstr(8, 0, "Edit canceled. Press any key to return.")
                stdscr.getch()
                return
            elif key in [10, 13]:  # Enter key pressed
                break
            elif key == curses.KEY_BACKSPACE or key == 127:
                new_value = new_value[:-1]
                stdscr.move(6, 0)
                stdscr.clrtoeol()
                stdscr.addstr(6, 0, "Enter new value (Press ESC to cancel): " + new_value)
                stdscr.refresh()
            else:
                new_value += chr(key)
                stdscr.move(6, 0)
                stdscr.clrtoeol()
                stdscr.addstr(6, 0, "Enter new value (Press ESC to cancel): " + new_value)
                stdscr.refresh()
        curses.noecho()

        # Confirm before updating
        stdscr.addstr(8, 0, f"Are you sure you want to update the value? (y/n)")
        key = stdscr.getch()
        if key not in [ord('y'), ord('Y')]:
            stdscr.addstr(9, 0, "Update canceled. Press any key to return.")
            stdscr.getch()
            return

        # Update the database
        update_query = update(core_config_data).where(core_config_data.c.config_id == config_id).values(value=new_value)
        session.execute(update_query)
        session.commit()

        stdscr.addstr(10, 0, "Record updated successfully! Press any key to continue.")
        stdscr.getch()

        session.close()

def display_env_php_config(stdscr):
    """Display the configuration from env.php."""
    config = get_db_config_from_env()
    stdscr.clear()
    if config:
        stdscr.addstr(0, 0, "Database Configuration from app/etc/env.php:\n")
        stdscr.addstr(2, 0, json.dumps(config, indent=4))
    else:
        stdscr.addstr(0, 0, "No configuration found in env.php.")
    stdscr.addstr(len(config) + 4, 0, "Press any key to continue.")
    stdscr.getch()

def main_menu(stdscr):
    """Display the main menu and handle user input."""
    options = ["Search by Path", "Show All Records", "Edit Record by ID", "View Database Configuration", "Exit (ESC)"]
    current_selection = 0

    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "Use arrow keys to navigate, Enter to select, ESC to exit:")

        for i, option in enumerate(options):
            if i == current_selection:
                stdscr.addstr(i + 2, 0, f"> {option}")
            else:
                stdscr.addstr(i + 2, 0, f"  {option}")

        key = stdscr.getch()

        if key == 27:  # ESC key pressed
            break  # Exit the menu immediately
        elif key == curses.KEY_UP and current_selection > 0:
            current_selection -= 1
        elif key == curses.KEY_DOWN and current_selection < len(options) - 1:
            current_selection += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if current_selection == 0:
                search_by_path(stdscr)
            elif current_selection == 1:
                show_all_records(stdscr)
            elif current_selection == 2:
                edit_record_by_id(stdscr)  # Add edit feature here
            elif current_selection == 3:
                display_env_php_config(stdscr)
            elif current_selection == 4:
                break  # Exit when "Exit" is selected

def main(stdscr_global):
    """Initialize curses and run the main menu."""
    global stdscr  # Access the global stdscr
    stdscr = stdscr_global  # Assign the passed stdscr to the global variable
    main_menu(stdscr)

def run():
    """Wrapper function for `curses.wrapper` to avoid argument errors."""
    curses.wrapper(main)

if __name__ == "__main__":
    run()
