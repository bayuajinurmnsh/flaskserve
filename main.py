
#   an simple flask backend
from flask import Flask, json, jsonify, request
from flask.helpers import make_response
from flask_cors import CORS
from datetime import datetime, date, time, timedelta
import jwt
############################ Choose Models ############################
# from dbms.json_db.model import Model
from dbms.json_db.model import Model
import uuid

############################ Initialization ############################
app = Flask(__name__)
# this essitial for Cross Origin Resource Sharing with React frontend
# https://flask-cors.readthedocs.io/en/latest/
CORS(app)

# secret key
app.config['SECRET_KEY'] = 'verysecretkey'
# use database
model = Model()

#CONSTANT
TODAY = datetime.today()

#addYears
def addYears(d, years):
    try:
        #Return same day of the current year        
        return d.replace(year = d.year + years)
    except ValueError:
        #If not same day, it will return other, i.e.  February 29 to March 1 etc.        
        return d + (date(d.year + years, 1, 1) - date(d.year, 1, 1))

#check method Put Valid Date
def validDate(inputDate):
    if len(inputDate) >=6:
      try:
        datetime.strptime(inputDate, '%d/%m/%Y')
        return inputDate
      except ValueError:
        return "invalid"
    
    elif len(inputDate) <6:
      try:
        datetime.strptime(inputDate, '%m/%y')
        return inputDate
      except ValueError:
        return "invalid"
    
    else:
      return "invalid"

#valid securityCode
def validSecurityCode(inputSecurityCode):
    if type(inputSecurityCode) !=float and len(str(inputSecurityCode)) == 4:
        try:
            tmp = int(inputSecurityCode)
            return tmp
        except ValueError:
            return "invalid"

    elif len(str(inputSecurityCode)) > 4:
        return "invalid"
    
    else:
        return "invalid"

def validAccountNumber(inputSecurityCode):
    if type(inputSecurityCode) !=float and len(str(inputSecurityCode)) == 6:
        try:
            tmp = int(inputSecurityCode)
            return tmp
        except ValueError:
            return "invalid"

    elif len(str(inputSecurityCode)) > 4:
        return "invalid"
    
    else:
        return "invalid"
#check is STR or NOT
def isAStr(input):
    if( (type(input) == int or type(input) == float) and input>=100000 ):
        return "valid"

    return "invalid"

######################### JWT ###############
def token_required():
    token = None
        # jwt is passed in the request header
    if 'x-access-token' in request.headers:
        token = request.headers['x-access-token']
        # return 401 if token is not passed
    if not token:
        return make_response(jsonify({'message' : "token is missing", "status":"error"}),401,
            {'WWW-Authenticate' : 'Basic realm ="Token Missing !!"'}
        )
  
    try:
            # decoding the payload to fetch the stored details
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        datedata = data['jwt_exp']
        datedataconv = datetime.strptime(datedata, '%Y-%m-%d %H:%M:%S.%f')
        time_now = datetime.now()
        print(f"time now : {time_now}, conv: {datedataconv}")

        if time_now > datedataconv:
            return make_response(
            jsonify({'message' : "token is expired", "status":"error"}),
            401,
            {'WWW-Authenticate' : 'Basic realm ="Token is Expired !!"'}
        )

    except:
        return make_response(
            jsonify({'message' : "token is invalid", "status":"error"}),
            401,
            {'WWW-Authenticate' : 'Basic realm ="Token is invalid !!"'}
        )
        # returns the current logged in users contex to the routes
    return  "valid"
########################### JWT above #############################
#  
##########################  API Implementation #########################

###############login#######################
@app.route('/login', methods =['POST'])
def login():
    # creates dictionary of form data
    auth = json.loads(request.data)

    if not auth or not auth['username'] or not auth['password']:
        # returns 401 if any email or / and password is missing
        return make_response(
            jsonify({'message' : "login required", "status":"error"}),
            401,
            {'WWW-Authenticate' : 'Basic realm ="Login required !!"'}
        )
  
    user = model.read_tbl_login(auth['username'])
  
    if not user:
        # returns 401 if user does not exist
        return make_response(
            jsonify({'message' : "user does not exists", "status":"error"}),
            404,
            {'WWW-Authenticate' : 'Basic realm ="User does not exist !!"'}
        )
  
    if (user['username'] == auth['username']) and (user['password'] == auth['password']):
        # generates the JWT Token
        token = jwt.encode({"jwt_username": user['username'] , 'jwt_exp' : str(datetime.now() + timedelta(minutes= 1))}, app.config['SECRET_KEY'], algorithm="HS256")
        
        # refreshToken = jwt.encode({
        #     'expR' : datetime.utcnow() + timedelta(minutes = 30)
        # }, app.config['SECRET_KEY'])
  
        return make_response(jsonify({'token' : token, "status":"ok"}), 201)
    # returns 404 if password is wrong
    return make_response(
        jsonify({'message' : "wrong username or password", "status":"error"}),
        404,
        {'WWW-Authenticate' : 'Basic realm ="Wrong Username or Password !!"'}
    )

