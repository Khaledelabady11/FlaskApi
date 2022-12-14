"""
    API REST con Python 3 y SQLite 3
"""
from flask import Flask, jsonify, request, redirect ,render_template
import person_controller
import faces_controller
import face_recognition
from db import create_tables
import json
import cloudinary
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url
from PIL import Image
import urllib.request
import ast
import numpy as np

app = Flask(__name__)

cloudinary.config(
  cloud_name = "khaledelabady11",
  api_key = "772589215762873",
  api_secret = "6EtKMojSfmrBn3t2UMH2wrAODCA"
)

def uploader(file):
    result = cloudinary.uploader.upload(file)
    return result["secure_url"]

# You can change this to any folder on your system
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def detect_faces_in_image(person_id):
    person = person_controller.get_by_id(person_id)
    response = urllib.request.urlopen(person[5])
    image = face_recognition.load_image_file(response)
    face_encodings = face_recognition.face_encodings(image)[0]
    json_data= json.dumps(face_encodings.tolist())
    result = faces_controller.insert_face(person_id,json_data)
    return jsonify(result)



@app.route('/person', methods=['GET', 'POST'])
def upload_image():

    # Check if a valid image file was uploaded
    if request.method == 'POST':
        name = request.form.get("name")
        message = request.form.get("message")
        age = request.form.get("age")
        description = request.form.get("description")
        file =request.files["file"]
        image= uploader(file)
        result = person_controller.insert_person(name,age,message,description,image)
        return jsonify(result)


    # If no valid image file was uploaded, show the file upload form:
    return render_template("form.html")


@app.route('/api/persons', methods=["GET"])
def get_persons():
    persons = person_controller.get_persons()
    person_list = []
    for person in persons:
        # detect_faces_in_image(person[0])
        person_list.append(
            {
                "id": person[0],
                "name": person[1],
                "age": person[2],
                "description": person[3],
                "message": person[4],
                "image": person[5]
            }
        )
    return jsonify(person_list)


@app.route('/persons', methods=["GET"])
def list_persons():
    persons = person_controller.get_persons()

    return render_template("index.html",data = persons)


@app.route("/api/persons", methods=["POST"])
def insert_person():
    person_details = request.get_json()
    name = person_details["name"]
    file = person_details["image"]
    image = uploader(file)
    message = person_details["message"]
    age = person_details["age"]
    description = person_details["description"]
    result = person_controller.insert_person(name,age,description, message,image)
    return jsonify(result)


@app.route("/api/persons/<id>", methods=["PUT"])
def update_person(id):
    person_details = request.get_json()
    name = person_details["name"]
    message = person_details["message"]
    result = person_controller.update_person(id,name, message)
    return jsonify(result)


@app.route("/api/persons/<id>", methods=["DELETE"])
def delete_person(id):
    result = person_controller.delete_person(id)
    return jsonify(result)


@app.route("/api/persons/<id>", methods=["GET"])
def get_person_by_id(id):
    person = person_controller.get_by_id(id)
    json_str= {
                "id": person[0],
                "name": person[1],
                "age": person[2],
                "description": person[3],
                "message": person[4],
                "image": person[5]
            }
    return jsonify(json_str)


#get Face_encodings
@app.route('/api/faces', methods=["GET"])
def get_faces():
    faces = faces_controller.get_faces()
    face_list = []
    for face in faces:
        face_list.append(
            {
                "person_id": face[0],
                "data": face[1],
                # "created_on": person["created_on"],
            }
        )
    return jsonify(face_list)

@app.route("/similar")
def find_similar():
    persons = person_controller.get_persons()
    person= person_controller.get_by_id(10)
    response = urllib.request.urlopen(person[5])
    image = face_recognition.load_image_file(response)
    p1= face_recognition.face_encodings(image)
    for x in persons:
        if x[0]==10:
            continue
        response2 = urllib.request.urlopen(x[5])
        image2 = face_recognition.load_image_file(response2)
        p2 =face_recognition.face_encodings(image2)
        if len(p1) > 0:

             match_results = face_recognition.compare_faces([p1[0]], p2[0])
             if match_results[0] == True:
               str = "May be the person with id = {}"
               return jsonify(str.format(x[0]))



    return jsonify(json.dumps("not exited"))


if __name__ == "__main__":
    create_tables()
    """
    Here you can change debug and port
    Remember that, in order to make this API functional, you must set debug in False
    """
    app.run(host='0.0.0.0', port=8000, debug=False)
