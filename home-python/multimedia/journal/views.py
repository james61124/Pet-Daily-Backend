from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from rest_framework_jwt.settings import api_settings
from .models import User, UserProduct, Pet, Product, Diary, IotWaterIntake # add more data
from django.db import connection
from datetime import datetime, timedelta

import base64 
import io 
import json
import os

### Iot
def FoodIntake(request):
    if request.method == 'POST':
        
        data = json.loads(request.body)
        FoodIntake = data.get('FoodIntake')

        current_date = datetime.now()
        new_date = current_date + timedelta(hours=8)
        formatted_date = new_date.strftime('%Y-%m-%d %H:%M:%S')
        current_date = formatted_date

        if FoodIntake is not None:
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
        current_date = datetime.now()
        new_date = current_date + timedelta(hours=8)
        formatted_date = new_date.strftime('%Y-%m-%d %H:%M:%S')
        current_date = formatted_date

        if water_intake is not None:
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
        current_date = datetime.now()
        new_date = current_date + timedelta(hours=8)
        formatted_date = new_date.strftime('%Y-%m-%d %H:%M:%S')
        current_date = formatted_date

        if weight is not None:
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
        money = money[0]

        # get which product user has and where it puts
        with connection.cursor() as cursor:
            cursor.execute("SELECT productid, posX, posY, width, height, zIndex, equipped FROM UserProduct WHERE userid = %s", [userID])
            user_product = cursor.fetchall()
        
        if user_product is not None:
            for productid, posX, posY, width, height, zIndex, equipped in user_product:
                query = f"SELECT image, product_type FROM Product WHERE productid = %s"
                product_info = ""
                with connection.cursor() as cursor:
                    cursor.execute(query, [productid])
                    product_info = cursor.fetchall()
                
                Image = ""
                Type = ""
                if product_info:
                    for image, product_type in product_info:
                        Image = image
                        Type = product_type

                dress_up_product = {
                    "Image": Image,
                    "posX": int(posX),
                    "posY": int(posY),
                    "width": int(width),
                    "height": int(height),
                    "productid": productid,
                    "type": Type,
                    "zIndex": int(zIndex),
                    "equipped": equipped
                }
                dress_up_product_list.append(dress_up_product)

        print(dress_up_product_list)
        
        # get shop product
        with connection.cursor() as cursor:
            cursor.execute("SELECT price, image, productid, product_type FROM Product")
            shop_products = cursor.fetchall()
        
        all_shop_product = [(price, image, productid, product_type) for price, image, productid, product_type in shop_products]
        all_shop_product_dict = {}

        for price, image, productid, product_type in all_shop_product:
            # check if this product user has bought
            bought = False
            Equipped = False
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM UserProduct WHERE userid = %s AND productid = %s", [userID, productid])
                user_product = cursor.fetchone()
            if user_product:
                bought = True
                for equipped in user_product:
                    Equipped = equipped

            shop_product = {
                "productid": productid,
                "price": int(price),
                "image": image,
                "bought": bought,
                "equipped": Equipped
            }
            if product_type in all_shop_product_dict:
                all_shop_product_dict[product_type].append(shop_product)
            else:
                all_shop_product_dict[product_type] = [shop_product]

        response_data = {
            "money": int(money),
            "DressUpProduct": dress_up_product_list,
            "ShopProduct": all_shop_product_dict
        }

        response_data = json.dumps(response_data)

        return HttpResponse(response_data)

    else:
        return HttpResponseBadRequest()

