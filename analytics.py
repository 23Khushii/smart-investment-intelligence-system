import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# -----------------------------
# Step 1: Load processed data
# -----------------------------
data = pd.read_csv('data/processed/processed_data.csv')
data['Date'] = pd.to_datetime(data['Date'])
data.sort_values(['Symbol', 'Date'], inplace=True)

# Step 2: Calculate returns
data['Daily_Return'] = data.groupby('Symbol')['Close'].pct_change()
data['Cumulative_Return'] = (1 + data['Daily_Return']).groupby(data['Symbol']).cumprod() - 1

# -----------------------------
# Step 3a: Calculate ROI
# -----------------------------
roi = data.groupby('Symbol', group_keys=False).apply(
    lambda x: (x['Close'].iloc[-1] - x['Close'].iloc[0]) / x['Close'].iloc[0]
).reset_index()
roi.columns = ['Symbol', 'ROI']

# -----------------------------
# Step 3b: Calculate Volatility
# -----------------------------
volatility = data.groupby('Symbol')['Daily_Return'].std() * np.sqrt(252)
volatility = volatility.reset_index()
volatility.columns = ['Symbol', 'Volatility']

# -----------------------------
# Step 3c: Calculate Sharpe Ratio
# -----------------------------
mean_daily = data.groupby('Symbol')['Daily_Return'].mean()  # Series with Symbol as index
volatility_series = volatility.set_index('Symbol')['Volatility']
volatility_series.replace(0, np.nan, inplace=True)  # Avoid division by zero
sharpe = (mean_daily * 252) / volatility_series
sharpe = sharpe.reset_index()
sharpe.columns = ['Symbol', 'Sharpe_Ratio']

# Combine all metrics
metrics = roi.merge(volatility, on='Symbol').merge(sharpe, on='Symbol')

# -----------------------------
# Step 4: Predict next-day prices for all stocks
# -----------------------------
predicted_prices = []

for symbol in data['Symbol'].unique():
    df_stock = data[data['Symbol'] == symbol].copy()
    df_stock['Date_ordinal'] = df_stock['Date'].map(pd.Timestamp.toordinal)

    X = df_stock['Date_ordinal'].values.reshape(-1, 1)
    y = df_stock['Close'].values

    model = LinearRegression()
    model.fit(X, y)

    next_day = pd.Timestamp(df_stock['Date'].max() + pd.Timedelta(days=1)).toordinal()
    predicted_price = model.predict([[next_day]])[0]

    predicted_prices.append({'Symbol': symbol, 'Next_Day_Price': predicted_price})

predicted_df = pd.DataFrame(predicted_prices)

# Merge predicted prices with metrics
final_metrics = metrics.merge(predicted_df, on='Symbol')

# Save to CSV
final_metrics.to_csv('data/processed/stock_metrics_with_predictions.csv', index=False)
print("Metrics + next-day predictions saved to 'data/processed/stock_metrics_with_predictions.csv'")

# Preview first 10 rows
print(final_metrics.head(10))

# -----------------------------
# Step 5: Generate Buy/Hold/Sell Recommendation
# -----------------------------
final_metrics['Recommendation'] = final_metrics.apply(
    lambda row: 'Buy' if row['Next_Day_Price'] > data[data['Symbol']==row['Symbol']]['Close'].iloc[-1]
    else ('Sell' if row['Next_Day_Price'] < data[data['Symbol']==row['Symbol']]['Close'].iloc[-1] else 'Hold'),
    axis=1
)

# Save updated CSV with recommendations
final_metrics.to_csv('data/processed/stock_metrics_with_recommendations.csv', index=False)
print("Metrics + predictions + recommendations saved to 'data/processed/stock_metrics_with_recommendations.csv'")

# Preview first 10 rows
print(final_metrics.head(10))
