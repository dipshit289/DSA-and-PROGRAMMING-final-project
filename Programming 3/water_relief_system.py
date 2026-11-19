import json
import os
import getpass
from datetime import datetime as dt

records_file = "records.json"
admin_file = "admin_info.json"

r_data = []

# if the json file doesn't exist -- create an empty list
if not os.path.exists(records_file):
    with open(records_file, "w") as rf:
        json.dump([], rf)
# if the file exists, load records
else:
    try:
        with open(records_file, "r") as rf:
            r_data = json.load(rf)
    # if file is damaged, back it up and start with an empty list
    except json.decoder.JSONDecodeError:
        os.replace(records_file, "records_backup.json")
        print("[!] records.json was damaged/corrupted. Saved a copy as records_backup.json")
        r_data = []
        with open(records_file, "w") as rf:
            json.dump([], rf)


# HELPER FUNCTIONS

# for saving changes/record
def save_records():
    # write all records back to json file
    with open(records_file, "w") as rf:
        json.dump(r_data, rf, indent=2)


# for getting input in create request
def get_required_input(prompt):
    # program keeps asking until input is not blank
    while True:
        value = input(prompt).strip()
        if value != "":
            return value
        print("[!] This field cannot be blank. Please try again.")


# admin login is required to access services 2-4
def check_admin_login():
    # returns true if password and username is correct, false if not
    if not os.path.exists(admin_file):
        print("admin_info.json was not found.")
        return False

    with open(admin_file, "r") as af:
        admin_info = json.load(af)

    print("Admin login required.")
    username = input("Enter your username: ").strip()
    # getpass to hide password and echo_char to display "*" while typing password
    password = getpass.getpass("Enter admin password: ", echo_char="*")

    for account in admin_info:
        if account["username"] == username and account["password"] == password:
            print("Login Successful.", "\nYou now have Administrative Access.")
            return True

    print("Access denied.")
    return False


# labels for display_record func
record_labels = {
    "ticket_id": "Ticket ID",
    "name": "Name",
    "block_number": "Block Number",
    "household_number": "Household Number",
    "contact_number": "Contact Number",
    "request_type": "Request Type",
    "description": "Description",
    "status": "Status",
    "date_created": "Date Created",
    "date_updated": "Last Updated",
}


# displays one ticket (used in all services)
def display_record(record):
    # print each info using for loop
    print("-" * 40)
    for key in record_labels:
        # skip keys the ticket doesn't have yet (date_updated on new ticket)
        if key in record:
            print(record_labels[key].ljust(18) + ":", record[key])
    print("-" * 40)


# function for finding ticket id
def find_ticket(ticket_id):
    # uses linear searching
    for record in r_data:
        if record["ticket_id"] == ticket_id:
            return record
    return None

# checks if a household already has an unfinished request of the same type
def find_active_request(block_number, household_number, request_type):
    for record in r_data:
        if (record["block_number"] == block_number
                and record["household_number"] == household_number
                and record["request_type"] == request_type
                and record["status"] != "Completed"):
            return record
    return None




# 1.CREATE REQUEST
def create_request():
    print("=" * 40)
    print("CREATE REQUEST".center(40))
    print("=" * 40)

    # name must contain letters only (spaces, periods, and hyphens are allowed)
    while True:
        name = input("Enter your name: ").strip()
        letter_only = name.replace(" ", "").replace("-", "").replace(".", "")

        if name == "":
            print("This field cannot be blank. Please try again.")
        elif not letter_only.isalpha():
            print("Invalid Name. Use letters only (spaces, periods, and hyphens are allowed).")
        elif len(letter_only) < 2:
            print("Invalid Name. It must have at least 2 letters.")
        else:
            break

    # choose block number from the list
    while True:
        print("\nChoose Block Number: ")
        print("[1] Block 10", "\n[2] Block 19", "\n[3] Block 35", "\n[4] Block 39A", "\n[5] Block 39B")

        choice = input("Enter block number: ").strip()

        if choice == "1":
            block_number = "10"
            break
        elif choice == "2":
            block_number = "19"
            break
        elif choice == "3":
            block_number = "35"
            break
        elif choice == "4":
            block_number = "39A"
            break
        elif choice == "5":
            block_number = "39B"
            break
        else:
            print("Invalid Block Number. Please try again")

    # for household number, digits only (1-36) are accepted
    while True:
        household_number = input("Enter your household number: ").strip()
        if household_number == "":
            print("This field cannot be blank. Please try again.")
        elif not household_number.isdigit():
            print("Invalid Household Number. Use Numbers only.")
        elif not 1 <= int(household_number) <= 36:
            print("Invalid Household Number. Enter number 1-36")
        else:
            household_number = str(int(household_number))  # removes leading zeros: "007" -> "7"
            break



    # contact number must be 11 digits and start with 09
    while True:
        contact_number = input("Enter your contact number: ").strip()
        if contact_number == "":
            print("This field cannot be blank. Please try again.")
        elif not contact_number.isdigit() or len(contact_number) != 11 or not contact_number.startswith("09"):
            print("Invalid Number. It must be 11 digits and start with 09.")
        else:
            break

    # while loop again to iterate through the choices
    while True:
        print("Request Type:")
        print("[1] No water supply", "\n[2] Contaminated / Discolored Water", "\n[3] Leak or burst pipe",
              "\n[4] Others")
        choice = input("Please choose a request type: ").strip()

        if choice == "1":
            request_type = "No water supply"
            break
        elif choice == "2":
            request_type = "Contaminated / Discolored Water"
            break
        elif choice == "3":
            request_type = "Leak or burst pipe"
            break
        elif choice == "4":
            request_type = "Others"
            break
        else:
            print("Invalid Choice. Please try again.")

    # checks for duplicate request
    existing = find_active_request(block_number, household_number, request_type)
    if existing is not None:
        print("\n[!] This household already has an active request for this problem.")
        print("No new ticket was created. Existing Ticket:")
        display_record(existing)
        return

    description = get_required_input("Enter a short description of the problem: ")

    ticket_id = "WR" + str(len(r_data) + 1).zfill(5)

    date_created = dt.now().strftime("%m/%d/%Y, %I:%M:%S %p")

    new_record = {
        "ticket_id": ticket_id,
        "name": name,
        "household_number": household_number,
        "block_number": block_number,
        "contact_number": contact_number,
        "request_type": request_type,
        "description": description,
        "status": "Pending",
        "date_created": date_created
    }

    # save list to json file
    r_data.append(new_record)
    save_records()

    print("\nRequest Created Successfully!")
    display_record(new_record)


