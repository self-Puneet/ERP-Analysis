from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict
from sklearn.linear_model import LinearRegression
from collections import defaultdict
from google.cloud import firestore
from google.protobuf.timestamp_pb2 import Timestamp

# Set GOOGLE_APPLICATION_CREDENTIALS to your Firebase service account file
# --------------------------- API key here ---------------------------

def create_object(collection_name):
    # Initialize Firestore client
    db = firestore.Client()
    # Reference to the collection
    collection_ref = db.collection(collection_name)

    # Fetch all documents in the collection
    docs = collection_ref.stream()
    docs_dic = {}
    for doc in docs:
        doc_dict = doc.to_dict()
        for i in ['act_returntime', 'reqdate', 'returnDate']:
            doc_dict[i] = datetime.strptime(str(doc_dict[i]).split(" ")[0], '%Y-%m-%d').date() if i in doc_dict.keys() else None
        docs_dic[doc.id] = doc_dict

    return docs_dic

requests_collection = create_object("requests")

# Launch date
launch_date = datetime(2024, 9, 6)

# Helper function to calculate the start of the week for a given date
def get_start_of_week(date):
    return date - timedelta(days=date.weekday())

# Function to count requests by week since launch date
def count_requests_by_week(request_collection, launch_date):
    week_counts = defaultdict(int)
    
    # Convert launch_date to datetime.date for consistency
    launch_date = launch_date.date()
    
    for request in request_collection.values():
        req_date = request['reqdate']
        
        # Calculate the start of the week for the request date
        start_of_week = get_start_of_week(req_date)
        
        # Calculate the weeks passed since the launch date
        weeks_since_launch = (start_of_week - launch_date).days // 7
        
        # Only consider requests after the launch date
        if weeks_since_launch >= 0:
            week_counts[weeks_since_launch] += 1
    
    return week_counts

# Function to calculate moving average
def calculate_moving_average(Y1):
    moving_avg = []
    for i in range(len(Y1)):
        moving_avg.append(np.mean(Y1[:i+1]))  # Average up to the current week
    return moving_avg

# Function to perform linear regression for data up to week X
def calculate_linear_regression_up_to_week(X, Y1):
    # Only use data from week 0 to X-1 to predict for week X
    X_data = np.array(list(range(X))).reshape(-1, 1)  # Weeks 0 to X-1
    Y_data = np.array(Y1[:X])  # Request counts for weeks 0 to X-1
    
    reg = LinearRegression()
    reg.fit(X_data, Y_data)  # Fit the model using weeks (X) and request counts (Y1)
    
    # Predict for the current week (week X)
    prediction = reg.predict([[X]])
    return prediction[0]  # The predicted value for week X

# Function to prepare the output data structure
def prepare_data_for_output(week_counts):
    sorted_weeks = sorted(week_counts.keys())
    sorted_counts = [week_counts[week] for week in sorted_weeks]
    
    # Calculate moving average
    moving_avg = calculate_moving_average(sorted_counts)
    
    # Calculate linear regression predictions
    Y3 = []
    for X in range(1, len(sorted_weeks) + 1):  # Start from week 1 to avoid fitting model on 0 data
        Y3.append(calculate_linear_regression_up_to_week(X, sorted_counts))
    
    # Prepare the output dictionary with X, Y1 (weekly requests), Y2 (moving average), Y3 (linear regression)
    return {
        "X": sorted_weeks,
        "Y1": sorted_counts,
        "Y2": moving_avg,
        "Y3": Y3
    }

# Main function to track request trends with moving average and linear regression
def track_request_trends(request_collection, launch_date):
    # Get request counts by week since launch
    week_counts = count_requests_by_week(request_collection, launch_date)
    
    # Prepare data for output format with Y1, Y2, Y3
    return prepare_data_for_output(week_counts)

# Get the data for plotting
trend_data = track_request_trends(requests_collection, launch_date)

# Output the result
print("Request Trends Data (X, Y1, Y2, Y3):", trend_data)


import matplotlib.pyplot as plt

# Function to plot the trends (Y1, Y2, Y3)
def plot_trends(trend_data):
    X = trend_data["X"]
    Y1 = trend_data["Y1"]
    Y2 = trend_data["Y2"]
    Y3 = trend_data["Y3"]
    
    # Create the plot
    plt.figure(figsize=(10, 6))

    # Plot each line
    plt.plot(X, Y1, label="Actual Requests (Y1)", marker='o', linestyle='-', color='b')
    plt.plot(X, Y2, label="Moving Average (Y2)", marker='s', linestyle='--', color='g')
    plt.plot(X, Y3, label="Linear Regression (Y3)", marker='^', linestyle='-.', color='r')

    # Add labels and title
    plt.xlabel("Weeks since Launch")
    plt.ylabel("Number of Requests")
    plt.title("Request Trends Over Time with Moving Average and Linear Regression")
    
    # Add grid, legend, and show plot
    plt.grid(True)
    plt.legend()
    plt.show()

# Plot the data using the function
plot_trends(trend_data)
