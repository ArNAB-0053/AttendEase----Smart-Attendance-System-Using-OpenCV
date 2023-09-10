import cv2
import time
import os
import pickle
import face_recognition
import numpy as np
import cvzone
from datetime import datetime

import firebase_admin
from firebase_admin import credentials, storage
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "databaseURL":"https://attendancesystemrealtime-default-rtdb.firebaseio.com/",
    "storageBucket":"attendancesystemrealtime.appspot.com"
})


bucket = storage.bucket()

imgBackground = cv2.imread('ImagesPython/background.png')
print(imgBackground.shape)

# Making symbols into list
symbolPath = "ImagesPython/Symbols"
pathList = os.listdir(symbolPath)
# print(pathList)
imgSysmbolList = []
for path in pathList:
    imgSysmbolList.append(cv2.imread(os.path.join(symbolPath, path)))



# Load encode file
print("Loading Encoding File...")
file = open("StudentDetails.p",'rb')
encodingStudentsWithIds = pickle.load(file)
file.close()
encodingStudents, studentIds = encodingStudentsWithIds
# print(studentIds)   # Testing
print("Loading Complete.")


symbol = 0
counter = 0
ids = -1
imgStd = []


cap = cv2.VideoCapture(0)

cap.set(3,640)
cap.set(4,430)
while True:
    succes, frame = cap.read()

    frame_small = cv2.resize(frame, (0,0), None, 0.25,0.25)
    frame_small = cv2.cvtColor(frame_small, cv2.COLOR_BGR2RGB)

    face_cur_frame = face_recognition.face_locations(frame_small)
    encode_cur_frame = face_recognition.face_encodings(frame_small, face_cur_frame)


    imgBackground[298:298+480, 54:54+640] = frame
    imgBackground[16:16+791, 775:775+666] = imgSysmbolList[symbol]

    if face_cur_frame:
        for encode_face, face_location in zip(encode_cur_frame,face_cur_frame):
            matches = face_recognition.compare_faces(encodingStudents, encode_face)
            face_dis = face_recognition.face_distance(encodingStudents, encode_face)

            ## Testing
            # print("matches: ", matches)
            # print("face distance:", face_dis)

            matches_index = np.argmin(face_dis)
            # print("Match Index: ",matches_index) #Testing


            if matches[matches_index]:
                ## Rectangle over face
                y1,x2, y2,x1 = face_location
                y1,x2, y2,x1 = y1*4,x2*4, y2*4,x1*4 
                bbox = 54+x1, 298+y1, x2-x1, y2-y1
                imgBackground = cvzone.cornerRect(imgBackground,bbox, rt=0)
                ids = studentIds[matches_index]
                # print(ids)

                if counter==0:
                    cvzone.putTextRect(imgBackground, "loading...", (275,400))
                    cv2.imshow("Attendance System", imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    symbol = 1


        
        if counter!=0:
            if counter==1:
                ## Getting the data
                StudentInfo = db.reference(f'StudentDetails/{ids}').get()
                print(StudentInfo)

                ## Getting the image
                blob = bucket.get_blob(f'Images/Student/{ids}.png')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgStd = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)

                ## Update data
                # print(datetime.now())
                #### Upadating last attendance
                dt = datetime.strptime(StudentInfo['last_attendance_time'],
                                    '%Y-%m-%d %H:%M:%S')
                second_cal = (datetime.now()-dt).total_seconds()
                # print(datetime.now())
                # print(second_cal)
                

                #### Upadating attendance
                if second_cal>20:
                    ref = db.reference(f'StudentDetails/{ids}')
                    StudentInfo['total_attendance'] += 1
                    ref.child('total_attendance').set(StudentInfo['total_attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                else:
                    symbol = 3
                    counter = 0
                    imgBackground[16:16+791, 775:775+666] = imgSysmbolList[symbol]


            if symbol != 3:
                if 10<counter<20:
                    symbol = 2
                imgBackground[16:16+791, 775:775+666] = imgSysmbolList[symbol]


                if counter<=10:
                    cv2.putText(
                        imgBackground,
                        str(StudentInfo['name']),
                        (950,467),
                        cv2.FONT_HERSHEY_COMPLEX,
                        1,
                        (0,0,0),2
                    )

                    cv2.putText(
                        imgBackground,
                        str(ids),
                        (880,524),
                        cv2.FONT_HERSHEY_COMPLEX,
                        1,
                        (0,0,0),2
                    )

                    cv2.putText(
                        imgBackground,
                        str(StudentInfo['semester']),
                        (1025,581),
                        cv2.FONT_HERSHEY_COMPLEX,
                        1,
                        (0,0,0),2
                    )

                    cv2.putText(
                        imgBackground,
                        str(StudentInfo['batch']),
                        (957,640),
                        cv2.FONT_HERSHEY_COMPLEX,
                        1,
                        (0,0,0),2
                    )
                    

                    cv2.putText(
                        imgBackground,
                        str(StudentInfo['total_attendance']),
                        (1050,697),
                        cv2.FONT_HERSHEY_COMPLEX,
                        1,
                        (0,0,0),2
                    )

                    cv2.putText(
                        imgBackground,
                        str(StudentInfo['last_attendance_time']),
                        (1060,751),
                        cv2.FONT_HERSHEY_COMPLEX,
                        0.8,
                        (0,0,0),2
                    )

                    #### Profile image
                    imgBackground[76:76+303,986:986+216] = imgStd

            counter+=1


            if counter>=20:
                counter = 0
                symbol = 0
                StudentInfo = []
                imgStd = []
                imgBackground[16:16+791, 775:775+666] = imgSysmbolList[symbol]
    
    else:
        symbol = 0
        counter = 0

    cv2.imshow("Attendance System", imgBackground)

    if cv2.waitKey(10) == ord('0'):
        break

if matches[matches_index]:
    print(f"{studentIds[matches_index]} is Present")

cap.release()
cv2.destroyAllWindows() 