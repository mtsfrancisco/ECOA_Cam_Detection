import firebase_admin
import os
from firebase_admin import credentials, db

# Get the service account key from the Firebase project settings
# Gear icon > Project settings > Service accounts > Generate new private key

cred = credentials.Certificate(os.path.join(os.path.dirname(__file__), './serviceAccountKey.json'))

# Intializing app with service account, granting admin privileges
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://ecoa-camera-default-rtdb.firebaseio.com/'
})

# Functions to handle users branch

def add_user(user_id, name, image_64):
    ref = db.reference(f'users/{user_id}')
    ref.set({
        'name': name,
        'image_64': image_64
    })

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