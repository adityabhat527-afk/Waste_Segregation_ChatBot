# 🗑️ Waste Segregation Chatbot  

## 🚀 Overview  
This **Waste Segregation Chatbot** helps users determine how to properly dispose of various waste items. It uses **Machine Learning (Random Forest Classifier)** to classify user input into waste categories and provides appropriate disposal instructions. Built with **Streamlit**, it offers an interactive chat interface for easy and efficient waste disposal guidance.  

---

## 🎯 Features  
✅ **Intelligent Waste Classification** – Identifies the category of waste based on user input.  
✅ **Machine Learning Powered** – Uses **TF-IDF Vectorization** and **Random Forest** for text classification.  
✅ **Interactive Chat Interface** – Built with **Streamlit** for a seamless user experience.  
✅ **WellIntent Handling** – Recognizes and responds to gratitude-based inputs like *"Thank you"* or *"Thanks"*.  
✅ **Fallback Intent** – Provides helpful responses when uncertain about a classification.  

---

## 📦 Installation  

### 1️⃣ Clone the Repository  

git clone https://github.com/Santhosh944/Waste_Segregation_Chatbot.git  
cd Waste_Segregation_Chatbot  

🌐 Live Demo
👉 [Launch Riya Now](https://waste-segregation-chatbot.onrender.com/)

2️⃣ Install Dependencies  
Ensure you have Python 3.8+ installed. Then, install the required packages:  
pip install -r requirements.txt

3️⃣ Run the Chatbot  
Launch the chatbot using Streamlit:  
streamlit run app.py

## 🛠️ Technologies Used  
- Python – Primary programming language  
- scikit-learn – Machine learning model for waste classification  
- Streamlit – Web-based chatbot interface  
- TF-IDF Vectorization – Converts text into numerical features  
- Random Forest Classifier – Trained model for waste category predictions  
- JSON – Stores waste category data

## 🏗️ How It Works  
1️⃣ User inputs an item (e.g., "plastic bottle").  
2️⃣ The input is vectorized using TF-IDF.  
3️⃣ The Random Forest model predicts the waste category.  
4️⃣ The chatbot provides disposal instructions.  
5️⃣ If unsure, it responds with a fallback message.  


🏆 Example Usage
User: "banana peel"  
Bot: "This is Organic Waste. Dispose of it in a compost bin."  

User: "Thank you!"  
Bot: "You're welcome! 😊"

## 📌 Future Improvements  
🔹 Expand Training Data – Add more waste categories and examples.  
🔹 Improve Model Accuracy – Tune the ML model for better predictions.  
🔹 Multilingual Support – Enable chatbot responses in multiple languages.  
🔹 Mobile & Web App Deployment – Make it accessible via mobile/web apps.

## 📷 Interface Preview
![image](https://github.com/user-attachments/assets/c900ee0c-d2bc-4bd1-b708-0922371628dc)

📜 License  
This project is open-source under the MIT License.

📧 Contact  
📌 GitHub: Santhosh944  
📌 Email: santhoshsanthosh7098200@gmail.com  

🚀 Let's make waste disposal smarter and greener! 🌱♻️
