from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
from koneksi import buat_koneksi

app = Flask(__name__)
app.secret_key = 'kunci_rahasia_perpustakaan'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        input_username = request.form['username']
        input_email = request.form['email']
        input_password = request.form['password']
        
        conn = buat_koneksi()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "INSERT INTO users (id_user, email, password_hash, nama, role, is_active) VALUES (%s, %s, %s, %s, 'siswa', 1)",
                (input_username, input_email, input_password, input_username)
            )
            cursor.execute(
                "INSERT INTO anggota (id_anggota, nama_lengkap, kelas, email, status_keanggotaan) VALUES (%s, %s, '-', %s, 'aktif')",
                (input_username, input_username, input_email)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('index'))
        except Exception as e:
            conn.rollback()
            cursor.close()
            conn.close()
            return f"Registrasi Gagal: {e} <a href='/signup'>Coba lagi</a>"
            
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        input_user = request.form['username']
        input_password = request.form['password']
        
        conn = buat_koneksi()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id_user = %s AND password_hash = %s AND is_active = 1", (input_user, input_password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user:
            session['id_user'] = user['id_user']
            session['nama'] = user['nama']
            session['role'] = user['role']
            
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user['role'] == 'kepsek':
                return redirect(url_for('kepsek_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            return "Login Gagal! Username atau Password salah. <a href='/'>Coba lagi</a>"
            
    return render_template('index.html')

# ==========================================================
# ===================== DASHBOARD ADMIN =====================
# ==========================================================

@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') == 'admin':
        conn = buat_koneksi()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT SUM(jumlah_total) as total FROM buku")
        res_buku = cursor.fetchone()
        total_buku = res_buku['total'] if res_buku and res_buku['total'] else 0
        
        cursor.execute("SELECT COUNT(*) as total FROM peminjaman WHERE status = 'dipinjam'")
        res_pinjam = cursor.fetchone()
        sedang_dipinjam = res_pinjam['total'] if res_pinjam and res_pinjam['total'] else 0
        
        cursor.execute("SELECT COUNT(*) as total FROM anggota")
        res_user = cursor.fetchone()
        total_pengguna = res_user['total'] if res_user and res_user['total'] else 0
        
        cursor.execute("SELECT SUM(denda_telat + denda_rusak) as total FROM pengembalian")
        res_denda = cursor.fetchone()
        total_denda = res_denda['total'] if res_denda and res_denda['total'] else 0
        
        cursor.execute("""
            SELECT peminjaman.*, anggota.nama_lengkap as nama_peminjam, buku.judul 
            FROM peminjaman 
            JOIN anggota ON peminjaman.id_anggota = anggota.id_anggota 
            JOIN buku ON peminjaman.id_buku = buku.id_buku 
            ORDER BY peminjaman.id_peminjaman DESC LIMIT 5
        """)
        transaksi_terbaru = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('admin/dashboard.html', 
                               total_buku=total_buku, 
                               sedang_dipinjam=sedang_dipinjam, 
                               total_pengguna=total_pengguna, 
                               total_denda=total_denda,
                               transaksi_terbaru=transaksi_terbaru)
    return redirect(url_for('login'))

@app.route('/admin/kelolabuku', methods=['GET', 'POST'])
def admin_kelolabuku():
    if session.get('role') == 'admin':
        conn = buat_koneksi()
        cursor = conn.cursor(dictionary=True)
        
        if request.method == 'POST':
            judul = request.form['judul']
            penulis = request.form['penulis']
            nama_kategori = request.form['kategori']
            tahun_terbit = request.form['tahun_terbit']
            jumlah = int(request.form['jumlah'])
            
            cursor.execute("SELECT id_kategori FROM kategori WHERE nama_kategori = %s", (nama_kategori,))
            kat = cursor.fetchone()
            if kat:
                id_kategori = kat['id_kategori']
            else:
                cursor.execute("INSERT INTO kategori (nama_kategori) VALUES (%s)", (nama_kategori,))
                conn.commit()
                id_kategori = cursor.lastrowid
                
            cursor.execute("""
                INSERT INTO buku (judul, penulis, id_kategori, tahun_terbit, jumlah_total, jumlah_tersedia) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (judul, penulis, id_kategori, tahun_terbit, jumlah, jumlah))
            conn.commit()
            
            cursor.close()
            conn.close()
            return redirect(url_for('admin_kelolabuku'))
            
        cursor.execute("""
            SELECT buku.*, kategori.nama_kategori as kategori 
            FROM buku 
            LEFT JOIN kategori ON buku.id_kategori = kategori.id_kategori 
            ORDER BY buku.id_buku DESC
        """)
        buku_list = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return render_template('admin/kelolabuku.html', buku_list=buku_list)
    return redirect(url_for('login'))

@app.route('/admin/peminjaman', methods=['GET', 'POST'])
def admin_peminjaman():
    if session.get('role') == 'admin':
        conn = buat_koneksi()
        cursor = conn.cursor(dictionary=True)
        
        if request.method == 'POST':
            id_anggota = request.form['id_anggota']
            id_buku = request.form['id_buku']
            tgl_pinjam = request.form['tgl_pinjam']
            jatuh_tempo = request.form['jatuh_tempo']
            admin_id = session.get('id_user')
            
            cursor.execute("""
                INSERT INTO peminjaman (id_anggota, id_buku, tgl_pinjam, jatuh_tempo, status, diproses_oleh) 
                VALUES (%s, %s, %s, %s, 'dipinjam', %s)
            """, (id_anggota, id_buku, tgl_pinjam, jatuh_tempo, admin_id))
            
            cursor.execute("UPDATE buku SET jumlah_tersedia = jumlah_tersedia - 1 WHERE id_buku = %s", (id_buku,))
            conn.commit()
            
            cursor.close()
            conn.close()
            return redirect(url_for('admin_peminjaman'))
            
        cursor.execute("SELECT id_anggota, nama_lengkap as nama FROM anggota")
        anggota_list = cursor.fetchall()
        
        cursor.execute("SELECT id_buku, judul, jumlah_tersedia FROM buku WHERE jumlah_tersedia > 0")
        buku_list = cursor.fetchall()
        
        cursor.execute("SELECT * FROM peminjaman ORDER BY id_peminjaman DESC")
        peminjaman_list = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return render_template('admin/peminjaman.html', 
                               anggota_list=anggota_list, 
                               buku_list=buku_list, 
                               peminjaman_list=peminjaman_list)
    return redirect(url_for('login'))

@app.route('/admin/pengembalian', methods=['GET', 'POST'])
def admin_pengembalian():
    if session.get('role') == 'admin':
        conn = buat_koneksi()
        cursor = conn.cursor(dictionary=True)
        
        if request.method == 'POST':
            id_peminjaman = request.form['id_peminjaman']
            tgl_kembali = request.form['tgl_kembali']
            kondisi_buku = request.form['kondisi_buku']
            total_denda = float(request.form.get('denda', 0))
            admin_id = session.get('id_user')
            
            cursor.execute("SELECT * FROM peminjaman WHERE id_peminjaman = %s", (id_peminjaman,))
            peminjaman = cursor.fetchone()
            
            if peminjaman:
                id_buku = peminjaman['id_buku']
                
                denda_telat = total_denda if kondisi_buku == 'Baik' else 0
                denda_rusak = total_denda if kondisi_buku != 'Baik' else 0
                
                cursor.execute("""
                    INSERT INTO pengembalian (id_peminjaman, tgl_kembali, kondisi_buku, denda_telat, denda_rusak, diproses_oleh) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (id_peminjaman, tgl_kembali, 'baik' if kondisi_buku=='Baik' else ('rusak ringan' if kondisi_buku=='Rusak Ringan' else 'rusak berat'), denda_telat, denda_rusak, admin_id))
                
                cursor.execute("UPDATE peminjaman SET status = 'dikembalikan' WHERE id_peminjaman = %s", (id_peminjaman,))
                cursor.execute("UPDATE buku SET jumlah_tersedia = jumlah_tersedia + 1 WHERE id_buku = %s", (id_buku,))
                
                conn.commit()
            
            cursor.close()
            conn.close()
            return redirect(url_for('admin_pengembalian'))
        
        cursor.execute("SELECT * FROM pengaturan")
        pengaturan_rows = cursor.fetchall()
        settings = {row['kunci']: row['nilai'] for row in pengaturan_rows}
        
        cursor.execute("""
            SELECT peminjaman.*, anggota.nama_lengkap as nama_anggota, buku.judul 
            FROM peminjaman 
            JOIN anggota ON peminjaman.id_anggota = anggota.id_anggota 
            JOIN buku ON peminjaman.id_buku = buku.id_buku 
            WHERE peminjaman.status = 'dipinjam'
        """)
        peminjaman_aktif = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('admin/pengembalian.html', 
                               settings=settings, 
                               peminjaman_aktif=peminjaman_aktif)
    return redirect(url_for('login'))

@app.route('/admin/biodataagt')
def admin_biodataagt():
    if session.get('role') == 'admin':
        conn = buat_koneksi()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM anggota ORDER BY id_anggota DESC")
        anggota_list = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('admin/biodataagt.html', anggota_list=anggota_list)
    return redirect(url_for('login'))

@app.route('/admin/tambah_anggota', methods=['POST'])
def tambah_anggota():
    if session.get('role') == 'admin':
        nama = request.form['nama']
        kelas = request.form['kelas']
        no_hp = request.form['no_hp']
        
        id_baru = "AGT" + datetime.now().strftime("%d%H%M")
        email_dummy = f"{id_baru.lower()}@sekolah.sch.id"
        
        conn = buat_koneksi()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "INSERT INTO users (id_user, email, password_hash, nama, role, is_active) VALUES (%s, %s, '123456', %s, 'siswa', 1)",
                (id_baru, email_dummy, nama)
            )
            cursor.execute("""
                INSERT INTO anggota (id_anggota, nama_lengkap, kelas, email, no_hp, status_keanggotaan, tanggal_bergabung) 
                VALUES (%s, %s, %s, %s, %s, 'aktif', CURDATE())
            """, (id_baru, nama, kelas, email_dummy, no_hp))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Error tambah anggota: {e}")
            
        cursor.close()
        conn.close()
        return redirect(url_for('admin_biodataagt'))
    return redirect(url_for('login'))

@app.route('/admin/hapus_anggota/<id_anggota>')
def hapus_anggota(id_anggota):
    if session.get('role') == 'admin':
        conn = buat_koneksi()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM users WHERE id_user = %s", (id_anggota,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Error hapus anggota: {e}")
            
        cursor.close()
        conn.close()
        return redirect(url_for('admin_biodataagt'))
    return redirect(url_for('login'))