def Buy(request):
    if request.method == 'POST':

        data = json.loads(request.body)
        userID = data.get('userID')
        petID = data.get('petID')
        productID = data.get('productID')
        money = 0
        
        # get user money
        with connection.cursor() as cursor:
            cursor.execute("SELECT money FROM User WHERE userid = %s", [userID])
            money = cursor.fetchone()
        if money is None:
            return HttpResponseBadRequest('User doesn\'t exist')
        
        # check if product exist
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Product WHERE productid = %s", [productID])
            product = cursor.fetchone()
        
        if product is None:
            return HttpResponseBadRequest('Product doesn\'t exist')

        # check if this product user has bought
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM UserProduct WHERE userid = %s AND productid = %s", [userID, productID])
            user_product = cursor.fetchone()
        
        if user_product:
            return HttpResponseBadRequest('User has bought this product')


        # get product price
        price = 0
        with connection.cursor() as cursor:
            cursor.execute("SELECT price FROM Product WHERE productid = %s", [productID])
            price = cursor.fetchone()

        money = money[0]
        price = price[0]
        
        if price > money:
            return HttpResponseBadRequest('User doesn\'t have enought money')
        

        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO UserProduct (userid, productid, equipped) VALUES (%s, %s, %s)", [userID, productID, False])
        
        money = money - price
        with connection.cursor() as cursor:
            cursor.execute("UPDATE User SET money = %s WHERE userid = %s", [money, userID])
        
        response_data = {
            "userid": userID,
            "money": int(money),
            "productid": productID
        }

        return HttpResponse(json.dumps(response_data))

    else:
        return HttpResponseBadRequest()

def _updateUserProductPosition(data, userID, petID):
    print(data)
    
    productID = data.get('productID')
    posX = data.get('posX')
    posY = data.get('posY')

    width = data.get('width')
    height = data.get('height')
    type_ = data.get('type')
    zIndex = data.get('zIndex')

    # check if product exist
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Product WHERE productid = %s", [productID])
        product = cursor.fetchall()
    if product is None:
        return ('error', 'Product doesn\'t exist')

    # check if this product user has bought
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM UserProduct WHERE userid = %s AND productid = %s", [userID, productID])
        user_product = cursor.fetchall()
    if user_product is None:
        return ('error', 'User hasn\'t bought this product')
    
    # update zindex
    if zIndex == -1:
        with connection.cursor() as cursor:
            cursor.execute("SELECT zIndex FROM UserProduct WHERE userid = %s", [userID])
            user_product = cursor.fetchall()
        max_zIndex = -1
        for z_index in user_product:
            z_index = z_index[0]
            if z_index > max_zIndex:
                max_zIndex = z_index
        zIndex = max_zIndex + 1

    # with connection.cursor() as cursor:
    #     cursor.execute("UPDATE UserProduct SET posX = %s, posY = %s, width = %s, height = %s, zIndex = %s, equipped = %s WHERE userid = %s AND productid = %s", [posX, posY, width, height, zIndex, True, userID, productID])

    update_query = "UPDATE UserProduct SET "
    params = []

    if posX is not None:
        update_query += "posX = %s, "
        params.append(posX)
    if posY is not None:
        update_query += "posY = %s, "
        params.append(posY)
    if width is not None:
        update_query += "width = %s, "
        params.append(width)
    if height is not None:
        update_query += "height = %s, "
        params.append(height)
    if zIndex is not None:
        update_query += "zIndex = %s, "
        params.append(zIndex)
    
    # Add the common parameters
    update_query += "equipped = %s WHERE userid = %s AND productid = %s"
    params.extend([True, userID, productID])

    print(update_query)
    print(params)

    with connection.cursor() as cursor:
        cursor.execute(update_query, params)
            
    return ('success','')

def UpdateUserProductPosition(request):
    if request.method == 'POST':

        data = json.loads(request.body)
        userID = data.get('userID')
        petID = data.get('petID')

        # check if user exists
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM User WHERE userid = %s", [userID])
            user_info = cursor.fetchall()
        if user_info is None:
            return ('error', 'User doesn\'t exist')

        result = _updateUserProductPosition(data, userID, petID)
        if result[0] == 'success':
            return HttpResponse()
        else:
            return HttpResponseBadRequest(result[1])
    else:
        return HttpResponseBadRequest()