##register###
@app.route('/register', methods =['POST'])
def register():
    # creates dictionary of form data
    auth = json.loads(request.data)

    if ("username" not in auth or "password" not in auth) and len(auth) !=2:
        return jsonify({"errorMsg": "valid key adalah username dan password, dan total key hanya dua", "status":"error"}), 400
    
    if auth['username'] == "" and auth['password']=="":
        return jsonify({"errorMsg": "ada key yang value nya kosong", "status":"error"}), 400

    if not (model.createRegister(auth["username"], auth)):
            return jsonify({"errorMsg": "username sudah terpakai", "status":"error"}), 400
    
    return jsonify({'data' : auth, "status":"ok"}), 201


############################## create name #############################
@app.route('/keys', methods=["POST"])
def create_name():
    check_token = token_required()
    if check_token == "valid":
        valid_key = ('key', 'firstName', 'lastName' , 'createdDate','balance' ,'status', 'accountType', 'validDate','accountNumber','securityCode')
        tmpValidDate = addYears(TODAY, 5) 

        data_json = request.data
        data_dict = json.loads(data_json)
        data_dict['key'] = str(uuid.uuid1())
        data_dict['createdDate'] = str(TODAY.strftime("%d/%m/%Y"))
        data_dict['validDate'] = str(tmpValidDate.strftime("%m/%y"))

        # bad request
        check_valid_data = [x for x in valid_key if x not in data_dict]
        if len(check_valid_data) != 0 or len(data_dict)!=10:
            return jsonify({"errorMsg": f"valid key nya adalah {valid_key} dan total key tidak kurang atau lebih dari 10", "status":"error"}), 400

        #if there is empty val
        emptyData = [k for k,v in data_dict.items() if v ==""]
        if len(emptyData) !=0:
            return jsonify({"errorMsg": "Ada key yang valuenya kosong", "status":"error"}), 400

        # len security code == 4 and type not float or str
        check_valid_security_code = validSecurityCode(data_dict['securityCode'])
        if check_valid_security_code == "invalid":
            return jsonify({"errorMsg": "security code harus int dan panjangnya tidak lebih atau kurang dari 4 angka", "status":"error"}), 400

        data_dict['securityCode'] = check_valid_security_code
    
        # len accountNumber == 6 and type not float or str
        check_valid_account_number = validAccountNumber(data_dict['accountNumber'])
        if check_valid_account_number == "invalid":
            return jsonify({"errorMsg": "Account Number harus int dan panjangnya tidak lebih atau kurang dari 6 angka", "status":"error"}), 400

        # check if balance is str or not
        check_balance = isAStr(data_dict['balance'])
        if check_balance == 'invalid':
            return jsonify({"errorMsg": "balance harus float atau int dan mimal harus 100000", "status":"error"}), 400
        
        #untuk insert dan sekalian check
        if not (model.create(data_dict["key"], data_dict)):
            return jsonify({"errorMsg": "accountNumber sudah terpakai", "status":"error"}), 400
        # succeed
        return jsonify({'data' : data_dict, "status":"ok"}), 201

    return jsonify({"message": "You dont have authorization", "status": "error"}), 400

############################## read name ###############################
@app.route('/keys/<key>', methods=["GET"])
def read_name(key):
    check_token = token_required()
    if check_token == "valid":
        value = model.read(key)

        # not found
        if (value is None):
            return jsonify({"key": key, "errorMsg": "not found"}), 404
        # succeed
        value["key"] = key
        return jsonify({"data":value,"status":"ok"}), 200
    
    return jsonify({"message": "You dont have authorization", "status": "error"}), 400


