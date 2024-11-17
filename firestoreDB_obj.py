import pickle
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

    with open(f"{collection_name}.pkl", "wb") as pickle_file:
        pickle.dump(docs_dic, pickle_file)

create_object("requests")
create_object("inventory")
create_object("userRoles")