from datetime import date , timedelta
import shutil
from fastapi import FastAPI, HTTPException
from fastapi import  File, UploadFile
from fastapi.responses import FileResponse
from PyPDF2 import PdfReader, PdfWriter
from fpdf import FPDF
import os
import sqlite3
import uvicorn
from pydantic import BaseModel
from PIL import Image

database = './lowyer.db'

def create():
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admins (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
    ''')

    # إنشاء جدول القضايا المنظوره
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Cases (
        user_id INTEGER NOT NULL,
        case_number TEXT PRIMARY KEY,
        case_year TEXT,
        case_type TEXT,
        first_instance_court TEXT,
        appellate_court TEXT,
        appellate_case_number TEXT,
        appellate_case_year TEXT,
        client_name TEXT,
        client_role TEXT,
        opponent_name TEXT,
        opponent_role TEXT,
        case_subject TEXT,
        power_of_attorney_number TEXT,
        power_of_attorney_year TEXT,
        FOREIGN KEY (user_id) REFERENCES admins(user_id)
    )
    ''')


    # إنشاء جدول قضايا الارشيف
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Arshef (
        user_id INTEGER NOT NULL,
        case_number TEXT PRIMARY KEY,
        case_year TEXT,
        case_type TEXT,
        first_instance_court TEXT,
        appellate_court TEXT,
        appellate_case_number TEXT,
        appellate_case_year TEXT,
        client_name TEXT,
        client_role TEXT,
        opponent_name TEXT,
        opponent_role TEXT,
        case_subject TEXT,
        power_of_attorney_number TEXT,
        power_of_attorney_year TEXT,
        FOREIGN KEY (user_id) REFERENCES admins(user_id)
    )
    ''')

    # إنشاء جدول الجلسات
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Sessions (
        session_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        case_number TEXT,
        session_rol INTEGER ,
        session_date DATE,
        session_decision TEXT,
        session_hasr TEXT,
        FOREIGN KEY (case_number) REFERENCES Cases(case_number)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS nmozg (
        nmozg_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER ,
        nmozg_name TEXT,
        nmozg_decision TEXT
    )
    ''')

    
    conn.commit()
    conn.close()

create()



app = FastAPI()

@app.get("/admins")
def home():
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM admins
    ''')
    RUSELT =  cursor.fetchall()
    conn.close()
    return RUSELT


class Admin(BaseModel):
    username: str
    email: str
    password: str



# إضافة مشرف
@app.post("/admins/")
def add_admin(admin: Admin):
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO admins (username, email, password) 
        VALUES (?, ?, ?)
    ''', (admin.username, admin.email, admin.password))
    conn.commit()
    conn.close()
    return {"detail": "تم اضافة ادمن بنجاح"}




@app.put("/admins/{user_id}")
def update_admin(user_id: int, admin: Admin):
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE admins 
        SET username = ?, email = ?, password = ? 
        WHERE user_id = ?
    ''', (admin.username, admin.email, admin.password, user_id))
    print(cursor.rowcount)
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="لا يوجد محامي بهذه المعلومات")
    
    conn.commit()
    conn.close()
    return {"detail": "تم تعديل معلومات المحامي بنجاح"}


@app.delete("/admins/{user_id}")
def delete_admin(user_id: int):
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM admins 
        WHERE user_id = ?
    ''', (user_id,))
    print(cursor.rowcount)
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="لا يوجد محامي بهذه المعلومات")
    
    conn.commit()
    conn.close()
    return {"detail": "تم حذف المحامي بنجاح"}


class Login(BaseModel):
    email: str
    password: str
    
    
