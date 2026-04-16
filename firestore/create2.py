import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

doc = {
  "name": "周辰恩",
  "mail": "s1131262@pu.edu.tw",
  "lab": 156
}

doc_ref = db.collection("靜宜資管").document("Amy")
doc_ref.set(doc)
