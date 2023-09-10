import cv2
import face_recognition
import pickle
import os



import firebase_admin
from firebase_admin import credentials, storage
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "databaseURL":"https://attendancesystemrealtime-default-rtdb.firebaseio.com/",
    "storageBucket":"attendancesystemrealtime.appspot.com"
})

# Making symbols into list
studentPath = "Images/Student"
pathList = os.listdir(studentPath)
# print(pathList)

imgStudentList = []
studentIds = []
for path in pathList:
    imgStudentList.append(cv2.imread(os.path.join(studentPath, path)))
    # print(path)
    # print(os.path.splitext(path)[0]) # "0" to get ids without .jpg
    studentIds.append(os.path.splitext(path)[0])


    # fileName = f"{studentPath}/{path}"  # also correct
    occ = "Student" # Later it will be changed in Sudent or teacher or other
    fileName = f"Images/{occ}/{path}"
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)

print(studentIds)


def findEncodings(imagesList):
    enlist = []
    
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        face_encodings = face_recognition.face_encodings(img)
        
        if len(face_encodings) > 0:
            encode = face_encodings[0]
            enlist.append(encode)
        else:
            print("No face detected in an image")
            continue

    return enlist

print("Encoding Start...")
encodingStudents = findEncodings(imgStudentList)
# print(encodingStudents)   # Testing
encodingStudentsWithIds = [encodingStudents, studentIds]
print("Encoding End.")


file = open("StudentDetails.p","wb")
pickle.dump(encodingStudentsWithIds,file)
file.close()
print("File saved.")