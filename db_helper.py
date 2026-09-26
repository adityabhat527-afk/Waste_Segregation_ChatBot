import json
from pymongo import MongoClient
from pymongo.errors import PyMongoError, ConnectionFailure

DEFAULT_URI = "mongodb://localhost:27017/"
DEFAULT_DB_NAME = "waste_db"
DEFAULT_COLLECTION_NAME = "intents"

def get_mongo_client(uri=DEFAULT_URI):
    """Establish and return a MongoClient connection."""
    client = MongoClient(uri, serverSelectionTimeoutMS=3000)
    # Check connection
    client.admin.command('ping')
    return client

def test_connection(uri=DEFAULT_URI):
    """Test if MongoDB server is reachable."""
    try:
        client = get_mongo_client(uri)
        client.close()
        return True, "Connected successfully to MongoDB"
    except Exception as e:
        return False, f"Failed to connect to MongoDB: {str(e)}"

def load_intents_from_db(uri=DEFAULT_URI, db_name=DEFAULT_DB_NAME, collection_name=DEFAULT_COLLECTION_NAME):
    """Fetch all intent categories from MongoDB."""
    client = get_mongo_client(uri)
    db = client[db_name]
    collection = db[collection_name]
    
    intents = list(collection.find({}, {'_id': 0}))
    client.close()
    return intents

def seed_db_from_json(json_filepath="intents.json", uri=DEFAULT_URI, db_name=DEFAULT_DB_NAME, collection_name=DEFAULT_COLLECTION_NAME, overwrite=False):
    """Import data from intents.json into MongoDB."""
    client = get_mongo_client(uri)
    db = client[db_name]
    collection = db[collection_name]

    if collection.count_documents({}) > 0 and not overwrite:
        client.close()
        return False, f"Collection '{collection_name}' already contains documents. Set overwrite=True to re-seed."

    with open(json_filepath, "r", encoding="utf-8") as file:
        data = json.load(file)

    categories = data.get("categories", [])
    if not categories:
        client.close()
        return False, "No categories found in JSON file."

    if overwrite:
        collection.delete_many({})

    collection.insert_many(categories)
    client.close()
    return True, f"Successfully seeded {len(categories)} categories into MongoDB ('{db_name}.{collection_name}')."

def insert_or_update_category(category_dict, uri=DEFAULT_URI, db_name=DEFAULT_DB_NAME, collection_name=DEFAULT_COLLECTION_NAME):
    """Insert or update a single intent category in MongoDB."""
    category_name = category_dict.get("category")
    if not category_name:
        raise ValueError("Category dict must contain a 'category' key.")

    client = get_mongo_client(uri)
    db = client[db_name]
    collection = db[collection_name]

    existing = collection.find_one({"category": category_name})

    if existing:
        existing_examples = set(existing.get("examples", []))
        new_examples = category_dict.get("examples", [])
        updated_examples = list(existing_examples.union(set(new_examples)))

        update_fields = {
            "examples": updated_examples,
        }
        if "description" in category_dict and category_dict["description"]:
            update_fields["description"] = category_dict["description"]
        if "type" in category_dict and category_dict["type"]:
            update_fields["type"] = category_dict["type"]

        collection.update_one({"category": category_name}, {"$set": update_fields})
        msg = f"Updated category '{category_name}' with total {len(updated_examples)} examples."
    else:
        # Strip _id if passed
        category_dict.pop("_id", None)
        collection.insert_one(category_dict)
        msg = f"Created new category '{category_name}' with {len(category_dict.get('examples', []))} examples."

    client.close()
    return True, msg

def add_examples_to_category(category_name, new_examples, uri=DEFAULT_URI, db_name=DEFAULT_DB_NAME, collection_name=DEFAULT_COLLECTION_NAME):
    """Add new examples to an existing category."""
    client = get_mongo_client(uri)
    db = client[db_name]
    collection = db[collection_name]

    result = collection.update_one(
        {"category": category_name},
        {"$addToSet": {"examples": {"$each": new_examples}}}
    )
    client.close()
    return result.modified_count > 0

def delete_category(category_name, uri=DEFAULT_URI, db_name=DEFAULT_DB_NAME, collection_name=DEFAULT_COLLECTION_NAME):
    """Delete a category from MongoDB."""
    client = get_mongo_client(uri)
    db = client[db_name]
    collection = db[collection_name]

    res = collection.delete_one({"category": category_name})
    client.close()
    return res.deleted_count > 0

def clear_all_categories(uri=DEFAULT_URI, db_name=DEFAULT_DB_NAME, collection_name=DEFAULT_COLLECTION_NAME):
    """Delete all categories from collection."""
    client = get_mongo_client(uri)
    db = client[db_name]
    collection = db[collection_name]

    res = collection.delete_many({})
    client.close()
    return res.deleted_count

def sync_training_dataset_table(uri=DEFAULT_URI, db_name=DEFAULT_DB_NAME, source_collection="intents", target_collection="training_dataset"):
    """
    Creates/updates a dedicated flat 'training_dataset' table (collection) in MongoDB
    where each document represents an individual training item mapped to its intent category,
    waste type, and disposal description.
    """
    client = get_mongo_client(uri)
    db = client[db_name]
    intents_coll = db[source_collection]
    training_coll = db[target_collection]

    intents = list(intents_coll.find({}, {'_id': 0}))
    if not intents:
        client.close()
        return False, "No intents data found to populate training table."

    training_coll.delete_many({})

    records = []
    for cat in intents:
        cat_name = cat.get("category", "")
        wtype = cat.get("type", "General Waste")
        desc = cat.get("description", "")
        examples = cat.get("examples", [])

        for ex in examples:
            if isinstance(ex, str) and ex.strip():
                records.append({
                    "item_pattern": ex.strip(),
                    "category": cat_name,
                    "waste_type": wtype,
                    "disposal_instruction": desc
                })

    if records:
        training_coll.insert_many(records)

    client.close()
    return True, f"Successfully created/updated '{target_collection}' table with {len(records)} training records."