# ==========================================================
# ===================== DASHBOARD USER ======================
# ==========================================================

@app.route('/user/dashboard')
def user_dashboard():
    if session.get('role') in ['siswa', 'user']:
        conn = buat_koneksi()
        cursor = conn.cursor(dictionary=True)
        user_id = session.get('id_user')
        
        cursor.execute("SELECT COUNT(*) as total FROM peminjaman WHERE id_anggota = %s AND status = 'dipinjam'", (user_id,))
        res1 = cursor.fetchone()
        jml_dipinjam = res1['total'] if res1 else 0
        
        cursor.execute("SELECT COUNT(*) as total FROM peminjaman WHERE id_anggota = %s AND status = 'menunggu'", (user_id,))
        res2 = cursor.fetchone()
        jml_menunggu = res2['total'] if res2 else 0
        
        cursor.close()
        conn.close()
        return render_template('user/dashboard.html', jml_dipinjam=jml_dipinjam, jml_menunggu=jml_menunggu)
    return redirect(url_for('login'))

@app.route('/user/databuku')
def user_databuku():
    if session.get('role') in ['siswa', 'user']:
        conn = buat_koneksi()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT buku.*, kategori.nama_kategori as kategori 
            FROM buku 
            LEFT JOIN kategori ON buku.id_kategori = kategori.id_kategori 
            ORDER BY buku.id_buku DESC
        """)
        buku_list = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('user/Databuku.html', buku_list=buku_list)
    return redirect(url_for('login'))

@app.route('/user/peminjaman')
def user_peminjaman():
    if session.get('role') in ['siswa', 'user']:
        conn = buat_koneksi()
        cursor = conn.cursor(dictionary=True)
        user_id = session.get('id_user')
        cursor.execute("""
            SELECT peminjaman.*, buku.judul, buku.penulis 
            FROM peminjaman 
            JOIN buku ON peminjaman.id_buku = buku.id_buku 
            WHERE peminjaman.id_anggota = %s AND peminjaman.status = 'dipinjam'
        """, (user_id,))
        peminjaman_list = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('user/peminjaman.html', peminjaman_list=peminjaman_list)
    return redirect(url_for('login'))

@app.route('/user/riwayat')
def user_riwayat():
    if session.get('role') in ['siswa', 'user']:
        conn = buat_koneksi()
        cursor = conn.cursor(dictionary=True)
        user_id = session.get('id_user')
        cursor.execute("""
            SELECT peminjaman.*, buku.judul, buku.penulis 
            FROM peminjaman 
            JOIN buku ON peminjaman.id_buku = buku.id_buku 
            WHERE peminjaman.id_anggota = %s 
            ORDER BY peminjaman.id_peminjaman DESC
        """, (user_id,))
        riwayat_list = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('user/riwayat.html', riwayat_list=riwayat_list)
    return redirect(url_for('login'))

@app.route('/user/biodata')
def user_biodata():
    if session.get('role') in ['siswa', 'user']:
        conn = buat_koneksi()
        cursor = conn.cursor(dictionary=True)
        user_id = session.get('id_user')
        
        cursor.execute("SELECT * FROM anggota WHERE id_anggota = %s", (user_id,))
        biodata = cursor.fetchone()
        
        if not biodata:
            biodata = {
                'nama_lengkap': session.get('nama', '-'),
                'email': '-',
                'no_hp': '-',
                'status_keanggotaan': 'Aktif',
                'tanggal_bergabung': '-',
                'masa_berlaku': '-',
                'kelas': '-'
            }
            
        cursor.close()
        conn.close()
        return render_template('user/biodata.html', biodata=biodata)
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)