def Multi_UpdateUserProductPosition(request):
    if request.method == 'POST':

        data = json.loads(request.body)
        userID = data.get('userID')
        petID = data.get('petID')

        # check if user exists
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM User WHERE userid = %s", [userID])
            user_info = cursor.fetchall()
        if user_info is None:
            return HttpResponseBadRequest('User doesn\'t exist')

        products = data.get('products')
        if not isinstance(products, list):
            return HttpResponseBadRequest('products have to be an list')
        
        results = []

        for idx, product in enumerate(products):
            results.append(_updateUserProductPosition(product, userID, petID))

        for result in results:
            if result[0] == 'error':
                return HttpResponseBadRequest(result[1])
        
        return HttpResponse()
    else:
        return HttpResponseBadRequest()
    pass

def UpdateProductStatus(request):
    if request.method == 'POST':

        data = json.loads(request.body)
        userID = data.get('userID')
        petID = data.get('petID')
        productID = data.get('productID')
        Equipped = data.get('equipped')

        # check if user exists
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM User WHERE userid = %s", [userID])
            user_info = cursor.fetchone()
        if user_info is None:
            return HttpResponseBadRequest('User doesn\'t exist')
        
        # check if product exist
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Product WHERE productid = %s", [productID])
            product = cursor.fetchone()
        if product is None:
            return HttpResponseBadRequest('Product doesn\'t exist')

        # check if this product user has bought
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM UserProduct WHERE userid = %s AND productid = %s", [userID, productID])
            user_product = cursor.fetchone()
        if user_product is None:
            return HttpResponseBadRequest('User hasn\'t bought this product')

        with connection.cursor() as cursor:
            cursor.execute("UPDATE UserProduct SET equipped = %s WHERE userid = %s AND productid = %s", [Equipped, userID, productID])
                
        return HttpResponse()

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
            cursor.execute("SELECT userid FROM User WHERE username = %s AND password = %s", [username, password])
            user_data = cursor.fetchone()
        
        if user_data:
            all_user_data = [userid for userid in user_data]
            UserID = 0
            for userid in all_user_data:
                UserID = userid

            with connection.cursor() as cursor:
                cursor.execute("SELECT petid FROM Pet WHERE userid = %s", [user_data[0]])
                pet_data = cursor.fetchone()
        
            all_pet_data = [petid for petid in pet_data]
            petID = 0
            for petid in all_pet_data:
                petID = petid

            if pet_data:
                response_data = {
                    "userID" : UserID,
                    "petID" : petID 
                }
                response_data = json.dumps(response_data)
                return HttpResponse(response_data)
            else:
                response_data = {
                    "userID" : str(user_data[0]),
                    "petID" : ""
                }
                response_data = json.dumps(response_data)
                return HttpResponse(response_data)
        else:
            return HttpResponse("Username or password is incorrect.")
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
        image = data.get('image')

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
            cursor.execute("INSERT INTO Pet (userid, petid, name, breed, gender, age, image) VALUES (%s, %s, %s, %s, %s, %s, %s)", [userID, petid, petName, breed, gender, age, image])

        with connection.cursor() as cursor:
            user_product_id = f"{userID}_{image}"
            cursor.execute("INSERT INTO Product (productid, name, price, image, product_type) VALUES (%s, %s, %s, %s, %s)", [user_product_id, image, 10, image, "Pet"])
            cursor.execute("INSERT INTO UserProduct (userid, productid, zIndex, equipped) VALUES (%s, %s, %s, %s)", [userID, "bg_1.png", 1, True])
            cursor.execute("INSERT INTO UserProduct (userid, productid, zIndex, equipped) VALUES (%s, %s, %s, %s)", [userID, user_product_id, 2, True])
        
        response_data = {
            "userID" : userID,
            "petID" : petid
        }

        response_data = json.dumps(response_data)

        return HttpResponse(response_data)
    else:
        return HttpResponseBadRequest()

def GetPetImage(request):
    if request.method == 'POST':

        data = json.loads(request.body)
        PetType = data.get('PetType')

        image_list = []

        directory = "/home/multimedia/journal/image/pet/" + PetType
        for filename in os.listdir(directory):
            if os.path.isfile(os.path.join(directory, filename)):
                image = "http://107.191.60.115:81/image/pet/" + PetType + '/' + filename
                image_list.append(image)

        response_data = {
            "image" : image_list
        }

        response_data = json.dumps(response_data)

        return HttpResponse(response_data)
    else:
        return HttpResponseBadRequest()

