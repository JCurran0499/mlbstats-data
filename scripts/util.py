import json

def get_secret(secret_name: str):
    try:
        with open("secrets.json", "r") as file:
            data = json.load(file)

        value = data.get(secret_name)

        if value is not None:
            return value
        else:
            return f"Field not found in the JSON file."

    except FileNotFoundError:
        return f"Error: The file was not found."
    except json.JSONDecodeError:
        return "Error: Failed to decode JSON. Check if the file is valid JSON."
    

def get_stat(data, stat: str):
    stat_array = stat.split(".")
    try:
        for key in stat_array:
            if _is_int(key):
                key = int(key)
            
            data = data[key]

        return data
    except KeyError:
        return f"Error: Key '{key}' not found in the JSON data."
    except Exception as e:
        return f"An error occurred: {str(e)}"
    

def _is_int(value):
    try:
        int(value)
        return True
    except ValueError:
        return False