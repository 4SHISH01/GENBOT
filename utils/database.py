import json, os, time

DATA_PATH = "data/storage.json"

def load_data():
    if not os.path.exists(DATA_PATH):
        return {"cooldowns": {}, "vouched": {}, "whitelist": []}
    with open(DATA_PATH, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=4)

def can_generate(user_id, wait_time):
    data = load_data()
    last_time = data["cooldowns"].get(str(user_id), 0)
    return (time.time() - last_time) >= wait_time

def set_generate(user_id):
    data = load_data()
    data["cooldowns"][str(user_id)] = time.time()
    save_data(data)

def mark_vouched(user_id):
    data = load_data()
    data["vouched"][str(user_id)] = True
    save_data(data)

def is_whitelisted(user_id):
    data = load_data()
    return str(user_id) in data["whitelist"]

def add_whitelist(user_id):
    data = load_data()
    if str(user_id) not in data["whitelist"]:
        data["whitelist"].append(str(user_id))
        save_data(data)
