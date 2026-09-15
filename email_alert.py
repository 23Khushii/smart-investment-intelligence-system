import os
from datetime import datetime

import pandas as pd
import yagmail
from dotenv import load_dotenv


# Load environment variables from .env
load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")


# Check that required credentials are available
if not EMAIL_ADDRESS or not EMAIL_PASSWORD or not RECIPIENT_EMAIL:
    raise ValueError(
        "Email configuration is missing. "
        "Please check your .env file."
    )


# Step 1: Load processed stock data
data = pd.read_csv(
    "data/processed/stock_metrics_with_recommendations.csv"
)


# Step 2: Filter stocks with Buy recommendation
buy_stocks = data[data["Recommendation"] == "Buy"]


# Step 3: Check if any Buy stocks exist
if not buy_stocks.empty:

    # Prepare email content
    message = "Stocks to Buy Today:\n\n"

    for _, row in buy_stocks.iterrows():
        message += (
            f"{row['Symbol']} - "
            f"Predicted Price: {row['Next_Day_Price']:.2f}\n"
        )

    # Step 4: Setup email using credentials from .env
    yag = yagmail.SMTP(
        EMAIL_ADDRESS,
        EMAIL_PASSWORD
    )

    yag.send(
        to=RECIPIENT_EMAIL,
        subject=(
            f"Stock Buy Alert - "
            f"{datetime.today().strftime('%Y-%m-%d')}"
        ),
        contents=message
    )

    print("Alert sent successfully!")

    # Step 5: Log the alert
    with open("alert_log.txt", "a") as f:
        f.write(
            f"{datetime.now()} - "
            f"Email sent with {len(buy_stocks)} stocks\n"
        )

else:
    print("No Buy alerts today.")