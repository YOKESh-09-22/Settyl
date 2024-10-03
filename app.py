import streamlit as st
import random
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Initialize Sentiment Analyzer
analyzer = SentimentIntensityAnalyzer()

# Function to get sentiment score from user's input
def get_sentiment(user_input):
    sentiment = analyzer.polarity_scores(user_input)
    return sentiment['compound']  # Compound score for overall sentiment

# Function to extract numeric value from user input
def extract_price(user_input):
    prices = re.findall(r'\d+', user_input)
    if prices:
        return int(prices[0])  # Return the first numeric value found
    return None

# Pricing logic
PRODUCTS = {
    "Laptop": {"max_price": 1000, "min_price": 700, "start_price": 850},
    "Smartphone": {"max_price": 800, "min_price": 500, "start_price": 650},
    "Headphones": {"max_price": 300, "min_price": 150, "start_price": 200},
}

# Function to apply a discount based on sentiment and handle negotiation
def negotiate(user_offer, product, initial_discount):
    min_price = PRODUCTS[product]['min_price']
    start_price = PRODUCTS[product]['start_price']

    # Calculate fixed discounted price based on initial discount
    discounted_price = start_price - initial_discount

    # 1. Accept the user's offer if it meets or exceeds the discounted price
    if user_offer >= discounted_price:
        return f"Congratulations! We accept your offer of ${user_offer} for the {product}. A discount of ${initial_discount} has been applied due to your feedback."

    # 2. If the user's offer is below the minimum price
    if user_offer < min_price:
        return f"Sorry, the minimum price for the {product} is ${min_price}. Your offer of ${user_offer} is too low."

    # 3. Provide a counter-offer with the discounted price
    return f"We can't accept your offer of ${user_offer}, but we can offer the {product} for ${discounted_price}. A discount of ${initial_discount} has been applied due to your feedback. How does that sound?"

# Initialize the Streamlit app
st.set_page_config(page_title="Negotiation Chatbot", layout="centered")

st.markdown(
    """
    <style>
    .chatbox {
        background-color: #f1f1f1;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .user-message {
        background-color: #d9fdd3;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
        text-align: left;
    }
    .bot-message {
        background-color: #ffffff;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
        text-align: right;
    }
    </style>
    """, unsafe_allow_html=True
)

st.header("Negotiation Chatbot")

# Initialize session state for chat history and initial discount
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'initial_discount' not in st.session_state:
    st.session_state['initial_discount'] = None

# Let user select a product
product_choice = st.selectbox("Select a product to negotiate:", list(PRODUCTS.keys()))
start_price = PRODUCTS[product_choice]['start_price']

st.subheader(f"Starting negotiation for a {product_choice}. The initial price is ${start_price}.")

# Get user input
user_input = st.text_input("Enter your price offer or message:", key="input")
submit = st.button("Submit your offer")

# Main negotiation process
if submit and user_input:
    user_offer = extract_price(user_input)
    
    if user_offer is not None:
        # Get sentiment analysis on user input
        sentiment_score = get_sentiment(user_input)

        # Determine initial discount based on sentiment score only once per negotiation session
        if st.session_state['initial_discount'] is None:
            if sentiment_score > 0.5:  # Positive sentiment
                st.session_state['initial_discount'] = random.randint(30, 50) 
            elif 0 <= sentiment_score <= 0.5:  # Neutral sentiment
                st.session_state['initial_discount'] = random.randint(10, 30) 
            else:  # Negative sentiment
                st.session_state['initial_discount'] = random.randint(5, 15) 

        initial_discount = st.session_state['initial_discount']

        # Add user offer to chat history
        st.session_state['chat_history'].append(("user", f"Offered: ${user_offer} - Message: {user_input}"))

        # Apply negotiation logic with fixed discount
        negotiation_response = negotiate(user_offer, product_choice, initial_discount)
        
        # Save bot responses to chat history
        st.session_state['chat_history'].append(("bot", negotiation_response))

    else:
        st.error("Please enter a valid price in your message.")

# Display chat history with a real chat interface
st.subheader("Chat History")
for role, text in st.session_state['chat_history']:
    if role == "user":
        st.markdown(f"<div class='chatbox user-message'>{text}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chatbox bot-message'>{text}</div>", unsafe_allow_html=True)