@app.post("/login/")
async def login(login: Login):
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT user_id, username, email, password
        FROM admins 
        WHERE email = ? AND password = ?
        ''', (login.email, login.password))
    user = cursor.fetchone()
    if user:
        return {"detail":user}
    else:
        raise HTTPException(status_code=404, detail="null")
    


    
# #####


# نموذج البيانات للقضية
class Case(BaseModel):
    user_id: int
    case_number: str
    case_year: str
    case_type: str
    first_instance_court: str
    appellate_court: str
    appellate_case_number: str
    appellate_case_year: str
    client_name: str
    client_role: str
    opponent_name: str
    opponent_role: str
    case_subject: str
    power_of_attorney_number: str
    power_of_attorney_year: str



# إضافة قضية
@app.post("/casesadd/")
async def add_case(case: Case):
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Cases (user_id, case_number, case_year, case_type, 
                           first_instance_court, appellate_court, 
                           appellate_case_number, appellate_case_year, 
                           client_name, client_role, opponent_name, 
                           opponent_role, case_subject, 
                           power_of_attorney_number, power_of_attorney_year
                           ) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (case.user_id, case.case_number, case.case_year, case.case_type, 
          case.first_instance_court, case.appellate_court, 
          case.appellate_case_number, case.appellate_case_year, 
          case.client_name, case.client_role, case.opponent_name, 
          case.opponent_role, case.case_subject, 
          case.power_of_attorney_number, case.power_of_attorney_year
          ))
    conn.commit()
    conn.close()
    return {"detail": "Case added successfully"}

# تعديل قضية
@app.post("/casesedit/")
async def update_case(case: Case):
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE Cases 
        SET case_number = ?, case_year = ?, case_type = ?, 
            first_instance_court = ?, appellate_court = ?, 
            appellate_case_number = ?, appellate_case_year = ?, 
            client_name = ?, client_role = ?, opponent_name = ?, 
            opponent_role = ?, case_subject = ?, 
            power_of_attorney_number = ?, power_of_attorney_year = ?
        WHERE case_number = ? AND user_id = ?
    ''', (case.case_number ,case.case_year, case.case_type, 
          case.first_instance_court, case.appellate_court, 
          case.appellate_case_number, case.appellate_case_year, 
          case.client_name, case.client_role, case.opponent_name, 
          case.opponent_role, case.case_subject, 
          case.power_of_attorney_number, case.power_of_attorney_year, 
           case.case_number,case.user_id))
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Case not found")
    
    conn.commit()
    conn.close()
    return {"detail": "Case updated successfully"}


class Casesone(BaseModel):
    user_id: int
    case_number: str

@app.post("/caseone/")
async def get_cases_by_userone(case: Casesone):
    try:
        conn = sqlite3.connect(database)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
                SELECT * FROM Cases WHERE user_id = ? AND case_number = ?
            ''', (case.user_id, case.case_number))
        
        cases = cursor.fetchall()
    
        if not cases:
            raise HTTPException(status_code=404, detail="No cases found for this user")
        
        return cases 
    finally:
        conn.close()

class Casesalls(BaseModel):
    user_id: int
    last_session_date: str

@app.post("/casesall/")
async def get_cases_by_usera(case: Casesalls):
    try:
        conn = sqlite3.connect(database)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
    SELECT s.session_id, c.case_number, s.session_rol, s.session_hasr, s.session_date, s.session_decision, 
           c.user_id, c.case_year, c.case_type, c.first_instance_court,
           c.appellate_court, c.appellate_case_number, c.appellate_case_year,
           c.client_name, c.client_role, c.opponent_name, c.opponent_role,
           c.case_subject, c.power_of_attorney_number, c.power_of_attorney_year
    FROM Sessions s
    JOIN Cases c ON s.case_number = c.case_number
    WHERE s.session_date = ?  AND c.user_id = ?
''',(case.last_session_date,case.user_id))
        
        cases = cursor.fetchall()
        

        
        if not cases:
            raise HTTPException(status_code=404, detail="No cases found for this user")
        
        return cases 
    finally:
        conn.close()
        
class Casesallsweek(BaseModel):
    user_id: int
    
from datetime import datetime, timedelta

