from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from rest_framework_jwt.settings import api_settings
from .models import User, UserProduct, Pet, Product, Diary, IotWaterIntake # add more data
from django.db import connection
from datetime import datetime

import base64 
import io 
import json

### Iot
def FoodIntake(request):
    if request.method == 'POST':
        
        data = json.loads(request.body)
        FoodIntake = data.get('FoodIntake')
        current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO IotFoodIntake (date, food_intake) VALUES (%s, %s)", [current_date, FoodIntake])
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT date, food_intake FROM IotFoodIntake")
            total_food_intake = cursor.fetchall()

        total_food_intake_list = [(date, food_intake) for date, food_intake in total_food_intake]

        return HttpResponse(f"IotFoodIntake insert successful! Here's all the food_intake: {total_food_intake_list}")
    else:
        return HttpResponseBadRequest()

def WaterIntake(request):
    if request.method == 'POST':

        data = json.loads(request.body)
        water_intake = data.get('WaterIntake')
        current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO IotWaterIntake (date, water_intake) VALUES (%s, %s)", [current_date, water_intake])
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT date, water_intake FROM IotWaterIntake")
            total_water_intake = cursor.fetchall()
        
        total_water_intake_list = [(date, water_intake) for date, water_intake in total_water_intake]

        return HttpResponse(f"IotWaterIntake insert successful! Here's all the water_intake: {total_water_intake_list}")

    else:
        return HttpResponseBadRequest()

def Weight(request):
    if request.method == 'POST':

        data = json.loads(request.body)
        weight = data.get('Weight')
        current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO IotWeight (date, weight) VALUES (%s, %s)", [current_date, weight])
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT date, weight FROM IotWeight")
            total_weight = cursor.fetchall()
        
        total_weight_list = [(date, weight) for date, weight in total_weight]

        return HttpResponse(f"IotWeight insert successful! Here's all the weight: {total_weight_list}")

    else:
        return HttpResponseBadRequest()

### Dress Up ###
def GetDressPageInfo(request):
    if request.method == 'POST':

        data = json.loads(request.body)
        userID = data.get('userID')
        petID = data.get('petID')

        dress_up_product_list = []
        money = 0
        
        # get user money
        with connection.cursor() as cursor:
            cursor.execute("SELECT money FROM User WHERE userid = %s", [userID])
            money = cursor.fetchone()

        # get which product user has and where it puts
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM UserProduct WHERE userid = %s", [userID])
            user_product = cursor.fetchone()
        
        if user_product:
            for productid, description, posX, posY in user_product:
                query = f"SELECT image FROM Product WHERE productid = %s"
                product_image = ""
                with connection.cursor() as cursor:
                    cursor.execute(query, [productid])
                    product_image = cursor.fetchone()

                dress_up_product = {
                    "Image": product_image,
                    "posX": str(posX),
                    "posY": str(posY)
                }

                dress_up_product_list.append(dress_up_product)
        
        # get shop product
        with connection.cursor() as cursor:
            cursor.execute("SELECT price, image FROM Product")
            shop_products = cursor.fetchall()
        
        all_shop_product = [(price, image) for price, image  in shop_products]
        all_shop_product_list = []

        for price, image in all_shop_product:
            shop_product = {
                "price": str(price),
                "image": image
            }
            all_shop_product_list.append(shop_product)

        response_data = {
            "money": str(money),
            "DressUpProduct": dress_up_product_list,
            "ShopProduct": all_shop_product_list
        }

        response_data = json.dumps(response_data)

        return HttpResponse(response_data)

    else:
        return HttpResponseBadRequest()


### Login Page ### 
def login(request):
    if request.method == 'POST':

        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        # check if user exsits or password is incorrect
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM User WHERE username = %s AND password = %s", [username, password])
            user_data = cursor.fetchone()

        if user_data:
            return HttpResponse("Login successful!")
        else:
            return HttpResponseBadRequest("Username or password is incorrect.")
    else:
        return HttpResponseBadRequest()

def register(request):
    if request.method == 'POST':

        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        breed = data.get('breed')
        petName = data.get('petName')
        age = data.get('age')
        gender = data.get('gender')

        credentials = f"{username}_{password}"
        pet_credentials = f"{username}_{petName}"
        userID = credentials
        petid = pet_credentials
        money = 1000

        # check if username exists
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM User WHERE username = %s", [username])
            username_exists = cursor.fetchone()[0]

        if username_exists > 0:
            return HttpResponse("Username already exists!")

        # check password is null
        if not password:
            return HttpResponseBadRequest("Password is null!")
        
        # check petName is null
        if not petName:
            return HttpResponseBadRequest("petName is null!")
        
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO User (userid, username, password, money) VALUES (%s, %s, %s, %s)", [userID, username, password, money])
            cursor.execute("INSERT INTO Pet (userid, petid, name, breed, gender, age) VALUES (%s, %s, %s, %s, %s, %s)", [userID, petid, petName, breed, gender, age])
        
        response_data = {
            "userID" : userID,
            "petID" : petid
        }

        response_data = json.dumps(response_data)

        return HttpResponse(response_data)
    else:
        return HttpResponseBadRequest()



#################################################################################################

def get_all_user(request):
    if request.method == 'GET':
        with connection.cursor() as cursor:
            cursor.execute("SELECT username, password FROM User")
            users = cursor.fetchall()

        user_credentials = [(username, password) for username, password in users]
        return HttpResponse(f"All the users: {user_credentials}")
    else:
        return HttpResponseBadRequest("Invalid request method")

