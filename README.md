# GMIT Student Attendance Panel

A full B.E. attendance management system for **7 branches** (EE, CS, AI, EC, ME, CE, CSD)
across **8 semesters each**, built with **Python + Django + MySQL**.

Three panels:
- **Admin Panel** — approve/reject teacher signups, assign teachers to a branch+semester,
  import student lists from Excel, view branch-wise and semester-wise stats and charts.
- **Teacher Panel** — (only after Admin approval) open an attendance sheet for an assigned
  branch+semester, mark each student Present/Absent with one click (saved instantly, no page
  reload), see running present/absent/total counts and a live date & time.
- **Student/User Panel** — read-only. A student can log in and see only their own attendance
  history and percentage. They cannot mark or edit anything.

---

## 1. What you need installed first

1. **Python 3.10+** — check with `python --version`
2. **MySQL** — easiest is **XAMPP** (as you mentioned) which bundles MySQL + phpMyAdmin.
   Download: https://www.apachefriends.org/
3. **MySQL Workbench** (optional but nice for viewing tables): https://dev.mysql.com/downloads/workbench/
4. **VS Code**

---

## 2. One-time project setup

Open the project folder in VS Code, then open a terminal (`` Ctrl + ` ``) and run these
**one at a time**:

```bash
# 1. Create a virtual environment
python -m venv venv

# 2. Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. Install all required packages
pip install -r requirements.txt
```

> If `mysqlclient` fails to install on Windows, download the matching wheel from
> https://www.lfd.uci.edu/~gohlke/pythonlibs/#mysqlclient and install it with
> `pip install <downloaded_file>.whl`, or simply install `pymysql` instead and let me know —
> I can adjust the settings for you.

---

## 3. Set up the MySQL database

1. Start **XAMPP** and click **Start** next to both **Apache** and **MySQL**.
2. Open **phpMyAdmin** (`http://localhost/phpmyadmin`) or **MySQL Workbench**.
3. Create a new database (exact name matters):
   ```sql
   CREATE DATABASE gmit_attendance_db;
   ```
4. By default XAMPP's MySQL uses username `root` with **no password**. This project's
   `settings.py` already assumes that. If your MySQL has a different username/password,
   set these environment variables before running the server (or edit `settings.py` directly
   in the `DATABASES` section):
   ```bash
   set DB_USER=root
   set DB_PASSWORD=yourpassword
   ```
   (On Mac/Linux use `export` instead of `set`.)

---

## 4. Create the tables and your Admin account

Still inside the activated virtual environment:

```bash
python manage.py makemigrations
python manage.py migrate
```

This builds every table (Students, Teachers, Attendance, etc.) inside `gmit_attendance_db`.

Now create your Admin login:

```bash
python manage.py createsuperuser
```

Enter a username, email, and password when asked. This account automatically gets full
Admin access on the Admin Panel (superusers are always treated as Admin in this app) —
you don't need to edit anything else.

---

## 5. Run the application

```bash
python manage.py runserver
```

You'll see something like:
```
Starting development server at http://127.0.0.1:8000/
```

Open that link in your browser. You'll land on the **Login** page.

- Log in with the Admin username/password you just created → you get the **Admin Dashboard**.
- Anyone can click **Teacher signup** on the login page to create a teacher account — but it
  stays locked until you (Admin) click **Approve** on the Admin Dashboard, and you must then
  click **Manage → Add Assignment** to give that teacher a branch + semester to handle.
- A **student** can only self-register (Student signup) if their **USN already exists** in the
  system — meaning you or a teacher must first import the class list via Excel
  (Admin Dashboard → Import Students).

---

## 6. Importing your student list from Excel

Use the included `sample_students_template.xlsx` as a reference. Required column order:

| Sl.No | USN | Name |
|---|---|---|
| 1 | 1GM22EE001 | Aarav Kumar |
| 2 | 1GM22EE002 | Bhavya Rao |

- First row = header (skipped automatically).
- On the Admin Dashboard, click **Import Students**, choose the Branch and Semester the
  sheet belongs to, and upload the file. Students already present (same USN+branch+semester)
  are skipped, not duplicated.

---

## 7. Everyday use (once set up)

- **Teacher marks attendance:** Teacher Panel → pick a class → click **Present** or
  **Absent** next to each student. It saves immediately (you'll see the badge and the
  running Present/Absent/Total counts update instantly) — no "Save" button needed.
- **Change the date:** use the date box above the table to mark or review a different day
  (e.g., to fix yesterday's attendance).
- **Charts:** Admin Dashboard shows overall attendance % per branch. Each attendance sheet
  shows a Present-vs-Absent bar chart for that specific class.
- **Students:** log in and see only their own record — a doughnut chart and a table of
  their last 60 days, with no edit controls anywhere.

---

## 8. Giving other people access on your Wi-Fi / LAN (phones, other laptops)

By default `runserver` only listens on your own computer (`127.0.0.1`). To let other
devices on the **same Wi-Fi network** (e.g., a teacher's phone, another PC in the same lab)
reach it:

1. Find your computer's local IP address:
   - Windows: open Command Prompt → `ipconfig` → look for **IPv4 Address**, e.g. `192.168.1.24`
   - Mac/Linux: `ifconfig` or `ip addr` → look for something like `192.168.1.24`

2. Run the server bound to all network interfaces instead of just localhost:
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

3. On any other device connected to the **same Wi-Fi router**, open a browser and go to:
   ```
   http://192.168.1.24:8000/
   ```
   (replace with your actual IP from step 1)

4. If it doesn't load, your computer's firewall is likely blocking incoming connections on
   port 8000:
   - **Windows:** Control Panel → Windows Defender Firewall → Advanced Settings → Inbound
     Rules → New Rule → Port → TCP → 8000 → Allow the connection.
   - **Mac:** System Settings → Network → Firewall → allow incoming connections for Python.

> This only works while your computer is on and the `runserver` command is running, and
> only for devices on the same local network (Wi-Fi/LAN) — not the wider internet.

### Making it reachable from anywhere on the internet (optional, later)

That needs real hosting (this is different from just LAN access), for example:
- Deploying to a service like **Render**, **Railway**, or **PythonAnywhere** (similar to how
  you deployed Campus Manager to Render) with a proper MySQL database add-on.
- Setting `DEBUG = False` in `settings.py`, adding your real domain to `ALLOWED_HOSTS`, and
  serving static files with `whitenoise` or a similar tool.

If you want, tell me and I'll walk you through deploying this one to Render step-by-step,
the same way we did Campus Manager.

---

## 9. Project structure (for your reference)

```
gmit_attendance/
├── manage.py
├── requirements.txt
├── sample_students_template.xlsx
├── gmit_project/          # Django project settings & URLs
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── attendance/            # Main app
│   ├── models.py          # CustomUser, Student, Attendance, TeacherProfile, TeacherAssignment
│   ├── views.py           # All page logic (admin/teacher/student panels)
│   ├── forms.py
│   ├── urls.py
│   ├── admin.py            # Django's built-in DB admin (at /django-admin/)
│   └── templatetags/
├── templates/attendance/  # All HTML pages
└── static/css/style.css   # Color scheme & layout
```

Django's own built-in database admin is also available at `http://127.0.0.1:8000/django-admin/`
(login with your superuser) if you ever want to directly view/edit raw table rows.

---

## Quick command summary (after first-time setup)

```bash
venv\Scripts\activate          # (or source venv/bin/activate on Mac/Linux)
python manage.py runserver
```

Then open `http://127.0.0.1:8000/` in your browser.
