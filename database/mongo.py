from pymongo import MongoClient

client = MongoClient("mongodb+srv://sriram65raja:1324sriram@cluster0.dejys.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

db = client['ai']
EMPLOYEE_REGISTER = db["EMPLOYEE_REGISTER"]
HMI_CLASS_REG = db['HMI_CLASS_REG']
COURSES = db["COURSES"]
COMPLETED = db['COMPLETED']