def delete_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        with connection.cursor() as cursor:

            # Check if the user exists before deleting
            cursor.execute("SELECT * FROM User WHERE username = %s", [username])
            user_exists = cursor.fetchone()

            if user_exists:
                cursor.execute("DELETE FROM User WHERE username = %s", [username])
                return HttpResponse(f"User '{username}' deleted successfully.")
            else:
                return HttpResponseBadRequest(f"User '{username}' not found.")
    else:
        return HttpResponseBadRequest("Invalid request method")



# add a new pet for a user
def add_pet(request):
    if request.method == 'POST':
        userid = request.POST.get('userid')
        breed = request.POST.get('breed')
        name = request.POST.get('name')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        image_b64 = request.POST.get('image')
        weight = request.POST.get('weight')

        # Convert the base64-encoded image to a binary format
        image_bytes = base64.b64decode(image_b64)
        image = io.BytesIO(image_bytes)

        # insert a new record into Pet table
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO Pet (userid, breed, name, age, gender, image, weight) VALUES (%s, %s, %s, %s, %s, %s)",[userid, breed, name, age, gender, image, weight]) 
            pet_id = cursor.lastrowid

        # return the pet id as a response
        return HttpResponse(pet_id)
    else:
        return HttpResponseBadRequest()

# add a photo for a diary entry
def add_photo(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        image_b64 = request.POST.get('image')

        #convert the base64-encoded image into a binary format
        image_bytes = base64.b64decode(image_b64)
        image = io.BytesIO(image_bytes)

        # update the image field of the Diary table
        with connection.cursor() as cursor:
            cursor.execute("UPDATE Diary SET image = %s WHERE date = %s", [image, date])

        # return a success message as a response
        return HttpResponse("Photo added successfully!")
    else:
        return HttpResponseBadRequest()



### NEED CHECK AGAIN ###  

# get the history of a pet's diary entries
def get_history(request):
    if request.method == 'POST':
        userid = request.POST.get('userid')
        pet_id = request.POST.get('pet_id')
        date = request.POST.get('date')

        # query the Diary table for the matching records
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Diary WHERE PetID = %s AND date = %s", [pet_id, date])
            diary_data = cursor.fetchall()

        # convert the query result into a JSON format
        diary_json = json.dumps(diary_data)

        # return the JSON data as a response
        return HttpResponse(diary_json)
    else:
        return HttpResponseBadRequest()



#get the pet information for a user
def get_pet_info(request): 

    if request.method == "POST": 
        userid = request.POST.get("userid") 
        petid = request.POST.get("petid")
    else:
        return HttpResponseBadRequest("Invalid request method")

    # check if the user and pet exist
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM User WHERE userid = %s", [userid])
        user_exists = cursor.fetchone()
        cursor.execute("SELECT * FROM Pet WHERE petid = %s", [petid])
        pet_exists = cursor.fetchone()

    if user_exists and pet_exists:
        # get the pet name, type, age, dressup image and selfie
        with connection.cursor() as cursor:
            cursor.execute("SELECT name, breed, age FROM Pet WHERE petid = %s", [petid])
            name,breed,age = cursor.fetchone() 
            cursor.execute("SELECT image FROM UserProduct WHERE userid = %s AND petid = %s AND description = 'Dressed'", [userid, petid])
            dressup_image = cursor.fetchone()[0]
            cursor.execute("SELECT image FROM Diary WHERE petid = %s AND content = 'Selfie'", [petid])
            pet_selfie = cursor.fetchone()[0]

        # return the pet information as a JSON object
        pet_info = {
            'petname': pet_name,
            'pettype': pet_type,
            'petage': pet_age,
            'dressupimage': dressup_image,
            'petselfie': pet_selfie
        }
        return HttpResponse(json.dumps(pet_info))
    else:
        return HttpResponseBadRequest("User or pet not found.")


# get the user information for a user
def get_user_info(request): 

    if request.method == "POST": 
        userid = request.POST.get("userid")
    else:
        return HttpResponseBadRequest("Invalid request method")

    # check if the user exists
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM User WHERE userid = %s", [userid])
        user_exists = cursor.fetchone()

    if user_exists:
        # get the user money
        with connection.cursor() as cursor:
            cursor.execute("SELECT money FROM User WHERE userid = %s", [userid])
            user_money = cursor.fetchone()[0]

        # return the user information as a JSON object
        user_info = {
            'money': user_money
        }
        return HttpResponse(json.dumps(user_info))
    else:
        return HttpResponseBadRequest("User not found.")


# get the history information for a user and a pet
def get_history_info(request): 
    if request.method == "POST": 
        userid = request.POST.get("userid") 
        petid = request.POST.get("petid")
    else:
        return HttpResponseBadRequest("Invalid request method")

    # check if the user and pet exist
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM User WHERE userid = %s", [userid])
        user_exists = cursor.fetchone()
        cursor.execute("SELECT * FROM Pet WHERE petid = %s", [petid])
        pet_exists = cursor.fetchone()

    if user_exists and pet_exists:
        # get the dates of all the diary entries for the pet
        with connection.cursor() as cursor:
            cursor.execute("SELECT date FROM Diary WHERE petid = %s", [petid])
            dates = cursor.fetchall()

        # return the history information as a JSON object #
        history_info = {
            'dates': [date[0] for date in dates]
        }
        return HttpResponse(json.dumps(history_info))
    else:
        return HttpResponseBadRequest("User or pet not found.")
