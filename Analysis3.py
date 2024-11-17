from collections import defaultdict
from datetime import datetime
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

def build_pie_chart_data ():
    # Step 1: Create a dictionary for delayed requests
    delayed_requests = defaultdict(int)

    # Loop through requests to identify delayed returns
    for request in requests_collection.values():
        game = request.get('game')  # Get the game type from the request
        return_date = request.get('returnDate')
        actual_return_date = request.get('act_returntime')
        
        # Check if the return is delayed
        if (type(actual_return_date) == type(return_date)):
            if actual_return_date > return_date:
                delayed_requests[game] += 1

    # Step 2: Calculate the total number of requests (TOTAL) and number of on-time requests
    TOTAL = len(requests_collection)  # Total number of requests
    on_time_requests = TOTAL - sum(delayed_requests.values())  # On-time requests are the remaining ones

    # Step 3: Create the pie chart label dictionary
    label_dict = {}

    # Add the 'onTimeReturn' label with description
    label_dict['onTimeReturn'] = [
        (on_time_requests / TOTAL) * 100,  # Percentage of on-time requests
        "request with no delay in return"  # Description for on-time requests
    ]

    # Add delayed requests for each game
    for game, delayed_count in delayed_requests.items():
        label_dict[game] = [
            (delayed_count / TOTAL) * 100,  # Percentage of delayed requests for this game
            f"delayed request for {game}"  # Description for delayed requests
        ]

    return label_dict

pie_chart_data = build_pie_chart_data()

# Final pie chart labels dictionary is ready
print("Pie Chart Labels Dictionary:", pie_chart_data)
