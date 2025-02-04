import firebase_admin
import os
from firebase_admin import credentials, db

# Get the service account key from the Firebase project settings
# Gear icon > Project settings > Service accounts > Generate new private key
# Save the file in the same directory as this file > Filename: serviceAccountKey.json

service_account_path = os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')
cred = credentials.Certificate(service_account_path)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://ecoa-camera-default-rtdb.firebaseio.com'
})

# Functions to handle users branch

def add_user(user_id, user_data, image_64):
    ref = db.reference(f'users/{user_id}')
    ref.set(user_data)

def get_user(user_id):
    ref = db.reference(f'users/{user_id}')
    return ref.get()

def update_user(user_id, name=None, image_64=None):
    ref = db.reference(f'users/{user_id}')
    updates = {}
    if name:
        updates['name'] = name
    if image_64:
        updates['image_64'] = image_64
    ref.update(updates)

def delete_user(user_id):
    ref = db.reference(f'users/{user_id}')
    ref.delete()

def get_all_users():
    ref = db.reference('users')
    return ref.get()