### Diary Page ###
def upload_diary(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            date = data.get('date')
            petid = data.get('petid')
            content = data.get('content')
            place = data.get('place')
            mood = data.get('mood')
            weight = data.get('weight')
            water_intake = data.get('water_intake')
            food_intake = data.get('food_intake')
            defecation = data.get('defecation')
            abnormality = data.get('abnormality')
            medical_record = data.get('medical_record')

            # check if those value is decimal
            if not (type(weight) == int or float):
                weight = 0
            if not (type(water_intake) == int or float):
                water_intake = 0
            if not (type(food_intake) == int or float):
                food_intake = 0

            # convert date format
            try:
                parsed_date = datetime.strptime(date, '%m/%d/%Y')
                date = parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                pass

            query = """
                    UPDATE Diary
                    SET content = %s, place = %s, mood = %s,
                        weight = %s, water_intake = %s, food_intake = %s,
                        defecation = %s, abnormality = %s, medical_record = %s
                    WHERE petid = %s AND date = %s
                """

            with connection.cursor() as cursor:
                    cursor.execute(query, [content, place, mood, weight, water_intake, food_intake, defecation, abnormality, medical_record, petid, date])
                    if cursor.rowcount == 0:
                        cursor.execute("INSERT INTO Diary (petid, date, content, place, mood, weight, water_intake, food_intake, defecation, abnormality, medical_record) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", [petid, date, content, place, mood, weight, water_intake, food_intake, defecation, abnormality, medical_record])

            response_data = {
                "petid": petid,
                "date": date,
                "content": content,
                "place": place,
                "mood": mood,
                "weight": weight,
                "water_intake": water_intake,
                "food_intake": food_intake,
                "defecation": defecation,
                "abnormality": abnormality,
                "medical_record": medical_record,
            }

            return HttpResponse(json.dumps(response_data), content_type='application/json')

        except Exception as e:
            response_data = {'error': str(e)}
            return HttpResponseBadRequest(json.dumps(response_data), content_type='application/json')

    else:
        return HttpResponseBadRequest("Invalid request method")

def upload_image(request):
    if request.method == 'POST':
        try:
            userID = request.POST.get('userID')
            petID = request.POST.get('petID')
            date = request.POST.get('date')
            image_file = request.FILES.get('image')

            # convert date format
            try:
                parsed_date = datetime.strptime(date, '%m/%d/%Y')
                date = parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                pass

            if image_file:
                image_path = f'/home/multimedia/journal/image/user/{userID}/{date}.jpg'
                if not os.path.exists(os.path.dirname(image_path)):
                    try:
                        os.makedirs(os.path.dirname(image_path))
                    except OSError as e:
                        response_data = {'error': str(e)}
                        return HttpResponseBadRequest(json.dumps(response_data), content_type='application/json')

                with open(image_path, 'wb') as destination:
                    for chunk in image_file.chunks():
                        destination.write(chunk)

                image_url = f'http://107.191.60.115:81/image/user/{userID}/{date}.jpg'

                with connection.cursor() as cursor:
                    cursor.execute("UPDATE Diary SET image = %s WHERE petid = %s AND date = %s", [image_url, petID, date])
                    if cursor.rowcount == 0:
                        cursor.execute("INSERT INTO Diary (petid, date, image) VALUES (%s, %s, %s)", [petID, date, image_url])

                response_data = {
                    "image": image_url
                }

                return HttpResponse(json.dumps(response_data), content_type='application/json')

            else:
                response_data = {'error': 'No image file provided'}
                return HttpResponseBadRequest(json.dumps(response_data), content_type='application/json')

        except Exception as e:
            response_data = {'error': str(e)}
            return HttpResponseBadRequest(json.dumps(response_data), content_type='application/json')

    else:
        return HttpResponseBadRequest("Invalid request method")

def get_diary_info(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            date = data.get('date')
            petid = data.get('petid')
            userID = data.get('userid')

            # convert date format
            try:
                parsed_date = datetime.strptime(date, '%m/%d/%Y')
                date = parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                pass

            with connection.cursor() as cursor:
                cursor.execute("SELECT image, content, place, mood, weight, water_intake, food_intake, defecation, abnormality, medical_record FROM Diary WHERE petid = %s AND date = %s", [petid, date])
                diary_info = cursor.fetchall()
            
            Image = None
            Content = None
            Place = None
            Mood = None
            Weight = None
            WaterIntake = None
            FoodIntake = None
            Defecation = None
            Abnormality = None
            MedicalRecord = None

            if diary_info:
                all_diary_info = [(image, content, place, mood, weight, water_intake, food_intake, defecation, abnormality, medical_record) for image, content, place, mood, weight, water_intake, food_intake, defecation, abnormality, medical_record in diary_info]
                for image, content, place, mood, weight, water_intake, food_intake, defecation, abnormality, medical_record in all_diary_info:
                    Image = image
                    Content = content
                    Place = place
                    Mood = mood
                    Weight = weight
                    WaterIntake = water_intake
                    FoodIntake = food_intake
                    Defecation = defecation
                    Abnormality = abnormality
                    MedicalRecord = medical_record
            
            with connection.cursor() as cursor:
                cursor.execute("SELECT date, water_intake FROM IotWaterIntake")
                total_water_intake = cursor.fetchall()
            total_water_intake_list = [(date, water_intake) for date, water_intake in total_water_intake]
            if len(total_water_intake_list) > 0:
                WaterIntake = total_water_intake_list[-1][1]

            with connection.cursor() as cursor:
                cursor.execute("SELECT date, food_intake FROM IotFoodIntake")
                total_food_intake = cursor.fetchall()
            total_food_intake_list = [(date, food_intake) for date, food_intake in total_food_intake]
            if len(total_food_intake_list) > 0:
                FoodIntake = total_food_intake_list[-1][1]

            with connection.cursor() as cursor:
                cursor.execute("SELECT date, weight FROM IotWeight")
                total_weight = cursor.fetchall()
            total_weight_list = [(date, weight) for date, weight in total_weight]
            if len(total_weight_list) > 0:
                Weight = total_weight_list[-1][1]

            # get which product user has and where it puts
            with connection.cursor() as cursor:
                cursor.execute("SELECT productid, posX, posY, width, height, zIndex, equipped FROM UserProduct WHERE userid = %s", [userID])
                user_product = cursor.fetchall()
            

            if WaterIntake is not None:
                WaterIntake = int(WaterIntake)
            if FoodIntake is not None:
                FoodIntake = int(FoodIntake)
            if Weight is not None:
                Weight = int(Weight)

            response_data = {
                "petid": petid,
                "date": date,
                "image": Image,
                "content": Content,
                "place": Place,
                "mood": Mood,
                "weight": Weight,
                "water_intake": WaterIntake,
                "food_intake": FoodIntake,
                "defecation": Defecation,
                "abnormality": Abnormality,
                "medical_record": MedicalRecord
            }

            return HttpResponse(json.dumps(response_data), content_type='application/json')

        except Exception as e:
            response_data = {'error': str(e)}
            return HttpResponseBadRequest(json.dumps(response_data), content_type='application/json')

    else:
        return HttpResponseBadRequest("Invalid request method")

### Main Page ###
def GetMainPagePetInfo(request):
    if request.method == 'POST':
        try:

            data = json.loads(request.body)
            userID = data.get('userID')
            petID = data.get('petID')

            Money = None
            Pet = None
            Breed = None
            Age = None
            Gender = None
            
            # get pet info
            with connection.cursor() as cursor:
                cursor.execute("SELECT name, breed, age, gender FROM Pet WHERE petid = %s", [petID])
                petInfo = cursor.fetchall()
            
            # get user money
            with connection.cursor() as cursor:
                cursor.execute("SELECT money FROM User WHERE userid = %s", [userID])
                Money = cursor.fetchone()
            
            Money = Money[0]

            
            if petInfo:
                pet_info = [(name, breed, age, gender) for name, breed, age, gender in petInfo]
                for name, breed, age, gender in pet_info:
                    Name = name
                    Breed = breed
                    Age = str(age)
                    Gender = gender
            else:
                return HttpResponseBadRequest("Pet doesn't exist.")
            
            # get which product user has and where it puts
            with connection.cursor() as cursor:
                cursor.execute("SELECT productid, posX, posY, width, height, zIndex, equipped FROM UserProduct WHERE userid = %s", [userID])
                user_product = cursor.fetchall()
            
            dress_up_product_list = []
            if user_product is not None:
                for productid, posX, posY, width, height, zIndex, equipped in user_product:
                    query = f"SELECT image, product_type FROM Product WHERE productid = %s"
                    product_info = ""
                    with connection.cursor() as cursor:
                        cursor.execute(query, [productid])
                        product_info = cursor.fetchall()
                    
                    Image = ""
                    Type = ""
                    if product_info:
                        for image, product_type in product_info:
                            Image = image
                            Type = product_type

                    dress_up_product = {
                        "Image": Image,
                        "posX": int(posX),
                        "posY": int(posY),
                        "width": int(width),
                        "height": int(height),
                        "productid": productid,
                        "type": Type,
                        "zIndex": int(zIndex),
                        "equipped": equipped
                    }
                    dress_up_product_list.append(dress_up_product)
            

            response_data = {
                "money": str(Money),
                "name": Name,
                "breed": Breed,
                "age": Age,
                "DressUpProduct": dress_up_product_list
            }

            response_data = json.dumps(response_data)

            return HttpResponse(response_data)
        except Exception as e:
            response_data = {'error': str(e)}
            return HttpResponseBadRequest(json.dumps(response_data), content_type='application/json')

    else:
        return HttpResponseBadRequest()

def GetMainPageDateInfo(request):
    if request.method == 'POST':

        data = json.loads(request.body)
        userID = data.get('userID')
        petID = data.get('petID')
        year = data.get('year')
        month = data.get('month')

        # Convert year and month to integers
        year = int(year)
        month = int(month)

        # Construct the raw SQL query
        query = """
                SELECT
                    DATE_FORMAT(date, '%%Y-%%m-%%d') as date
                FROM
                    Diary
                WHERE
                    petid = %s
                    AND EXTRACT(YEAR_MONTH FROM date) = %s;
            """

        # Execute the raw SQL query
        with connection.cursor() as cursor:
            cursor.execute(query, [petID, year * 100 + month])
            diary_entries = cursor.fetchall()

        response_data = {
            "date": diary_entries
        }

        response_data = json.dumps(response_data)

        return HttpResponse(response_data)

    else:
        return HttpResponseBadRequest()

### DashBoard
def GetWeight(request):
    if request.method == 'POST':
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT date, weight FROM IotWeight")
            total_weight = cursor.fetchall()
        
        total_weight_list = [{ "date": date.strftime('%Y-%m-%d %H:%M:%S'), "value": int(weight)} for date, weight in total_weight][-10:]

        response_data = {
            "weight": total_weight_list
        }

        response_data = json.dumps(response_data)

        return HttpResponse(response_data)

    else:
        return HttpResponseBadRequest()

def GetWaterIntake(request):
    if request.method == 'POST':
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT date, water_intake FROM IotWaterIntake")
            total_water_intake = cursor.fetchall()
        
        total_water_intake_list = [{ "date": date.strftime('%Y-%m-%d %H:%M:%S'), "value": int(water_intake)} for date, water_intake in total_water_intake][-10:]

        response_data = {
            "water_intake": total_water_intake_list
        }

        response_data = json.dumps(response_data)

        return HttpResponse(response_data)

    else:
        return HttpResponseBadRequest()

def GetFoodIntake(request):
    if request.method == 'POST':

        with connection.cursor() as cursor:
            cursor.execute("SELECT date, food_intake FROM IotFoodIntake")
            total_food_intake = cursor.fetchall()

        total_food_intake_list = [{ "date": date.strftime('%Y-%m-%d %H:%M:%S'), "value": int(food_intake)} for date, food_intake in total_food_intake][-10:]

        response_data = {
            "food_intake": total_food_intake_list
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