# 2.VIEW RECORDS
def view_records():
    print("=" * 40)
    print("VIEW RECORDS".center(40))
    print("=" * 40)

    # Admin login
    if not check_admin_login():
        return

    # Check if there are records
    if len(r_data) == 0:
        print("Records not found.")
        return

    # Ask which record to show
    while True:
        print("\nSelect Which Record to View")
        print("[1] All", "\n[2] Pending", "\n[3] Ongoing", "\n[4] Completed")

        choice = input("Selected record: ").strip()

        if choice == "1":
            selected_record = "All"
            break
        elif choice == "2":
            selected_record = "Pending"
            break
        elif choice == "3":
            selected_record = "Ongoing"
            break
        elif choice == "4":
            selected_record = "Completed"
            break
        else:
            print("Invalid choice. Please try again.")

    # Show matching records
    found_count = 0

    for record in r_data:
        if selected_record == "All" or record["status"] == selected_record:
            display_record(record)
            found_count += 1

    if found_count == 0:
        print(f"No {selected_record} records found")

    # Count each status
    pending = 0
    ongoing = 0
    completed = 0

    for record in r_data:
        status = record["status"]

        if status == "Pending":
            pending += 1
        elif status == "Ongoing":
            ongoing += 1
        elif status == "Completed":
            completed += 1

    # Summary
    print("Total:", len(r_data), "| Pending:", pending,
          "| Ongoing:", ongoing, "| Completed:", completed)


# 3.SEARCH TICKET

def search_ticket():
    print("=" * 40)
    print("SEARCH TICKET".center(40))
    print("=" * 40)

    # admin authentication
    if not check_admin_login():
        return

    ticket_id = input("Enter ticket ID: ").strip().upper()
    record = find_ticket(ticket_id)

    if record is None:
        print("Ticket Not Found")
    else:
        display_record(record)


# 4.UPDATE REQUEST

def update_request():
    print("=" * 40)
    print("UPDATE REQUEST".center(40))
    print("=" * 40)

    # admin authentication
    if not check_admin_login():
        return

    # find the ticket id (same steps as search_ticket)
    ticket_id = input("Enter ticket ID: ").strip().upper()
    record = find_ticket(ticket_id)

    if record is None:
        print("Ticket Not Found")
        return

    display_record(record)

    # show the update options
    print("Update Status:")
    print("[1] Pending", "\n[2] Ongoing", "\n[3] Completed")
    choice = input("Choose new Status: ").strip()

    if choice == "1":
        new_status = "Pending"
    elif choice == "2":
        new_status = "Ongoing"
    elif choice == "3":
        new_status = "Completed"
    else:
        print("Invalid Choice. No changes were made.")
        return

    # same as current status, no changes
    if new_status == record["status"]:
        print("Ticket is already", new_status + ". No changes were made.")
        return

    # update records
    record["status"] = new_status
    # include the date and time when the record was updated
    record["date_updated"] = dt.now().strftime("%m/%d/%Y, %I:%M:%S %p")

    # save changes to json file
    save_records()

    print("Record Updated Successfully!")
    display_record(record)


# MAIN PROGRAM

print("=" * 40)
print("WATER RELIEF TICKETING SYSTEM".center(40))
print("=" * 40)

# Menu loop, repeats until user chooses exit
while True:
    print("\n[1] Create Request", "\n[2] View Records (Admin)", "\n[3] Search Ticket (Admin)",
          "\n[4] Update Request (Admin)", "\n[5] Exit")
    print("[!] Note: Options 2-4 Require Administrative Access")
    service = input("Please Choose a Service: ").strip()

    if service == "1":
        create_request()
    elif service == "2":
        view_records()
    elif service == "3":
        search_ticket()
    elif service == "4":
        update_request()
    elif service == "5":
        save_records()
        print("Thank you for using Water Relief Ticketing System")
        print("Program Terminated")
        break
    else:
        print("Invalid Input. Please try again")