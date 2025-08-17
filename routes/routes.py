
from flask import Blueprint , request , render_template , session , redirect , url_for , jsonify
from database.mongo import EMPLOYEE_REGISTER , HMI_CLASS_REG , COURSES , COMPLETED , NOTES , COMMENTS , PUBLISH
from delroutes.dele import delete_All
from cloud.cloudi import upload_notes
from bson.objectid import ObjectId

home = Blueprint("routes" , __name__)


@home.route("/" , methods=["POST" , "GET"])
def HomeLogin():
    
    if session.get("email"):
        return redirect("/dash")
    try:
        if request.method == "POST":  
            phone_no = request.form.get("phone_no")
            
            emp = EMPLOYEE_REGISTER.find_one({"Employee_phone_no":phone_no})

            try:
                hmi = HMI_CLASS_REG.find_one({"employee_email":emp["Employee_email"]})
                
                if hmi['isLogged']==True:
                    return render_template("index.html" , err=f"Employee with This Phone number {phone_no} Already Logged Use Different Phone Number !")
                else:
                    session["email"] = emp["Employee_email"]
                    session.permanent = True
                    return redirect("/dash")
            except:
                data = {
                    "employee_email":emp['Employee_email'],
                    "employes_phone_no":emp["Employee_phone_no"],
                    "role":emp["Employee_Role"],
                    "payment_completed":False,
                    "yes":False,
                    "accept":False,
                    "link":"",
                    "isLogged":True,
                    "status":"pending...."
                }
                
                HMI_CLASS_REG.insert_one(data)
                
                session["email"] = emp["Employee_email"]
                session.permanent = True
                return redirect("/dash")
        return render_template("index.html")
    
    except:
        return render_template("index.html" , err='Internal Server Error')
        
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
    p = PUBLISH.find({"user":email}).sort("_id" , -1).limit(1)
    return render_template("settings.html" , data=data , photo=photo['Employee_Pic'] , p=p)


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
    
@home.route("/delete/pub")
def delete_pub():
    PUBLISH.delete_many({})
    return "deleted...."            

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


@home.route("/check/website/<name>")
def check_name(name):
    p_name = PUBLISH.find_one({"project_name":name})

    if p_name:
        return jsonify({"Sucess":False , "data":"Name Exits"})
    else:
        return jsonify({"Sucess":True})


    
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

@home.route("/notes/students")
def show_notes():
    n = NOTES.find({}).sort("_id" , -1)
    return render_template("notes.html" , n=n)

@home.route("/admin/upload/notes" , methods=["POST" , "GET" , "DELETE"])
def Upload_Notes():
    if request.method == "POST":
        cat = request.form.get("cat")
        note = request.files.get("note")
        
        url = upload_notes(note)

        data = {
            "cat":cat,
            "note_pdf":url,
        }
        NOTES.insert_one(data)
        return redirect("/hmi-class/home")

        
    else:
        all_Notes = NOTES.find({}).sort("_id" , -1)
        return render_template("Upload_notes.html" , all_notes=all_Notes)
    
@home.route("/admin/Delete" , methods=["POST"])
def Delete_note():
    note_id = request.form.get("note_id")
    NOTES.find_one_and_delete({"_id":ObjectId(note_id)})
    return redirect("/hmi-class/home")

@home.route("/course-comments/<c_id>")
def Comments(c_id):
   n = COURSES.find_one({"_id":ObjectId(c_id)})
   comment = COMMENTS.find({"c_id":c_id})
   session['course'] = str(c_id)
   return render_template("comments.html" , n=n , c=comment)

@home.route("/add-comments/<c_id>" , methods=["POST"])
def add_comments(c_id):
    text = request.form.get("comment")
    email = session.get("email")
    User = EMPLOYEE_REGISTER.find_one({"Employee_email":email})
    data={
        "Comment":text,
        "user_email":email,
        "user_name":User['Employee_name'],
        "c_id":c_id,
    }
    COMMENTS.insert_one(data)
    return redirect(url_for('routes.Comments' , c_id=c_id))


@home.route("/playground")
def PlayGround():
    return render_template("test.html")


