from collections import defaultdict
from datetime import datetime
from google.cloud import firestore
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


# Helper function to calculate delay in days between two dates
def calculate_delay(return_date, actual_return_date):
    return (actual_return_date - return_date).days

# Function to calculate the delayed returns and average delay
def calculate_delayed_returns(request_collection):
    # Dictionary to store the delayed requests for each student
    student_delays = defaultdict(list)

    # Iterate through each request in the collection
    for request in request_collection.values():
        return_date = request['returnDate']
        actual_return_date = request['act_returntime']
        
        # Check if the return is delayed
        if type(actual_return_date) == type(return_date):
            if actual_return_date > return_date:
                # Calculate the delay in days
                delay_days = calculate_delay(return_date, actual_return_date)
                # Store the delay for the student (org_name)
                student_delays[request['org_name']].append(delay_days)

    # Now calculate the top 5 students with the most delayed returns
    delay_counts = {}
    for student, delays in student_delays.items():
        delay_counts[student] = {
            'count': len(delays),  # Count of delays for the student
            'average_delay': sum(delays) / len(delays)  # Average delay for the student
        }

    # Sort the students by the count of delayed returns in descending order and pick top 5
    sorted_delays = sorted(delay_counts.items(), key=lambda x: x[1]['count'], reverse=True)[:5]

    # Prepare the final dictionary in the required format
    final_data = {}
    for student, data in sorted_delays:
        final_data[student] = [data['count'], round(data['average_delay'], 2)]

    return final_data

# Call the function to get the delayed return analysis for the top 5 students
delayed_returns_data = calculate_delayed_returns(requests_collection)

# Output the result
print("Top 5 Students with Most Delayed Returns:")
print(delayed_returns_data)