@app.post("/casesallweek/")
async def get_casesweek_usera(case: Casesallsweek):
    try: 
        conn = sqlite3.connect(database)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        today = date.today()
        next_week = today + timedelta(days=7)
        cursor.execute('''
    SELECT s.session_id, c.case_number,s.session_rol, s.session_hasr, s.session_date, s.session_decision, 
           c.user_id, c.case_year, c.case_type, c.first_instance_court,
           c.appellate_court, c.appellate_case_number, c.appellate_case_year,
           c.client_name, c.client_role, c.opponent_name, c.opponent_role,
           c.case_subject, c.power_of_attorney_number, c.power_of_attorney_year
    FROM Sessions s
    JOIN Cases c ON s.case_number = c.case_number
    WHERE s.session_date BETWEEN ? AND ? 
    AND c.user_id = ?
''',(today.strftime('%d-%m-%Y'),next_week.strftime('%d-%m-%Y'),case.user_id))
        
        cases = cursor.fetchall()
        if not cases:
            raise HTTPException(status_code=404, detail="No cases found for this user")
        
        return cases 
    finally:
        conn.close()

        
class Casesallsempty(BaseModel):
    user_id: int

@app.post("/casesallempty/")
async def get_casesempty_usera(case : Casesallsempty):
    try:
        conn = sqlite3.connect(database)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(''' 
    SELECT s.session_id,s.session_rol, s.session_hasr, s.session_date, s.session_decision, 
           c.user_id,c.case_number, c.case_year, c.case_type, c.first_instance_court,
           c.appellate_court, c.appellate_case_number, c.appellate_case_year,
           c.client_name, c.client_role, c.opponent_name, c.opponent_role,
           c.case_subject, c.power_of_attorney_number, c.power_of_attorney_year
    FROM Cases c
    LEFT JOIN Sessions s ON s.case_number = c.case_number
    WHERE s.session_id IS NULL AND c.user_id = ?
''',(case.user_id,))

        cases = cursor.fetchall()
        
        if not cases:
            raise HTTPException(status_code=404, detail="No cases found without sessions")
        
        return cases 
    finally:
        conn.close()


class Casesallsbyname(BaseModel):
    user_id: int
    name: str
    
@app.post("/casesallname/")
async def get_cases_by_name(case: Casesallsbyname):
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute('''
        SELECT *
        FROM Cases
        WHERE user_id = ? AND (client_name LIKE ? OR opponent_name LIKE ? OR case_number LIKE ? OR first_instance_court LIKE ? OR power_of_attorney_number LIKE ? OR case_subject LIKE ?)
        ''', (case.user_id, f'{case.name}%', f'{case.name}%', f'{case.name}%', f'{case.name}%', f'{case.name}%', f'{case.name}%'))
        return  cursor.fetchall()
    finally:
        conn.close()

class getsessions(BaseModel):
    user_id : int
    case_number: str


@app.post("/sessions/")
async def get_sessions(case : getsessions):
    with sqlite3.connect(database) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Sessions WHERE user_id = ? AND case_number = ?", (case.user_id,case.case_number,))
        sessions = cursor.fetchall()

        if not sessions:
            raise HTTPException(status_code=404, detail="No sessions found for this case number")

        return [dict(session) for session in sessions]

class Session(BaseModel):
    user_id : int
    case_number: str
    session_rol:int
    session_date: str
    session_decision: str
    session_hasr : str