@home.route("/publish/user/code" , methods=["POST"])
def pusblish_website():
    try:
        code = request.form.get("code")
        email = session.get("email")
        p_name = request.form.get("p_name")
        

        data = {
            "user":email,
            "project_name":p_name,
            "code":code,
            "link":""
        }
      
        p_id = PUBLISH.insert_one(data)
        link = url_for("routes.Hmi_Publish" ,publish_id=p_id.inserted_id , _external=True)
        PUBLISH.find_one_and_update({"_id":ObjectId(p_id.inserted_id)} , {"$set":{
            "link":link
        }})
        return jsonify({"Sucess":True , "link":link})
    
    except Exception as e:
        return jsonify({"Sucess":False , "error":e})


@home.route("/hmi/publish/<publish_id>")
def Hmi_Publish(publish_id):
    try:
        website = PUBLISH.find_one({"_id":ObjectId(publish_id)})
        return render_template("liveWeb.html" , wesite = website)
    except:
        return render_template("pagenotfound.html")



@home.route("/admin/activity")
def activity():
    c = COMMENTS.find({}).sort("_id" , -1)
    course = COURSES.find({}).sort("_id" , -1)
    return render_template("Activity.html" , c=c , course=course)

@home.route("/delete")
def delete():
    delete_All()
    return jsonify({"suess":"deleted Suessfully"})

@home.route("/reply/<c_id>" , methods=["POST"])
def Rep_Comment(c_id):
   content = request.form.get("content")

   hmi = "@HMIADMIN✅"

   reply = {
       "content":content,
       "for":c_id,
       "hmi":hmi
   }
   COMMENTS.find_one_and_update({"c_id":c_id} , {"$push":{"replies":reply}})

   return redirect("/admin/activity")
   

@home.route("/delete/reply/admin/<d_id>" , methods=["POST"])
def Delete_Reply(d_id):
    COMMENTS.find_one_and_update({"_id":ObjectId(d_id)} , {"$unset":{"replies":""}})
    return redirect("/admin/activity")

@home.route("/delete/admin/comment/<d_id>" , methods=["POST"])
def Delete_comment(d_id):
    COMMENTS.find_one_and_delete({"_id":ObjectId(d_id)})  
    return redirect("/admin/activity") 

@home.route("/check-owner/<email_id>")
def check_email(email_id):
    e = session.get("email")

    if email_id == e:
        return jsonify({"owner":True})
    else:
        return jsonify({"owner":False})

@home.route("/delete-comment/<d_id>" , methods=["POST"])
def Delete_Comment(d_id):
    
    COMMENTS.delete_one({"_id":ObjectId(d_id)})
    
    return redirect(f"/course-comments/{session.get("course")}")


@home.route("/delete/course/<c_id>" , methods=["POST"])
def Delete_Course(c_id):
    COURSES.find_one_and_delete({"_id":ObjectId(c_id)})
    return redirect("/admin/activity")

@home.route("/delete/<email>")
def delete_one_email(email):
    HMI_CLASS_REG.find_one_and_delete({"employee_email":email})
    return jsonify("Suess...")


@home.route("/send-mail")
def send_mail():
    email = session.get("email")
    if email:
        session['email'] = email
        session.permanent = True
        return jsonify({"Sucess":True,"user_email":email})
        
    else:
        return jsonify({"Sucess":False , "error":"User is Not Authenticated"})

@home.route('/edit/<course_id>' , methods=["POST" , "GET"])
def Edit_course(course_id):
    try:
        if request.method == "POST":
            title = request.form.get("title")
            des = request.form.get("des")
            code = request.form.get("code")
            for_which = request.form.get("for_which")

            COURSES.find_one_and_update({"_id":ObjectId(course_id)} , {"$set":{
                "title":title,
                "des":des,
                "video_link":code,
                "for_which":for_which
            }})

            return redirect("/admin/activity")
        
        courses = COURSES.find_one({"_id":ObjectId(course_id)})
        if courses:
          return render_template("editcourse.html" , c=courses)
        else:
            return "<h1> Course Not Found </h1> <br> <b> Pls Check Again if any mistake </b>"

    except:
        return "Internal Server Error"


@home.route("/clear")
def logout():
    em = session.get("email")
    HMI_CLASS_REG.find_one_and_update({"employee_email":em} , {"$set":{
        "isLogged":False
    }})
   
    session.clear()
    return redirect("/")

