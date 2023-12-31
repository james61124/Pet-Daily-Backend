from django.apps import AppConfig
from django.db import connection
import os


class JournalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'journal'

    def ready(self):

        shop_type_list = ['Cristmas', 'Helloween', 'Home', 'NewYear', 'Others', 'Background']
        for shop_type in shop_type_list:
            directory = f"/home/multimedia/journal/image/shop/{shop_type}"
            for filename in os.listdir(directory):
                if os.path.isfile(os.path.join(directory, filename)):
                    image = f"http://107.191.60.115:81/image/shop/{shop_type}/" + filename
                    productid = filename
                    name = filename
                    price = 10
                    product_type = f"{shop_type}"

                    with connection.cursor() as cursor:
                        cursor.execute("SELECT COUNT(*) FROM Product WHERE productid = %s", [productid])
                        count = cursor.fetchone()[0]

                    if count == 0:
                        with connection.cursor() as cursor:
                            cursor.execute("INSERT INTO Product (productid, name, price, image, product_type) VALUES (%s, %s, %s, %s, %s)", [productid, name, price, image, product_type])
                