@app.post("/sessionsadd/")
async def add_session(session: Session):
    with sqlite3.connect(database) as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO Sessions (user_id,case_number,session_rol, session_date, session_decision,session_hasr)
            VALUES (?,?, ?,?,?,?)
        ''', (session.user_id,session.case_number,session.session_rol, session.session_date, session.session_decision,session.session_hasr))

        conn.commit()
    
    return {"detail": "Session added successfully"}

class UpdateSession(BaseModel):
    session_id: int
    session_rol: int
    session_decision: str
    session_date: str
    session_hasr: str

@app.post("/update-session/")
async def update_session(data: UpdateSession):
    with sqlite3.connect(database) as conn:
        cursor = conn.cursor()
    
        cursor.execute('''
            UPDATE Sessions
            SET session_decision = ? , session_date = ? ,session_rol = ?, session_hasr = ?
            WHERE session_id = ?
        ''', (data.session_decision,data.session_date,data.session_rol,data.session_hasr, data.session_id))
        conn.commit()
        return {"message": "تم تحديث القرار بنجاح"}

# نموذج بيانات لحذف الجلسة
class DeleteSession(BaseModel):
    session_id: int


@app.delete("/delete-session/")
async def delete_session(data: DeleteSession):
    with sqlite3.connect(database) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM Sessions
            WHERE session_id = ?
        ''', (data.session_id,))
        conn.commit()

# استخدام المسار المطلق

UPLOAD_DIR = 'uploads'
# تأكد من وجود المجلد
os.makedirs(UPLOAD_DIR, exist_ok=True)
    
# @app.post("/upload/{new_filename}")
# async def upload_file(file: UploadFile = File(...), new_filename: str = None):
#     filename = new_filename if new_filename else file.filename
#     file_location = os.path.join(UPLOAD_DIRECTORY, f"{filename}.pdf")
#     with open(file_location, "wb") as f:
#         f.write(await file.read())
#     return {"filename": filename}



