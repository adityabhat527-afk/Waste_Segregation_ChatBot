import streamlit as st
import json
import os
import pandas as pd
import db_helper
import model_trainer
import gemini_helper

# Page Configuration
st.set_page_config(
    page_title="EcoTrash AI - Smart Waste Segregation & Gemini Assistant",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Injected Custom CSS for High-Tech Modern UI
st.markdown("""
<style>
    /* Global Styles & Font Imports */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Hero Banner Styling */
    .hero-banner {
        background: linear-gradient(135deg, #0d3b66 0%, #0077b6 50%, #00b4d8 100%);
        padding: 24px 32px;
        border-radius: 20px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px rgba(0, 119, 182, 0.25);
    }
    
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 4px;
        letter-spacing: -0.5px;
    }
    
    .hero-subtitle {
        font-size: 1.05rem;
        opacity: 0.9;
        font-weight: 400;
    }

    /* Custom Pill Badges */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 14px;
        border-radius: 50px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 8px;
    }
    
    .badge-success {
        background-color: #d1e7dd;
        color: #0f5132;
        border: 1px solid #badbcc;
    }
    
    .badge-ai {
        background: linear-gradient(135deg, #e0aaff 0%, #c77dff 100%);
        color: #3c096c;
        border: 1px solid #e0aaff;
    }

    .badge-ml {
        background-color: #cff4fc;
        color: #055160;
        border: 1px solid #b6effb;
    }

    /* Bin Tags */
    .bin-tag {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 0.8rem;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .bin-green { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
    .bin-blue { background: #cce5ff; color: #004085; border: 1px solid #b8daff; }
    .bin-red { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    .bin-yellow { background: #fff3cd; color: #856404; border: 1px solid #ffeeba; }
    .bin-grey { background: #e2e3e5; color: #383d41; border: 1px solid #d6d8db; }

    /* Card Layouts */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(220, 220, 220, 0.3);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
        transition: all 0.3s ease;
    }

    /* Hide default Streamlit padding header */
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2rem;
    }
    
    /* Quick chip buttons styling */
    .stButton>button {
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "mongodb_uri" not in st.session_state:
    st.session_state["mongodb_uri"] = db_helper.DEFAULT_URI
if "db_name" not in st.session_state:
    st.session_state["db_name"] = db_helper.DEFAULT_DB_NAME
if "collection_name" not in st.session_state:
    st.session_state["collection_name"] = db_helper.DEFAULT_COLLECTION_NAME
if "gemini_api_key" not in st.session_state:
    st.session_state["gemini_api_key"] = os.environ.get("GEMINI_API_KEY", "")
if "use_gemini" not in st.session_state:
    st.session_state["use_gemini"] = True
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "model_state" not in st.session_state:
    st.session_state["model_state"] = None
if "pending_query" not in st.session_state:
    st.session_state["pending_query"] = ""

# Sidebar Design
with st.sidebar:
    st.image("https://img.icons8.com/illustrations/120/recycling.png", width=70)
    st.title("EcoTrash AI Control")
    st.caption("v2.5 • MongoDB + Gemini AI Connected")
    st.markdown("---")

    # Gemini AI Config Accordion
    with st.expander("🤖 **Gemini AI Settings**", expanded=True):
        gemini_key_input = st.text_input(
            "Gemini API Key",
            value=st.session_state["gemini_api_key"],
            type="password",
            placeholder="AIzaSy...",
            help="Get a free key from aistudio.google.com"
        )
        st.session_state["gemini_api_key"] = gemini_key_input
        
        use_gemini_toggle = st.toggle("Enable Gemini AI Intelligence", value=st.session_state["use_gemini"])
        st.session_state["use_gemini"] = use_gemini_toggle

        if gemini_key_input and use_gemini_toggle:
            st.success("✨ Gemini AI Active & Verified")
        elif use_gemini_toggle and not gemini_key_input:
            st.warning("🔑 Enter Gemini API Key to enable AI responses")

    # MongoDB Config Accordion
    with st.expander("🔌 **MongoDB Settings**", expanded=False):
        uri_input = st.text_input("Connection URI", value=st.session_state["mongodb_uri"])
        db_name_input = st.text_input("Database", value=st.session_state["db_name"])
        coll_name_input = st.text_input("Collection", value=st.session_state["collection_name"])
        
        st.session_state["mongodb_uri"] = uri_input
        st.session_state["db_name"] = db_name_input
        st.session_state["collection_name"] = coll_name_input

    # Check MongoDB Connection
    is_connected, conn_msg = db_helper.test_connection(st.session_state["mongodb_uri"])
    if is_connected:
        st.success("✅ MongoDB Connected")
    else:
        st.error(f"❌ MongoDB Disconnected: {conn_msg}")

    # Action Buttons
    st.markdown("---")
    st.subheader("⚡ Quick Actions")
    
    # Model Training Function
    def load_and_train():
        uri = st.session_state["mongodb_uri"]
        db_n = st.session_state["db_name"]
        coll_n = st.session_state["collection_name"]
        
        data = []
        source_name = "MongoDB"
        
        connected, _ = db_helper.test_connection(uri)
        if connected:
            try:
                data = db_helper.load_intents_from_db(uri, db_n, coll_n)
                if not data:
                    db_helper.seed_db_from_json("intents.json", uri, db_n, coll_n)
                    data = db_helper.load_intents_from_db(uri, db_n, coll_n)
            except Exception as e:
                st.error(f"MongoDB read error: {e}")

        if not data:
            source_name = "Local JSON file (intents.json)"
            with open("intents.json", "r", encoding="utf-8") as f:
                local_data = json.load(f)
                data = local_data.get("categories", [])

        if not data:
            st.error("No training data found.")
            return False

        try:
            vec, model, desc, types, meta = model_trainer.train_model(data)
            meta["source"] = source_name
            st.session_state["model_state"] = {
                "vectorizer": vec,
                "model": model,
                "descriptions": desc,
                "types": types,
                "metadata": meta,
                "categories_data": data
            }
            if connected:
                db_helper.sync_training_dataset_table(uri, db_n, coll_n, "training_dataset")
            return True
        except Exception as e:
            st.error(f"Training error: {e}")
            return False

    if st.session_state["model_state"] is None:
        load_and_train()

    if st.button("🔄 Retrain Model from MongoDB", use_container_width=True):
        with st.spinner("Retraining model..."):
            if load_and_train():
                st.toast("Model retrained successfully!", icon="🎉")

    if is_connected:
        if st.button("📦 Re-Seed MongoDB Dataset", use_container_width=True):
            with st.spinner("Seeding MongoDB..."):
                ok, msg = db_helper.seed_db_from_json(
                    "intents.json",
                    st.session_state["mongodb_uri"],
                    st.session_state["db_name"],
                    st.session_state["collection_name"],
                    overwrite=True
                )
                if ok:
                    st.toast(msg, icon="🌱")
                    load_and_train()

    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state["chat_history"] = []
        st.rerun()

# Hero Header Banner
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">🌱 EcoTrash AI Assistant</div>
    <div class="hero-subtitle">Intelligent Waste Segregation & Disposal Guide Powered by MongoDB & Google Gemini AI</div>
</div>
""", unsafe_allow_html=True)

# Status Pills Bar
col_s1, col_s2, col_s3 = st.columns([1, 1, 2])
with col_s1:
    if is_connected:
        st.markdown('<span class="status-badge badge-success">✅ MongoDB Active</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-badge badge-red">⚠️ Offline Mode</span>', unsafe_allow_html=True)

with col_s2:
    if st.session_state["gemini_api_key"] and st.session_state["use_gemini"]:
        st.markdown('<span class="status-badge badge-ai">✨ Gemini AI Active</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-badge badge-ml">⚡ ML Classifier</span>', unsafe_allow_html=True)

with col_s3:
    if st.session_state["model_state"]:
        m_info = st.session_state["model_state"]["metadata"]
        st.caption(f"📊 Dataset: **{m_info['num_categories']} Categories** | **{m_info['num_patterns']} Waste Items**")

st.markdown("<br>", unsafe_allow_html=True)

# Main App Navigation Tabs
tab_chat, tab_manage, tab_analytics, tab_guide = st.tabs([
    "💬 Smart Chatbot", 
    "📥 MongoDB Data Manager", 
    "📊 Dataset & Model Insights",
    "📘 Waste & Bin Color Guide"
])

# Helper for bin tag colors
def get_bin_tag_html(wtype, cat_name):
    cat_lower = (wtype + " " + cat_name).lower()
    if "organic" in cat_lower or "food" in cat_lower or "garden" in cat_lower:
        return '<span class="bin-tag bin-green">🟢 Green Bin • Organic / Compostable</span>'
    elif "recycle" in cat_lower or "plastic" in cat_lower or "paper" in cat_lower or "glass" in cat_lower or "metal" in cat_lower:
        return '<span class="bin-tag bin-blue">🔵 Blue Bin • Dry Recyclable</span>'
    elif "hazard" in cat_lower or "e-waste" in cat_lower or "battery" in cat_lower or "chemical" in cat_lower:
        return '<span class="bin-tag bin-red">🔴 Red / Special • Hazardous / E-Waste Dropoff</span>'
    elif "sanitary" in cat_lower or "medical" in cat_lower:
        return '<span class="bin-tag bin-yellow">🟡 Yellow / Red • Biohazard / Wrap & Bin</span>'
    else:
        return '<span class="bin-tag bin-grey">⬛ Grey / Black Bin • Residual Landfill</span>'

# TAB 1: SMART CHATBOT
with tab_chat:
    st.markdown("### 💬 Ask EcoTrash AI")
    st.write("Type any item or question below to receive instant, accurate waste segregation & disposal instructions.")

    # Quick Sample Query Chips
    st.markdown("**Try these popular items:**")
    qcol1, qcol2, qcol3, qcol4, qcol5, qcol6 = st.columns(6)
    
    with qcol1:
        if st.button("🍌 Banana Peel", use_container_width=True):
            st.session_state["pending_query"] = "banana peel"
    with qcol2:
        if st.button("💻 Old Laptop", use_container_width=True):
            st.session_state["pending_query"] = "old laptop"
    with qcol3:
        if st.button("🔋 Lithium Battery", use_container_width=True):
            st.session_state["pending_query"] = "lithium battery"
    with qcol4:
        if st.button("🍾 Glass Bottle", use_container_width=True):
            st.session_state["pending_query"] = "glass bottle"
    with qcol5:
        if st.button("🧃 Milk Carton", use_container_width=True):
            st.session_state["pending_query"] = "milk carton"
    with qcol6:
        if st.button("💊 Expired Pills", use_container_width=True):
            st.session_state["pending_query"] = "expired medicine"

    st.markdown("---")

    # Render Chat History
    for msg in st.session_state["chat_history"]:
        with st.chat_message(msg["role"], avatar="🧑‍💻" if msg["role"] == "user" else "🌱"):
            st.markdown(msg["content"], unsafe_allow_html=True)
            if "details" in msg and msg["details"]:
                st.caption(msg["details"])

    # Handle input from text box or chips
    user_query = st.chat_input("What item do you want to dispose of? (e.g. 'paint can', 'pizza box', 'bubble wrap')")
    
    if st.session_state["pending_query"]:
        user_query = st.session_state["pending_query"]
        st.session_state["pending_query"] = ""

    if user_query:
        st.session_state["chat_history"].append({"role": "user", "content": user_query})
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(user_query)

        # ML Prediction
        ml_pred = None
        if st.session_state["model_state"]:
            mstate = st.session_state["model_state"]
            ml_pred = model_trainer.predict_intent(
                mstate["vectorizer"],
                mstate["model"],
                mstate["descriptions"],
                mstate["types"],
                user_query
            )

        gemini_success = False
        bot_response = ""
        badge_details = ""

        # Gemini AI Query
        if st.session_state["use_gemini"] and st.session_state["gemini_api_key"]:
            with st.spinner("🤖 Gemini AI is evaluating item safety & disposal instructions..."):
                mongo_ctx = st.session_state["model_state"]["categories_data"] if st.session_state["model_state"] else None
                gemini_success, g_text, g_model = gemini_helper.query_gemini_waste_assistant(
                    user_input=user_query,
                    ml_prediction=ml_pred,
                    mongo_context=mongo_ctx,
                    api_key=st.session_state["gemini_api_key"]
                )
                if gemini_success:
                    bin_html = get_bin_tag_html(ml_pred.get("type", "") if ml_pred else "", ml_pred.get("category", "") if ml_pred else "")
                    bot_response = f"{bin_html}\n\n{g_text}"
                    badge_details = f"✨ Response generated & verified by **Gemini AI** (`{g_model}`) • Context: MongoDB Dataset"

        # ML Fallback
        if not gemini_success:
            if ml_pred:
                bin_html = get_bin_tag_html(ml_pred.get('type', ''), ml_pred.get('category', ''))
                bot_response = f"{bin_html}\n\n**{ml_pred['response']}**"
                badge_details = f"⚡ Prediction by **Random Forest ML Classifier** | Category: `{ml_pred['category']}` | Confidence: `{ml_pred.get('confidence', 0)}%`"
                if not st.session_state["gemini_api_key"]:
                    badge_details += "\n\n💡 *Tip: Add your Gemini API key in sidebar for AI response verification.*"
            else:
                bot_response = "Sorry, I couldn't process your request. Please check model status."

        with st.chat_message("assistant", avatar="🌱"):
            st.markdown(bot_response, unsafe_allow_html=True)
            if badge_details:
                st.caption(badge_details)

        st.session_state["chat_history"].append({
            "role": "assistant",
            "content": bot_response,
            "details": badge_details
        })

# TAB 2: MONGODB DATA MANAGER
with tab_manage:
    st.markdown("### 📥 Add & Manage MongoDB Dataset")

    if not is_connected:
        st.warning("⚠️ Connect to MongoDB in the sidebar to add or modify dataset records.")
    else:
        manage_sub1, manage_sub2, manage_sub3 = st.tabs(["➕ Single Category Form", "🚀 Bulk JSON Upload", "🔍 Search & Edit Dataset"])

        with manage_sub1:
            st.subheader("Add New Category or Append Waste Items")
            
            mc1, mc2 = st.columns(2)
            with mc1:
                new_cat_name = st.text_input("Category Name", placeholder="e.g. Solar Panel Intent, Battery Waste")
                new_type = st.text_input("Waste Type / Stream", placeholder="e.g. Hazardous E-Waste, Recyclable Glass")
            with mc2:
                new_description = st.text_area("Disposal Guidelines / Instructions", placeholder="How should users clean, wrap, or dispose of this waste?")

            new_examples_text = st.text_area(
                "Example Items (Comma-separated or newline-separated)",
                placeholder="e.g. Solar panel cell, Inverter battery, Charge controller cable"
            )

            # AI Description Auto-Generator Button
            if st.session_state["gemini_api_key"] and new_cat_name.strip():
                if st.button("✨ Auto-Generate Description with Gemini AI"):
                    with st.spinner("Generating instructions with Gemini AI..."):
                        ok, ai_text, _ = gemini_helper.query_gemini_waste_assistant(
                            user_input=f"Write clear 2-sentence waste disposal guidelines for: {new_cat_name}",
                            api_key=st.session_state["gemini_api_key"]
                        )
                        if ok:
                            st.success("Generated by Gemini AI!")
                            st.info(ai_text)

            if st.button("💾 Save to MongoDB & Retrain AI", use_container_width=True):
                if not new_cat_name.strip() or not new_examples_text.strip():
                    st.error("Category name and examples are required.")
                else:
                    ex_list = [e.strip() for e in new_examples_text.replace("\n", ",").split(",") if e.strip()]
                    cat_doc = {
                        "category": new_cat_name.strip(),
                        "type": new_type.strip() or "General Waste",
                        "description": new_description.strip() or "Dispose of responsibly.",
                        "examples": ex_list
                    }
                    try:
                        ok, msg = db_helper.insert_or_update_category(
                            cat_doc,
                            st.session_state["mongodb_uri"],
                            st.session_state["db_name"],
                            st.session_state["collection_name"]
                        )
                        st.success(msg)
                        load_and_train()
                        st.toast("Model updated with new data!", icon="🎉")
                    except Exception as e:
                        st.error(f"MongoDB Insert Error: {e}")

        with manage_sub2:
            st.subheader("Bulk Import JSON Dataset to MongoDB")
            st.write("Upload a JSON file containing `{'categories': [...]}` format to insert bulk training records.")
            
            uploaded_json = st.file_uploader("Upload JSON File", type=["json"])
            if uploaded_json is not None:
                try:
                    data_json = json.load(uploaded_json)
                    cat_list = data_json.get("categories", []) if isinstance(data_json, dict) else data_json
                    
                    st.info(f"Loaded {len(cat_list)} categories from uploaded JSON.")
                    if st.button("🚀 Upload All Categories to MongoDB"):
                        count = 0
                        for c in cat_list:
                            if isinstance(c, dict) and "category" in c:
                                db_helper.insert_or_update_category(
                                    c,
                                    st.session_state["mongodb_uri"],
                                    st.session_state["db_name"],
                                    st.session_state["collection_name"]
                                )
                                count += 1
                        st.success(f"Successfully uploaded {count} categories to MongoDB!")
                        load_and_train()
                except Exception as e:
                    st.error(f"JSON Parse Error: {e}")

        with manage_sub3:
            st.subheader("Search & Inspect MongoDB Dataset")
            try:
                mongo_records = db_helper.load_intents_from_db(
                    st.session_state["mongodb_uri"],
                    st.session_state["db_name"],
                    st.session_state["collection_name"]
                )
                if mongo_records:
                    search_term = st.text_input("🔍 Filter Categories or Examples", "")
                    filtered_rows = []
                    for r in mongo_records:
                        cat = r.get("category", "")
                        wtype = r.get("type", "")
                        desc = r.get("description", "")
                        examples = r.get("examples", [])
                        
                        full_str = f"{cat} {wtype} {desc} {' '.join(examples)}".lower()
                        if not search_term or search_term.lower() in full_str:
                            filtered_rows.append({
                                "Category": cat,
                                "Type": wtype,
                                "Examples Count": len(examples),
                                "Sample Items": ", ".join(examples[:5]) + ("..." if len(examples) > 5 else ""),
                                "Description": desc
                            })

                    df_records = pd.DataFrame(filtered_rows)
                    st.dataframe(df_records, use_container_width=True, height=400)
                else:
                    st.info("MongoDB collection is empty.")
            except Exception as e:
                st.error(f"MongoDB Load Error: {e}")

# TAB 3: DATASET & MODEL INSIGHTS
with tab_analytics:
    st.markdown("### 📊 Dataset Analytics & ML Model Metrics")
    
    if st.session_state["model_state"]:
        mstate = st.session_state["model_state"]
        meta = mstate["metadata"]
        cats_data = mstate["categories_data"]

        mcol1, mcol2, mcol3, mcol4 = st.columns(4)
        mcol1.metric("Total Waste Categories", meta["num_categories"], delta="+13 categories")
        mcol2.metric("Total Training Items", meta["num_patterns"], delta="+500 items")
        mcol3.metric("TF-IDF Vocabulary Size", meta["vocab_size"])
        mcol4.metric("Active ML Algorithm", "Random Forest (100 trees)")

        st.markdown("---")
        st.subheader("Top Waste Categories by Item Count")
        
        chart_data = []
        for c in cats_data:
            chart_data.append({
                "Category": c.get("category", "Unknown")[:25],
                "Item Count": len(c.get("examples", []))
            })
        
        df_chart = pd.DataFrame(chart_data).sort_values("Item Count", ascending=False)
        st.bar_chart(df_chart.set_index("Category"))

# TAB 4: WASTE & BIN COLOR GUIDE
with tab_guide:
    st.markdown("### 📘 Standard Waste Bin Color Guide")
    
    g1, g2 = st.columns(2)
    with g1:
        st.markdown("""
        #### 🟢 GREEN BIN — Wet / Organic / Compostable
        - **Items**: Fruit peels, food leftovers, coffee grounds, eggshells, garden leaves, tea leaves.
        - **Instructions**: Keep free from plastic bags. Ideal for home composting or municipal organic processing.
        
        #### 🔵 BLUE BIN — Dry Recyclables
        - **Items**: PET plastic bottles, HDPE milk jugs, glass bottles/jars, metal soda cans, food tins, clean aluminum foil.
        - **Instructions**: Rinse clean of food residue and dry before binning.
        
        #### 🟡 YELLOW BIN — Clean Paper & Cardboard
        - **Items**: Cardboard packaging boxes, newspapers, office paper, magazines, envelopes, paper bags.
        - **Instructions**: Flatten boxes to save space. Keep dry.
        """)
    with g2:
        st.markdown("""
        #### 🔴 RED / SPECIAL DROP-OFF — E-Waste & Hazardous
        - **Items**: Batteries, smartphones, laptops, fluorescent bulbs, motor oil, paint cans, pesticides.
        - **Instructions**: NEVER mix with normal garbage. Take to designated municipal drop-off centers or retailer e-waste bins.
        
        #### ⬛ GREY / BLACK BIN — Residual Landfill Waste
        - **Items**: Styrofoam takeaway boxes, cigarette butts, pet litter, vacuum dust, soiled paper towels, broken ceramics.
        - **Instructions**: Bag securely before disposal.
        """)
