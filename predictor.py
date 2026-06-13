from sklearn.linear_model import LinearRegression
import numpy as np

def predict_next_price(chart_df):
    data = chart_df.dropna()
    X = np.arange(len(data)).reshape(-1, 1)
    y = data["price"].values
    
    model = LinearRegression()
    model.fit(X, y)
    
    next_day = np.array([[len(data)]])
    prediction = model.predict(next_day)
    
    return float(prediction[0])