@app.post("/uploadpdf/{new_filename}")
async def upload_pdf(new_filename: str, files: list[UploadFile] = File(...)):
    pdf_path = os.path.join(UPLOAD_DIR, f"{new_filename}.pdf")
    
    # تحقق إذا كان ملف PDF موجودًا
    if os.path.exists(pdf_path):
        # إذا كان الملف موجودًا، نضيف الصور إليه
        try:
            # قراءة الملف الموجود
            reader = PdfReader(pdf_path)
            writer = PdfWriter()

            # نسخ جميع الصفحات من الـ PDF الموجود
            for page in reader.pages:
                writer.add_page(page)

            # إضافة الصور إلى الـ PDF
            for file in files:
                temp_pdf = "temp_image_page.pdf"
                pdf = FPDF()
                pdf.add_page()

                # حساب أبعاد الصفحة (A4 هو الحجم القياسي)
                page_width = pdf.w
                page_height = pdf.h
                
                # مسار الصورة المؤقت
                image_path = os.path.join(UPLOAD_DIR, file.filename)
                
                # حفظ الصورة مؤقتًا
                with open(image_path, 'wb') as image_file:
                    image_file.write(await file.read())
                
                # استخدام PIL للحصول على أبعاد الصورة الأصلية
                with Image.open(image_path) as img:
                    img_width, img_height = img.size
                
                # حساب النسب وتعديل حجم الصورة بحيث تحافظ على النسبة الأصلية
                # حساب نسبة التوسيع للعرض والارتفاع
                width_ratio = page_width / img_width
                height_ratio = page_height / img_height
                
                # اختر النسبة الأصغر لتجنب التشويه
                scale_ratio = min(width_ratio, height_ratio)
                
                # حساب الأبعاد الجديدة
                new_width = img_width * scale_ratio
                new_height = img_height * scale_ratio
                
                # إضافة الصورة إلى PDF بحجم مناسب
                pdf.image(image_path, x=0, y=0, w=new_width, h=new_height)
                pdf.output(temp_pdf)

                # قراءة الملف المؤقت الذي يحتوي على الصورة
                image_pdf_reader = PdfReader(temp_pdf)
                image_pdf_page = image_pdf_reader.pages[0]
                writer.add_page(image_pdf_page)

                # حذف الصورة المؤقتة
                os.remove(image_path)
                os.remove(temp_pdf)

            # حفظ الـ PDF المعدل
            with open(pdf_path, "wb") as output_file:
                writer.write(output_file)

            return {"message": "تم إضافة الصور بنجاح إلى ملف PDF!"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    else:
        # إذا لم يكن الملف موجودًا، نخلق ملف PDF جديد
        try:
            writer = PdfWriter()

            # إضافة الصور إلى الـ PDF الجديد
            for file in files:
                temp_pdf = "temp_image_page.pdf"
                pdf = FPDF()
                pdf.add_page()

                # حساب أبعاد الصفحة (A4 هو الحجم القياسي)
                page_width = pdf.w
                page_height = pdf.h
                
                # مسار الصورة المؤقت
                image_path = os.path.join(UPLOAD_DIR, file.filename)
                
                # حفظ الصورة مؤقتًا
                with open(image_path, 'wb') as image_file:
                    image_file.write(await file.read())
                
                # استخدام PIL للحصول على أبعاد الصورة الأصلية
                with Image.open(image_path) as img:
                    img_width, img_height = img.size
                
                # حساب النسب وتعديل حجم الصورة بحيث تحافظ على النسبة الأصلية
                # حساب نسبة التوسيع للعرض والارتفاع
                width_ratio = page_width / img_width
                height_ratio = page_height / img_height
                
                # اختر النسبة الأصغر لتجنب التشويه
                scale_ratio = min(width_ratio, height_ratio)
                
                # حساب الأبعاد الجديدة
                new_width = img_width * scale_ratio
                new_height = img_height * scale_ratio
                
                # إضافة الصورة إلى PDF بحجم مناسب
                pdf.image(image_path, x=0, y=0, w=new_width, h=new_height)
                pdf.output(temp_pdf)

                # قراءة الملف المؤقت الذي يحتوي على الصورة
                image_pdf_reader = PdfReader(temp_pdf)
                image_pdf_page = image_pdf_reader.pages[0]
                writer.add_page(image_pdf_page)

                # حذف الصورة المؤقتة
                os.remove(image_path)
                os.remove(temp_pdf)

            # إنشاء ملف PDF جديد
            with open(pdf_path, "wb") as output_file:
                writer.write(output_file)

            return {"message": "تم إنشاء ملف PDF جديد وإضافة الصور بنجاح!"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, f"{filename}.pdf")
    if not os.path.exists(file_path):
        return {"error": "File not found"}
    return FileResponse(file_path)

class removeimgpdf(BaseModel):
    name: str
    delete : int
    
@app.post("/removeimg/")
async def removeimg(case: removeimgpdf):
    page_to_delete = case.delete - 1  
    reader = PdfReader(f"uploads/{case.name}.pdf")
    writer = PdfWriter()
    cont = 0
    # نسخ كل الصفحات من PDF الأصلي ما عدا الصفحة التي نريد حذفها
    for i, page in enumerate(reader.pages):
        cont = i
        if i != page_to_delete:
            
            writer.add_page(page)
            
    if cont < page_to_delete:
        print(cont)
        raise HTTPException(status_code=404,detail="error")
    else:
        with open(f"uploads/{case.name}.pdf", "wb") as output_file:
            writer.write(output_file)
    

class ArshefCase(BaseModel):
    user_id: int
    case_number: str
    case_year: str
    case_type: str
    first_instance_court: str
    appellate_court: str
    appellate_case_number: str
    appellate_case_year: str
    client_name: str
    client_role: str
    opponent_name: str
    opponent_role: str
    case_subject: str
    power_of_attorney_number: str
    power_of_attorney_year: str
    

@app.post("/Arshefcases/")
async def create_arshefcase(case: ArshefCase):
    with sqlite3.connect(database) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM Arshef WHERE user_id = ? AND case_number = ?', (case.user_id, case.case_number))
        existing_case = cursor.fetchone()

        if existing_case:
            # إذا كان موجودًا، استخدم INSERT OR REPLACE
            cursor.execute('''
                INSERT OR REPLACE INTO Arshef (
                    user_id, case_number, case_year, case_type, 
                    first_instance_court, appellate_court, 
                    appellate_case_number, appellate_case_year, 
                    client_name, client_role, opponent_name, 
                    opponent_role, case_subject, 
                    power_of_attorney_number, power_of_attorney_year) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (case.user_id, case.case_number, case.case_year, case.case_type, 
                case.first_instance_court, case.appellate_court, 
                case.appellate_case_number, case.appellate_case_year, 
                case.client_name, case.client_role, case.opponent_name, 
                case.opponent_role, case.case_subject, 
                case.power_of_attorney_number, case.power_of_attorney_year))
            conn.commit()
            return {"detail": "تم تحديث البيانات في الارشيف"}
        else:
            # إذا لم يكن موجودًا، قم بإدخاله كإدخال جديد
            cursor.execute('''
                INSERT INTO Arshef (
                    user_id, case_number, case_year, case_type, 
                    first_instance_court, appellate_court, 
                    appellate_case_number, appellate_case_year, 
                    client_name, client_role, opponent_name, 
                    opponent_role, case_subject, 
                    power_of_attorney_number, power_of_attorney_year
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (case.user_id, case.case_number, case.case_year, case.case_type, 
                case.first_instance_court, case.appellate_court, 
                case.appellate_case_number, case.appellate_case_year, 
                case.client_name, case.client_role, case.opponent_name, 
                case.opponent_role, case.case_subject, 
                case.power_of_attorney_number, case.power_of_attorney_year))
            conn.commit()
            return {"detail": "تم الحفظ في الارشيف"}


class ArshefCasesalls(BaseModel):
    user_id: int

@app.post("/archefcasesall/")
async def get_Arshefcases_by_usera(case: ArshefCasesalls):
    try:
        conn = sqlite3.connect(database)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
                SELECT * FROM Arshef WHERE user_id = ? 
            ''', (case.user_id,))
        
        archefcases = cursor.fetchall()
        

        
        if not archefcases:
            raise HTTPException(status_code=404, detail="No cases found for this user")
        
        return archefcases 
    finally:
        conn.close()


class arshefallsbyname(BaseModel):
    user_id: int
    name: str
    
@app.post("/arshefallsbyname/")
async def get_arshef_by_name(case: arshefallsbyname):
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute('''
        SELECT *
        FROM Arshef
        WHERE user_id = ? AND (client_name LIKE ? OR opponent_name LIKE ? OR case_number LIKE ? OR first_instance_court LIKE ? OR power_of_attorney_number LIKE ? OR case_subject LIKE ?)
        ''', (case.user_id, f'{case.name}%', f'{case.name}%', f'{case.name}%', f'{case.name}%', f'{case.name}%', f'{case.name}%'))
        return  cursor.fetchall()
    finally:
        conn.close()
        
class nmozgreq(BaseModel):
    user_id : int
    nmozg_name: str
    nmozg_decision: str

@app.post("/add_nmozg/")
def add_nmozg(nmozg: nmozgreq):
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO nmozg (user_id,nmozg_name, nmozg_decision)
    VALUES (?,?, ?);
''', (nmozg.user_id,nmozg.nmozg_name, nmozg.nmozg_decision))
    conn.commit()
    conn.close()
    return {"detail": "تم اضافة نموزج بنجاح"}     

class allnmozg(BaseModel):
    user_id: int

@app.post("/all_nmozg/")
async def get_all_nmozg_usera(case : allnmozg):
    try:
        conn = sqlite3.connect(database)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(''' 
    SELECT * FROM nmozg
    WHERE user_id = ?
''',(case.user_id,))

        nmozg = cursor.fetchall()
        
        if not nmozg:
            raise HTTPException(status_code=404, detail="No cases found without sessions")
        
        return nmozg 
    finally:
        conn.close()


if __name__ =="__main__":
    uvicorn.run("main:app",host="10.1.130.219",port=8080,reload=True)