############################## update name #############################
@app.route('/keys/<key>', methods=["PUT"])
def update_name(key):
    check_token = token_required()
    if check_token == "valid":
        valid_key = ('key', 'firstName', 'lastName' , 'createdDate','balance' ,'status', 'accountType', 'validDate')
        data_dict = json.loads(request.data)

        # bad request
        check_valid_data = [x for x in valid_key if x not in data_dict]
        if len(check_valid_data) != 0 or len(data_dict)!=10:
            return jsonify({"errorMsg": f"valid key nya adalah {valid_key} dan total key tidak kurang atau lebih dari 10", "status":"error"}), 400

        #if there is empty val
        emptyData = [k for k,v in data_dict.items() if v ==""]
        if len(emptyData) !=0:
            return jsonify({"errorMsg": "Ada key yang valuenya kosong", "status":"error"}), 400

        # len security code > 4 and type not int
        check_valid_security_code = validSecurityCode(data_dict['securityCode'])
        if check_valid_security_code == "invalid":
            return jsonify({"errorMsg": "security code harus int dan panjangnya tidak lebih atau kurang dari 4 angka", "status":"error"}), 400
        data_dict['securityCode'] = check_valid_security_code

        # len accountNumber == 6 and type not float or str
        check_valid_account_number = validAccountNumber(data_dict['accountNumber'])
        if check_valid_account_number == "invalid":
            return jsonify({"errorMsg": "Account Number harus int dan panjangnya tidak lebih atau kurang dari 6 angka", "status":"error"}), 400

        # check if balance is str or not
        check_balance = isAStr(data_dict['balance'])
        if check_balance == 'invalid':
            return jsonify({"errorMsg": "balance harus float atau int dan mimal harus 100000", "status":"error"}), 400

        #check date from input user
        validCreatedDate = validDate(data_dict['createdDate'])
        if validCreatedDate == 'invalid':
            return jsonify({"errorMsg": "created date harus dalam format d/m/y , cth :31/12/2021", "status":"error"}), 400
        
        #check date from input user
        validDateFromUser = validDate(data_dict['validDate'])
        if validDateFromUser == 'invalid':
            return jsonify({"errorMsg": "valid date harus dalam format m/y , cth : 12/26 ", "status":"error"}), 400

        # bad request
        if (not model.update(key, data_dict)):
            return jsonify({"key": key, "errorMsg": "ganti accountNumber dengan accountNumber lain! karena accountNumber sudah dipakai", "status":"error"}), 400
        # succeed
        data_dict["key"] = key
        return jsonify({'data' : data_dict, "status":"ok"}), 200

    return jsonify({"message": "You dont have authorization", "status": "error"}), 400


############################## delete name #############################
@app.route('/keys/<key>', methods=["DELETE"])
def delete_name(key):
    # not found
    check_token = token_required()
    if check_token == "valid":
        value = model.read(key)
        if not value:
            return jsonify({"key": key, "errorMsg": "not found"}), 404
        # not found
        if (not model.delete(key)):
            return jsonify({"key": key, "errorMsg": "not found"}), 404
        # succeed
        value["key"] = key
        return jsonify({'data' : value, "status":"ok"}), 200
    return jsonify({"message": "You dont have authorization", "status": "error"}), 400


############################# Debug Method #############################
# print database
@app.route('/debug', methods=["GET"])
def print_database():
    check_token = token_required()
    if check_token == "valid":
        database = model.debug()
        if (database is None):
            print("\n########### Debug Method Not Implemented #############")
            return jsonify({"errorMsg": "Debug Method Not Implemented","status":"error"}), 200
        else:
            print("\n######################################################")
            print(database)
            return jsonify({'data' : database, "status":"ok"}), 200
    return jsonify({"message": "You dont have authorization", "status": "error"}), 403
    # database = model.debug()
    # if (database is None):
    #     print("\n########### Debug Method Not Implemented #############")
    #     return jsonify({"errorMsg": "Debug Method Not Implemented","status":"error"}), 200
    # else:
    #     print("\n######################################################")
    #     print(database)
    #     return jsonify({'data' : database, "status":"ok"}), 200


############################ Main Function #############################
if __name__ == "__main__":
    # run backend server on http://localhost:5000/
    app.run(host='localhost', port=5000, debug=True)
