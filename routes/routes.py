from flask import Blueprint , request , render_template , session , redirect , url_for , jsonify
from database.mongo import EMPLOYEE_REGISTER , HMI_CLASS_REG , COURSES , COMPLETED
from delroutes.dele import delete_All

home = Blueprint("routes" , __name__)


@home.route("/" , methods=["POST" , "GET"])
def HomeLogin():
    
    if session.get("email"):
        return redirect("/dash")
    try:
        if request.method == "POST":  
            phone_no = request.form.get("phone_no")
            
            emp = EMPLOYEE_REGISTER.find_one({"Employee_phone_no":phone_no})
            hmi = HMI_CLASS_REG.find_one({"employee_email":emp["Employee_email"]})
            
            
            if hmi:
                return render_template("index.html" , err=f"Employee with This Phone number {phone_no} Already Found Use Different Phone Number !")
            
            data = {
                "employee_email":emp['Employee_email'],
                "employes_phone_no":emp["Employee_phone_no"],
                "role":emp["Employee_Role"],
                "payment_completed":False,
                "yes":False,
                "accept":False,
                "link":"",
                "status":"pending...."
            }
            
            HMI_CLASS_REG.insert_one(data)
            
            session["email"] = emp["Employee_email"]
            session.permanent = True
            
            return redirect("/dash")
        return render_template("index.html")
    except:
        return render_template("index.html" , err='User Not Found')
        
@home.route("/dash")
def dashboard():
    if not session.get("email"):
        return redirect("/")
    try:
        email = session.get("email")
        h = HMI_CLASS_REG.find_one({"employee_email":email})
        employee_photo = EMPLOYEE_REGISTER.find_one({"Employee_email":email})
        if h["role"] == "ClinetEmployee":
            if h['payment_completed'] == True:
             if h['status'] == "Fail" or h['status'] == "pending....":
                C =  COURSES.find({"for_which":h["role"]})
                return render_template("clientemp.html" , email=email , h=h , employee_photo = employee_photo["Employee_Pic"] , c = C )
            elif h['status'] == "Pass":
                return render_template("pass.html" , em=employee_photo)
            else:
                return render_template("qr.html")
        elif h["role"] == "Developer":
            if h['payment_completed'] == True:
                if h['status'] == "Fail" or h['status'] == "pending....":
                    C =  COURSES.find({"for_which":h["role"]})  
                    return render_template("Dev.html" , email=email , h=h , employee_photo = employee_photo["Employee_Pic"] , c=C)
                elif h['status'] == "Pass":
                    return render_template("pass.html" , em=employee_photo)
            else:
                return render_template("qr.html")
        else:
            return "Invalid Or Not Authorized"
    except Exception as e:
        ip = request.remote_addr
        return render_template("err.html" , ip=ip , e=e)


@home.route("/apply-payment-completed/<email_id>" , methods=["POST"])
def Payment_completed(email_id):
   HMI_CLASS_REG.find_one_and_update({"employee_email" : email_id} , {"$set":{
       "payment_completed":True
   }})
   
   return redirect("/hmi-class/home")

@home.route("/get-data-payment")
def Get_data():
    if not session.get("email"):
        return redirect("/")
    email = session.get("email")
    U = HMI_CLASS_REG.find_one({"employee_email":email})
    if U:
        U["_id"] = str(U["_id"])
    return jsonify({"User":U})


@home.route("/dash/settings/<email>")
def get_datas(email):
    data = HMI_CLASS_REG.find_one({"employee_email":email})
    photo = EMPLOYEE_REGISTER.find_one({"Employee_email":email})
    return render_template("settings.html" , data=data , photo=photo['Employee_Pic'])


@home.route("/hmi-class/home")
def hmi_class_home():
    h = HMI_CLASS_REG.find({}).sort("_id" , -1)
    return render_template("admin.html" , h=h)

@home.route("/upload/<name>")
def UploadCourse(name):
    if name == "ClinetEmployee":
        return redirect("/ClientEmployee")
    elif name == "Developer":
        return redirect("/developer")
    
            

@home.route("/ClientEmployee" , methods=["POST" , "GET"])
def Clinet_Employee():
    
    if request.method == "POST":
        title = request.form.get("title")
        des = request.form.get("des")
        video_link = request.form.get("video_link")
        for_which = request.form.get("for_which")
        
        data = {
            "title":title,
            "des":des,
            "video_link":video_link,
            "for_which":for_which,
        }
        
        COURSES.insert_one(data)
        return redirect("/hmi-class/home")
    
    return render_template("upload_clinet.html")
        
@home.route("/developer" , methods=["POST" , "GET"])
def upload_developer():
    if request.method == "POST":
        title = request.form.get("title")
        des = request.form.get("des")
        video_link = request.form.get("video_link")
        for_which = request.form.get("for_which")
        
        data = {
            "title":title,
            "des":des,
            "video_link":video_link,
            "for_which":for_which,
        
        }
        
        COURSES.insert_one(data)
        return redirect("/hmi-class/home")
    return render_template("upload_dev.html")


@home.route("/send-complete" , methods=["POST"])
def send_completed():
    email = session.get("email")
    HMI_CLASS_REG.find_one_and_update({"employee_email":email} , {"$set":{
        "yes":True
    }})
    
    return redirect("/dash")


@home.route("/accept")
def accpets():
  
    l = request.args.get("link")
    e = request.args.get("email")
    
    HMI_CLASS_REG.find_one_and_update({"employee_email":e} , {"$set":{
        "accept":True,
        "link":l
    }})
  
    return jsonify({"data":"Updated Suessfully...."})


@home.route("/set-status" , methods=["POST"])
def setstatus():
    e = request.form.get("email-id")
    stuas = request.form.get("passorfail")
    HMI_CLASS_REG.find_one_and_update({"employee_email":e} , {"$set":{
        "status":stuas
    }})
    
    return redirect('hmi-class/home')
    
@home.route("/delete")
def delete():
    delete_All()
    return jsonify({"suess":"deleted Suessfully"})

@home.route("/delete/<email>")
def delete_one_email(email):
    HMI_CLASS_REG.find_one_and_delete({"employee_email":email})
    return jsonify("Suess...")

@home.route("/clear")
def logout():
    session.clear()
    return redirect("/")
