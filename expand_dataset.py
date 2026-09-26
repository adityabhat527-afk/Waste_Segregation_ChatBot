import db_helper
import model_trainer

EXPANDED_CATEGORIES = [
    {
        "category": "Organic & Food Waste Intent",
        "type": "Organic / Biodegradable Waste",
        "description": "Dispose of in the GREEN organic/compost bin or home compost pit. Keep free from plastic wrappers.",
        "examples": [
            "Banana peels", "Apple cores", "Orange rinds", "Lemon peels", "Potato peels", "Onion skins",
            "Garlic hulls", "Carrot tops", "Eggshells", "Coffee grounds", "Tea bags", "Tea leaves",
            "Spoiled fruits", "Rotten vegetables", "Cooked rice leftovers", "Pasta scraps", "Bread crusts",
            "Meat scraps", "Chicken bones", "Fish bones", "Seafood shells", "Nut shells", "Coconut shells",
            "Melon rinds", "Avocado pits", "Corn cobs", "Pumpkin seeds", "Fruit seeds", "Salad leftovers",
            "Wilted lettuce", "Broccoli stems", "Herb stems", "Stale bread", "Pastry scraps", "Cheese rinds"
        ]
    },
    {
        "category": "Garden & Yard Waste Intent",
        "type": "Organic / Compostable Waste",
        "description": "Dispose of in yard waste bins or community composting centers. Do not burn.",
        "examples": [
            "Dry leaves", "Grass clippings", "Fallen tree branches", "Dead flowers", "Potted plant soil",
            "Weeds", "Twig bundles", "Pine needles", "Shrub trimmings", "Mulch scraps", "Bark chips"
        ]
    },
    {
        "category": "E-Waste & Electronics Intent",
        "type": "Electronic Waste (E-Waste)",
        "description": "MUST be taken to designated E-Waste collection points, electronic store drop-boxes, or municipal e-waste recycling events. NEVER throw in regular trash.",
        "examples": [
            "Old smartphone", "Broken cell phone", "Laptop computer", "Desktop CPU", "Computer monitor",
            "Keyboard", "Computer mouse", "USB flash drive", "External hard drive", "HDMI cable",
            "Phone charger cable", "Power bank", "Headphones", "Earphones", "Wireless earbuds",
            "Smartwatch", "Tablet iPad", "Wi-Fi router", "Modem", "Printer", "Ink cartridge",
            "Toner cartridge", "Gaming console", "PlayStation controller", "Xbox console", "Extension cord",
            "Calculators", "Digital cameras", "Drone batteries", "Electric toothbrush", "Hair dryer",
            "Microwave oven", "Electric kettle", "Toaster", "Circuit boards", "RAM sticks"
        ]
    },
    {
        "category": "Hazardous & Chemical Waste Intent",
        "type": "Hazardous Household Waste",
        "description": "DANGER: High toxicity or fire hazard. Take to a municipal Hazardous Waste Disposal Facility. Do not pour down drains or put in landfill bins.",
        "examples": [
            "Lithium-ion batteries", "AA batteries", "AAA batteries", "9V batteries", "Car battery",
            "Button cell batteries", "Motor oil", "Used engine oil", "Oil filters", "Paint cans",
            "Oil-based paint", "Paint thinner", "Turpentine", "Acetone nail polish remover", "Pesticides",
            "Insecticide sprays", "Weed killer", "Rat poison", "Bleach bottles", "Drain cleaner chemicals",
            "Ammonia cleaner", "Fluorescent light bulbs", "CFL tube lights", "Mercury thermometers",
            "Kerosene", "Gasoline cans", "Propane tanks", "Fire extinguishers", "Pool chemicals"
        ]
    },
    {
        "category": "Medical & Sanitary Waste Intent",
        "type": "Biohazardous / Sanitary Waste",
        "description": "Sanitary waste should be wrapped securely in newspaper or bags and put in the RED or NON-RECYCLABLE residual waste bin. Needles/syringes must go to sharp disposal boxes.",
        "examples": [
            "Used face masks", "Latex gloves", "Surgical gloves", "Sanitary pads", "Tampons",
            "Diapers", "Baby wipes", "Used bandages", "Gauze pads", "Used cotton swabs",
            "Cotton balls", "Expired prescription medicines", "Pill blister packs", "Empty medicine bottles",
            "Syringes with needles", "Insulin needles", "Lancets", "IV bags", "Medical tubing", "Thermometer sheath"
        ]
    },
    {
        "category": "Recyclable Plastics Intent",
        "type": "Recyclable Plastic Waste",
        "description": "Rinse clean, dry, and place in the BLUE plastic recycling bin. Remove caps if required by local facility.",
        "examples": [
            "PET water bottle", "Soda plastic bottle", "HDPE milk jug", "Shampoo bottle", "Conditioner bottle",
            "Detergent bottle", "Liquid soap dispenser bottle", "Juice plastic bottle", "Plastic food containers",
            "Yogurt tub", "Margarine tub", "Plastic condiment bottles", "Ketchup bottle", "Plastic bottle caps",
            "Plastic sauce jars", "Clear plastic clamshell packaging", "Plastic takeaway containers"
        ]
    },
    {
        "category": "Soft Plastics & Packaging Film Intent",
        "type": "Soft Plastic Packaging",
        "description": "Check if your grocery store has a soft plastic drop-off bin. Do NOT place in standard curb recycling bins as they jam sorting machinery.",
        "examples": [
            "Plastic grocery shopping bags", "Bubble wrap", "Air pillow packaging", "Shrink wrap",
            "Cling film", "Potato chip packets", "Snack wrappers", "Candy wrappers", "Bread plastic bags",
            "Frozen food plastic bags", "Ziploc bags", "Plastic mailer envelopes", "Cereal box liners"
        ]
    },
    {
        "category": "Paper & Cardboard Intent",
        "type": "Recyclable Paper Waste",
        "description": "Keep dry and clean. Flatten cardboard boxes and place in the YELLOW or BLUE paper recycling bin.",
        "examples": [
            "Corrugated cardboard boxes", "Shipping boxes", "Cereal cardboard boxes", "Tissue boxes",
            "Egg cartons (paper)", "Newspapers", "Magazines", "Office printing paper", "Notebooks",
            "Envelopes", "Paper bags", "Paperback books", "Telephone books", "Shredded paper",
            "Cardboard packaging inserts", "Brochures", "Junk mail", "Paper egg crates"
        ]
    },
    {
        "category": "Glass Containers Intent",
        "type": "Recyclable Glass Waste",
        "description": "Rinse clean and place in the GLASS recycling bin. Separated by color (clear, green, brown) if required locally. Do not mix window or mirror glass.",
        "examples": [
            "Glass water bottle", "Wine glass bottle", "Beer bottle", "Glass jam jar", "Glass pickle jar",
            "Sauce glass bottle", "Olive oil glass bottle", "Medicine glass vial", "Cosmetic glass jar",
            "Glass baby food jar", "Glass condiment bottle"
        ]
    },
    {
        "category": "Metals & Aluminum Intent",
        "type": "Recyclable Metal Waste",
        "description": "Rinse food containers clean. Place aluminum soda cans and tin food cans in the METAL recycling bin.",
        "examples": [
            "Aluminum soda cans", "Beer aluminum cans", "Tin soup cans", "Canned food tins", "Tuna fish cans",
            "Metal bottle caps", "Jar lids", "Clean aluminum foil", "Aluminum foil baking trays",
            "Empty aerosol cans (spray paint, deodorant)", "Metal cutlery", "Scrap metal pieces", "Copper wires"
        ]
    },
    {
        "category": "Textile & Clothing Intent",
        "type": "Textile Waste",
        "description": "Donate wearable items to clothing drop boxes or charity bins. Torn/unwearable fabrics can go to textile recycling facilities.",
        "examples": [
            "Old cotton T-shirts", "Jeans", "Torn pants", "Worn shoes", "Sneakers", "Old socks",
            "Bed sheets", "Pillowcases", "Blankets", "Towels", "Curtains", "Fabric scraps",
            "Winter jackets", "Sweaters", "Leather belts", "Handbags"
        ]
    },
    {
        "category": "Bulky & Household Goods Intent",
        "type": "Bulky Waste / Furniture",
        "description": "Schedule a municipal bulky item collection or bring to a local transfer station / scrap yard.",
        "examples": [
            "Old mattress", "Wooden chair", "Broken sofa", "Dining table", "Carpet roll",
            "Desk", "Bookshelf", "Bicycle frame", "Broken mirror", "Luggage suitcase"
        ]
    },
    {
        "category": "Composite & Residual Waste Intent",
        "type": "Non-Recyclable Residual Landfill Waste",
        "description": "Place in the BLACK or GREY non-recyclable landfill bin.",
        "examples": [
            "Tetra Pak juice carton", "Milk carton", "Waxed paper cups", "Greasy pizza box bottom",
            "Used paper napkins", "Dirty paper towels", "Broken ceramic dish", "Porcelain mug",
            "Cigarette butts", "Vacuum cleaner dust bag", "Styrofoam takeaway box", "Styrofoam packing peanuts",
            "Pet litter", "Cat litter", "Dog waste bags", "Chewing gum"
        ]
    }
]

def main():
    print("🌱 Inserting enriched multi-category dataset into MongoDB...")
    inserted_count = 0
    total_examples = 0
    
    for cat in EXPANDED_CATEGORIES:
        success, msg = db_helper.insert_or_update_category(cat)
        if success:
            inserted_count += 1
            total_examples += len(cat["examples"])
            print(f"  ✅ {msg}")

    print(f"\n🎉 Added/Updated {inserted_count} comprehensive categories with {total_examples} new examples in MongoDB!")
    
    # Reload all categories from MongoDB
    all_data = db_helper.load_intents_from_db()
    print(f"\n📊 Total MongoDB Categories: {len(all_data)}")
    
    # Train Model
    print("\n🏋️ Retraining Random Forest ML Model with enriched dataset...")
    vec, model, desc, types, meta = model_trainer.train_model(all_data)
    
    print("\n✅ AI Model Training Complete!")
    print(f"  - Total Categories: {meta['num_categories']}")
    print(f"  - Total Training Patterns: {meta['num_patterns']}")
    print(f"  - Vocabulary Size: {meta['vocab_size']}")

if __name__ == "__main__":
    main()
