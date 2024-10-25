from fastapi import FastAPI, HTTPException
from fastapi import  File, UploadFile
from fastapi.responses import FileResponse
import os
import sqlite3
import uvicorn
from pydantic import BaseModel

database = 'lowyer.db'

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
        last_session_date TEXT,
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
        last_session_date TEXT,
        FOREIGN KEY (user_id) REFERENCES admins(user_id)
    )
    ''')

    # إنشاء جدول الجلسات
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Sessions (
        session_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        case_number TEXT,
        session_date TEXT,
        session_decision TEXT,
        FOREIGN KEY (case_number) REFERENCES Cases(case_number)
    )
    ''')

    
    conn.commit()
    conn.close()

create()



app = FastAPI()

@app.get("/admins")
def home():
    conn = sqlite3.connect()
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
    print(cursor.rowcount)
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
    last_session_date: str



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
                           power_of_attorney_number, power_of_attorney_year, 
                           last_session_date) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (case.user_id, case.case_number, case.case_year, case.case_type, 
          case.first_instance_court, case.appellate_court, 
          case.appellate_case_number, case.appellate_case_year, 
          case.client_name, case.client_role, case.opponent_name, 
          case.opponent_role, case.case_subject, 
          case.power_of_attorney_number, case.power_of_attorney_year, 
          case.last_session_date))
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
            power_of_attorney_number = ?, power_of_attorney_year = ?, 
            last_session_date = ? 
        WHERE case_number = ? AND user_id = ?
    ''', (case.case_number ,case.case_year, case.case_type, 
          case.first_instance_court, case.appellate_court, 
          case.appellate_case_number, case.appellate_case_year, 
          case.client_name, case.client_role, case.opponent_name, 
          case.opponent_role, case.case_subject, 
          case.power_of_attorney_number, case.power_of_attorney_year, 
          case.last_session_date, case.case_number,case.user_id))
    
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
                SELECT * FROM Cases WHERE user_id = ? AND last_session_date = ?
            ''', (case.user_id, case.last_session_date))
        
        cases = cursor.fetchall()
        

        
        if not cases:
            raise HTTPException(status_code=404, detail="No cases found for this user")
        
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
    case_number: str


@app.post("/sessions/")
async def get_sessions(case : getsessions):
    with sqlite3.connect(database) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Sessions WHERE case_number = ?", (case.case_number,))
        sessions = cursor.fetchall()

        if not sessions:
            raise HTTPException(status_code=404, detail="No sessions found for this case number")

        return [dict(session) for session in sessions]

class Session(BaseModel):
    user_id : int
    case_number: str
    session_date: str
    session_decision: str

@app.post("/sessionsadd/")
async def add_session(session: Session):
    with sqlite3.connect(database) as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO Sessions (user_id,case_number, session_date, session_decision)
            VALUES (?,?, ?, ?)
        ''', (session.user_id,session.case_number, session.session_date, session.session_decision))

        conn.commit()
    
    return {"detail": "Session added successfully"}


# استخدام المسار المطلق
UPLOAD_DIRECTORY = "/tmp/uploads"

# تأكد من وجود المجلد
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)
    
@app.post("/upload/{new_filename}")
async def upload_file(file: UploadFile = File(...), new_filename: str = None):
    # إذا تم توفير اسم جديد، استخدمه، وإلا استخدم الاسم الأصلي
    filename = new_filename if new_filename else file.filename
    file_location = os.path.join(UPLOAD_DIRECTORY, filename)
    
    with open(file_location, "wb") as f:
        f.write(await file.read())
    
    return {"filename": filename}


@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(UPLOAD_DIRECTORY, filename)
    if not os.path.exists(file_path):
        return {"error": "File not found"}
    return FileResponse(file_path)


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
    last_session_date: str
    

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
                    power_of_attorney_number, power_of_attorney_year, 
                    last_session_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (case.user_id, case.case_number, case.case_year, case.case_type, 
                case.first_instance_court, case.appellate_court, 
                case.appellate_case_number, case.appellate_case_year, 
                case.client_name, case.client_role, case.opponent_name, 
                case.opponent_role, case.case_subject, 
                case.power_of_attorney_number, case.power_of_attorney_year, 
                case.last_session_date))
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
                    power_of_attorney_number, power_of_attorney_year, 
                    last_session_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (case.user_id, case.case_number, case.case_year, case.case_type, 
                case.first_instance_court, case.appellate_court, 
                case.appellate_case_number, case.appellate_case_year, 
                case.client_name, case.client_role, case.opponent_name, 
                case.opponent_role, case.case_subject, 
                case.power_of_attorney_number, case.power_of_attorney_year, 
                case.last_session_date))
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

# if __name__ =="__main__":
#     uvicorn.run("main:app",host="10.1.133.37",port=8080,reload=True)
