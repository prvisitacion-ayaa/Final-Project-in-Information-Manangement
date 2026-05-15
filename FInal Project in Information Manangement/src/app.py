from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
import mysql.connector
import csv
import io
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'CCCS105'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.before_request
def require_login():
    allowed_routes = ['login', 'static']
    if 'user_id' not in session and request.endpoint not in allowed_routes:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials!', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) as count FROM vehicles")
    v_count = cursor.fetchone()['count']
    cursor.execute("SELECT COUNT(*) as count FROM parking_slots WHERE status = 'Available'")
    s_count = cursor.fetchone()['count']
    query = """
        SELECT zone, 
               COUNT(*) as total_slots,
               SUM(CASE WHEN status = 'Occupied' THEN 1 ELSE 0 END) as occupied_count
        FROM parking_slots
        GROUP BY zone
        ORDER BY zone ASC
    """
    cursor.execute(query)
    building_stats = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('dashboard.html', v_count=v_count, s_count=s_count, building_stats=building_stats)

@app.route('/vehicles', methods=['GET', 'POST'])
def vehicles():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    search = request.args.get('search', '')
    if search:
        cursor.execute("SELECT * FROM vehicles WHERE owner_name LIKE %s OR plate_number LIKE %s", (f'%{search}%', f'%{search}%'))
    else:
        cursor.execute("SELECT * FROM vehicles")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('vehicles.html', vehicles=data)

@app.route('/vehicles/add', methods=['POST'])
def add_vehicle():
    owner = request.form['owner_name']
    plate = request.form['plate_number']
    v_type = request.form['vehicle_type']
    contact = request.form['contact_number']
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO vehicles (owner_name, plate_number, vehicle_type, contact_number) VALUES (%s, %s, %s, %s)", (owner, plate, v_type, contact))
        conn.commit()
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('vehicles'))

@app.route('/vehicles/delete/<int:id>')
def delete_vehicle(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM reservations WHERE vehicle_id = %s", (id,))
        cursor.execute("DELETE FROM vehicles WHERE id = %s", (id,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('vehicles'))

@app.route('/slots')
def slots():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT s.*, v.plate_number 
        FROM parking_slots s
        LEFT JOIN reservations r ON s.id = r.slot_id AND r.status = 'Active'
        LEFT JOIN vehicles v ON r.vehicle_id = v.id
    """
    cursor.execute(query)
    all_slots = cursor.fetchall()
    cursor.execute("SELECT id, plate_number FROM vehicles")
    all_vehicles = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('slots.html', slots=all_slots, vehicles=all_vehicles)

@app.route('/occupy/<int:slot_id>', methods=['POST'])
def occupy_slot(slot_id):
    vehicle_id = request.form.get('vehicle_id')
    if not vehicle_id:
        return redirect(url_for('slots'))
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE parking_slots SET status = 'Occupied' WHERE id = %s", (slot_id,))
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("INSERT INTO reservations (vehicle_id, slot_id, time_in, status) VALUES (%s, %s, %s, 'Active')", (vehicle_id, slot_id, now))
        conn.commit()
    except:
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('slots'))

@app.route('/release/<int:slot_id>')
def release_slot(slot_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE parking_slots SET status = 'Available' WHERE id = %s", (slot_id,))
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("UPDATE reservations SET time_out = %s, status = 'Completed' WHERE slot_id = %s AND status = 'Active'", (now, slot_id))
        conn.commit()
    except:
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('slots'))

@app.route('/reservations')
def reservations():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT r.*, IFNULL(v.plate_number, 'DELETED') as plate_number, s.slot_number 
        FROM reservations r
        LEFT JOIN vehicles v ON r.vehicle_id = v.id
        JOIN parking_slots s ON r.slot_id = s.id
        ORDER BY r.time_in DESC
    """
    cursor.execute(query)
    all_res = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('reservations.html', reservations=all_res)

@app.route('/export/vehicles')
def export_vehicles():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vehicles")
    rows = cursor.fetchall()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Owner', 'Plate', 'Type', 'Contact'])
    writer.writerows(rows)
    return Response(output.getvalue(), mimetype="text/csv", headers={"Content-disposition": "attachment; filename=vehicles.csv"})

if __name__ == '__main__':
    app.run(debug=True)
