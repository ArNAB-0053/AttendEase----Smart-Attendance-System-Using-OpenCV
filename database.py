import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "databaseURL":"https://attendancesystemrealtime-default-rtdb.firebaseio.com/"
})


ref = db.reference('StudentDetails')

data = {
    "000": {
        "name":"Elon Musk",
        "batch":"2023",
        "semester":"2nd",
        "total_attendance":8,
        "last_attendance_time":"2023-05-18 09:04:03"
    },

    "007": {
        "name":"Cristiano Ronaldo",
        "batch":"2023",
        "semester":"2nd",
        "total_attendance":2,
        "last_attendance_time":"2023-05-18 09:04:03"
    },

    "017": {
        "name":"AB de Villiars",
        "batch":"2023",
        "semester":"2nd",
        "total_attendance":9,
        "last_attendance_time":"2023-05-18 09:04:03"
    },

    "053": {
        "name":"Arnab Bhattacharyya",
        "batch":"2023",
        "semester":"2nd",
        "total_attendance":14,
        "last_attendance_time":"2023-05-18 09:04:03"
    }
    
}

for key, value in data.items():
    ref.child(key).set(value)