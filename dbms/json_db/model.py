
#   an database implementated by json in file system
import json
from os import path

#################### Database CRUD Implementation ######################


class Model():
    database = {}
    location = ""

    def __init__(self, database={}, location="database.json"):
        self.location = path.dirname(__file__) + "/" + location
        self.database = database
        # the only case which need to read file
        if (path.isfile(self.location) and len(database) == 0):
            with open(self.location, "r") as data_file:
                self.database = json.load(data_file)
        # then write to the disk
        self.save()

    ############################ create item ###########################

    def create(self, key, value):
        # key = "1"
        # value = {"firstName": "John", "lastName": "Doe"}
        # return = True
        #          False
        for x in self.database['tbl_users']:
            y = self.database.get('tbl_users', {}).get(str(x))
            if y['accountNumber']==value['accountNumber']:
                return False

        if key in self.database['tbl_users']:
            return False
        
        # invalid value
        try:
            if (len(value["firstName"]) == 0
                    and len(value["lastName"]) == 0):
                return False
        except KeyError:
            return False
        # succeed
        self.database['tbl_users'][key] = value
        self.save()
        return True

    ############################ read item ###########################

    def read(self, key):
        # key = "1"
        # reutrn value = {"firstName": "John", "lastName": "Doe"}
        #                None
        if key in self.database['tbl_users']:
            return self.database['tbl_users'][key]
        else:
            return None

    ############################ update item ###########################

    def update(self, key, value):
        # key = "1"
        # value = {"firstName": "John", "lastName": "Doe"}
        # return = True
        #          False
        # invalid value

        #buat variable nampung value dengan key sekarang
        tmpDataDb = self.database['tbl_users'][key]
        if tmpDataDb['accountNumber'] != value['accountNumber']:
            for x in self.database['tbl_users']:
                y = self.database.get('tbl_users', {}).get(str(x))
                if y['accountNumber']==value['accountNumber']:
                    return False

        try:
            if (len(value["firstName"]) == 0
                    and len(value["lastName"]) == 0):
                return False
            # not found
            if (key not in self.database['tbl_users']):
                return False
        # invalid value
        except KeyError:
            print("key error")
            return False
        # succeed
        self.database['tbl_users'][key] = value
        self.save()
        return True

    ############################ delete item ###########################

    def delete(self, key):
        # key = "1"
        # return = True
        #          False
        if key not in self.database['tbl_users']:
            return False
        # succeed
        del self.database['tbl_users'][key]
        self.save()
        return True

    ############################ debug method ###########################

    def debug(self):
        # return = database if implemented
        #          None if not implemented
        with open(self.location, "r") as data_file:
            data_dict = json.load(data_file)
        return data_dict['tbl_users']

    ############################ save method ###########################

    def save(self):
        # save self.database to self.location
        with open(self.location, "w+") as data_file:
            data_file.write(json.dumps(self.database, indent=2))

    #read login
    def read_tbl_login(self, username):
        # key = "1"
        # reutrn value = {"firstName": "John", "lastName": "Doe"}
        #                None
        if username in self.database['tbl_login']:
            return self.database['tbl_login'][username]
        else:
            return None
    
    #register user for login
    def createRegister(self, key, value):
        # key = "1"
        # value = {"firstName": "John", "lastName": "Doe"}
        # return = True
        #          False
        for x in self.database['tbl_login']:
            y = self.database.get('tbl_login', {}).get(str(x))
            if y['username']==value['username']:
                return False

        if key in self.database['tbl_login']:
            return False

        # invalid value
        try:
            if (len(value["username"]) == 0
                    and len(value["password"]) == 0):
                return False
        except KeyError:
            return False
        # succeed
        self.database['tbl_login'][key] = value
        self.save()
        return True

########################## Test Function #############################
# if __name__ == "__main__":
#     model = Model({
#         "tbl_users": {
#             "1": {"firstName": "John", "lastName": "Doe", "key":"1","createdDate":"29/11/2021","balance":100000.0,"status":"active","accountType":"basic", "validDate":"11/26",'accountNumber':111222,'securityCode':1234},
            
#             "2":{"firstName": "Strong", "lastName": "Dinosaur", "key":"2","createdDate":"29/11/2021","balance":150000.0,"status":"active","accountType":"platinum","validDate":"11/26",'accountNumber':111333,'securityCode':1234},
            
#             "3": {"firstName": "Black", "lastName": "Cat", "key":"3","createdDate":"29/11/2021","balance":200000.0,"status":"active","accountType":"basic","validDate":"11/26",'accountNumber':111444,'securityCode':1234}
#         },
#         "tbl_login": {
#             "bayuaji": {
#             "username": "bayuaji",
#             "password": "bayuaji",
#             "jwt": {
#                 "token": "",
#                 "refreshToken": ""
#                 }
#             }
#         }
#     })
#     print(model.debug())
    