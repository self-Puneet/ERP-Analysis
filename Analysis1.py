from datetime import datetime
import calendar
from google.cloud import firestore
import os
from google.protobuf.timestamp_pb2 import Timestamp
from datetime import datetime

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
print(requests_collection)
input()
# Launch date
launch_date = datetime(2024, 9, 6)

from datetime import datetime
import calendar
from collections import defaultdict

# Launch date
launch_date = datetime(2024, 9, 6)

# Helper function to calculate months passed since the launch date
def months_passed(start_date, end_date):
    return (end_date.year - start_date.year) * 12 + end_date.month - start_date.month

# Function to count requests by sport and month range (0-1, 1-2 months, etc.)
def count_requests_by_sport_and_month(request_collection, launch_date):
    data = {'X': [], 'Y': [], 'Z': []}
    request_counts = defaultdict(int)  # Dictionary to count unique combinations of sport and month

    # Loop through each request in the request_collection
    for request in request_collection.values():
        sport = request['game']
        req_date = request['reqdate']
        
        # Calculate months passed since launch date
        months_diff = months_passed(launch_date, req_date)
        
        # We are interested in requests from the last few months
        if months_diff >= 0:  # Only consider requests after the launch date
            month_name = calendar.month_name[req_date.month]  # Get month name (e.g., "September")
            
            # Update the request count for the unique combination of sport and month
            request_counts[(sport, month_name)] += 1

    # Now populate the X, Y, Z lists based on the unique sport-month combinations
    for (sport, month), count in request_counts.items():
        data['X'].append(sport)
        data['Y'].append(month)
        data['Z'].append(count)
    
    return data

# Function to count item requests by sport and month range
def count_item_requests_by_sport_and_month(request_collection, launch_date):
    data = {'X': [], 'Y': [], 'Z': []}
    request_counts = defaultdict(int)  # Dictionary to count unique combinations of sport and month

    request_requestitems_collection = []
    for i in request_collection.values():
        request_requestitems_collection.append([i["requestitems"], i['reqdate']]) 

    # Loop through requestitems of each request in the request_collection
    for request in request_requestitems_collection:
        sports_items = list(request[0].keys())
        req_date = request[1]
        
        # Calculate months passed since launch date
        months_diff = months_passed(launch_date, req_date)
        
        # We are interested in requests from the last few months
        if months_diff >= 0:  # Only consider requests after the launch date
            month_name = calendar.month_name[req_date.month]  # Get month name (e.g., "September")
            
            for i in range(0, len(sports_items)):

                # Update the request count for the unique combination of sport and month
                request_counts[(sports_items[i], month_name)] += 1

    # Now populate the X, Y, Z lists based on the sport-item-month combinations and request counts
    for (sport_item, month), count in request_counts.items():
        data['X'].append(sport_item)
        data['Y'].append(month)
        data['Z'].append(count)
    
    return data

# Main function to build the final dictionary {X: [], Y: [], Z: []}
def build_sports_analysis_data(request_collection, launch_date):
    # Count requests by sport and month
    analysis_data = count_requests_by_sport_and_month(request_collection, launch_date)
    
    return analysis_data

def build_item_analysis_data(request_collection, launch_date):
    # Count requests by sport, item, and month
    analysis_data = count_item_requests_by_sport_and_month(request_collection, launch_date)
    
    return analysis_data

# Build the dictionary
sports_analysis_data = build_sports_analysis_data(requests_collection, launch_date)
items_analysis_data = build_item_analysis_data(requests_collection, launch_date)


'''
1. Sport-Level Request Dictionary (First Output)
X (Sports): List of requested sports (repeated for multiple requests).
Y (Months): Corresponding months for each request.
Z (Request Counts): Count of requests for each sport in each month.
Description: Tracks request frequency for each sport per month.
'''''
''''
2. Item-Level Request Dictionary (Second Output)
X (Items): List of requested items (specific to sports).
Y (Months): Corresponding months for each item request.
Z (Request Counts): Count of requests for each item in each month.
Description: Tracks request frequency for specific items within sports per month.
'''

print("X: ",sports_analysis_data["X"])
print("Y: ",sports_analysis_data["Y"])
print("Z: ",sports_analysis_data["Z"])

print("X: ",items_analysis_data["X"])
print("Y: ",items_analysis_data["Y"])
print("Z: ",items_analysis_data["Z"])