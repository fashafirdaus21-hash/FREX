from flask import Flask, render_template, request, redirect, url_for, session
from koneksi import buat_koneksi
import os
import time
from werkzeug.utils import secure_filename
import uuid
import datetime as dt

app = Flask(__name__)

app.config['LAPORAN_UPLOAD_FOLDER'] = os.path.join(
    app.root_path, 'static', 'uploads', 'laporan'
)

app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

os.makedirs(app.config['LAPORAN_UPLOAD_FOLDER'], exist_ok=True)

app.secret_key = 'kunci_rahasia_perpustakaan'

# ==========================================
# KONFIGURASI FOLDER UPLOAD COVER BUKU
# ==========================================
UPLOAD_FOLDER = 'static/uploads/covers'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


BATAS_PEMINJAMAN = 3


def hitung_kuota_terpakai(cursor, id_anggota):
    """
    Menghitung buku yang masih menggunakan kuota.
    Status menunggu dan dipinjam sama-sama dihitung.
    """
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM peminjaman
        WHERE id_anggota = %s
        AND status IN ('menunggu', 'dipinjam')
    """, (id_anggota,))

    hasil = cursor.fetchone()
    return hasil['total'] if hasil else 0


@app.context_processor
def inject_biodata():
    biodata = None

    if session.get('role') in ['siswa', 'user']:
        conn = None
        cursor = None

        try:
            conn = buat_koneksi()
            cursor = conn.cursor(dictionary=True, buffered=True)

            cursor.execute("""
                SELECT *
                FROM anggota
                WHERE id_anggota = %s
            """, (session.get('id_user'),))

            biodata = cursor.fetchone()

        except Exception as e:
            print(f"Gagal mengambil profil: {e}")

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return {'biodata': biodata}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        nama = request.form.get('nama', '').strip()
        kelas = request.form.get('kelas', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        no_hp_raw = request.form.get('no_hp', '').strip()
        no_hp = no_hp_raw if no_hp_raw else None

        if not username or not nama or not kelas or not email or not password:
            return redirect(url_for('signup', status='kosong'))

        conn = buat_koneksi()
        cursor = conn.cursor(dictionary=True, buffered=True)
        try:
            cursor.execute("SELECT id_user FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return redirect(url_for('signup', status='duplikat'))

            cursor.execute(
                """INSERT INTO users (username, email, password_hash, nama, role, is_active)
                   VALUES (%s, %s, %s, %s, 'siswa', 1)""",
                (username, email, password, nama)
            )
            id_user_baru = cursor.lastrowid

            cursor.execute(
                """INSERT INTO anggota (id_anggota, nama_lengkap, kelas, email, no_hp, status_keanggotaan, tanggal_bergabung)
                   VALUES (%s, %s, %s, %s, %s, 'aktif', CURDATE())""",
                (id_user_baru, nama, kelas, email, no_hp)
            )
            conn.commit()
            cursor.close()
            conn.close()

            return redirect(url_for('index', daftar='sukses', username=username, nama=nama))
        except Exception as e:
            conn.rollback()
            cursor.close()
            conn.close()
            if "1062" in str(e):
                return redirect(url_for('signup', status='duplikat'))
            return f"Registrasi Gagal: {e} <a href='/signup'>Coba lagi</a>"

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        input_username = request.form['username'].strip()
        input_password = request.form['password']

        conn = buat_koneksi()
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute(
            "SELECT * FROM users WHERE username = %s AND password_hash = %s AND is_active = 1",
            (input_username, input_password)
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            kelas_user = ''
            if user['role'] in ['siswa', 'user']:
                conn_k = buat_koneksi()
                cursor_k = conn_k.cursor(dictionary=True, buffered=True)
                cursor_k.execute("SELECT kelas FROM anggota WHERE id_anggota = %s", (user['id_user'],))
                agt = cursor_k.fetchone()
                cursor_k.close()
                conn_k.close()
                if agt and agt.get('kelas'):
                    kelas_user = agt['kelas']

            session['id_user'] = user['id_user']
            session['username'] = user['username']
            session['nama'] = user['nama']
            session['role'] = user['role']
            session['kelas'] = kelas_user

            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user['role'] == 'kepsek':
                return redirect(url_for('kepsek_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            return "Login Gagal! Username atau Password salah. <a href='/login'>Coba lagi</a>"

    return render_template('index.html')


# ==========================================================
# ===================== DASHBOARD ADMIN =====================
# ==========================================================

@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') == 'admin':
        conn = buat_koneksi()
        cursor = conn.cursor(dictionary=True, buffered=True)

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

        # Hitung jumlah anggota/member unik yang meminjam buku per bulan (1 - 12)
        cursor.execute("""
            SELECT MONTH(tgl_pinjam) AS bulan, COUNT(DISTINCT id_anggota) AS jumlah_peminjam
            FROM peminjaman
            WHERE tgl_pinjam IS NOT NULL
            GROUP BY MONTH(tgl_pinjam)
        """)
        rows_bulanan = cursor.fetchall()

        # Siapkan list 12 bulan (default 0 untuk bulan yang belum ada peminjaman)
        data_peminjam_bulanan = [0] * 12
        for r in rows_bulanan:
            idx_bulan = int(r['bulan']) - 1
            if 0 <= idx_bulan < 12:
                data_peminjam_bulanan[idx_bulan] = int(r['jumlah_peminjam'])

        cursor.execute("""
            SELECT peminjaman.*, anggota.nama_lengkap as nama_peminjam, buku.judul
            FROM peminjaman
            JOIN anggota ON peminjaman.id_anggota = anggota.id_anggota
            JOIN buku ON peminjaman.id_buku = buku.id_buku
            ORDER BY peminjaman.id_peminjaman DESC LIMIT 10
        """)
        transaksi_terbaru = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('admin/dashboard.html',
                               total_buku=total_buku,
                               sedang_dipinjam=sedang_dipinjam,
                               total_pengguna=total_pengguna,
                               total_denda=total_denda,
                               transaksi_terbaru=transaksi_terbaru,
                               data_peminjam_bulanan=data_peminjam_bulanan)
    return redirect(url_for('login'))


@app.route('/admin/kelolabuku', methods=['GET', 'POST'])
def admin_kelolabuku():
    if session.get('role') == 'admin':
        conn = buat_koneksi()
        cursor = conn.cursor(dictionary=True, buffered=True)

        if request.method == 'POST':
            judul = request.form['judul']
            penulis = request.form['penulis']
            penerbit = request.form.get('penerbit', '').strip() or None
            nama_kategori = request.form['kategori']
            tahun_terbit = request.form['tahun_terbit']
            jumlah = int(request.form['jumlah'])

            nama_file_cover = 'default_cover.jpg'
            if 'cover' in request.files:
                file = request.files['cover']
                if file and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    nama_file_cover = f"{int(time.time())}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], nama_file_cover))

            cursor.execute("SELECT id_kategori FROM kategori WHERE nama_kategori = %s", (nama_kategori,))
            kat = cursor.fetchone()
            if kat:
                id_kategori = kat['id_kategori']
            else:
                cursor.execute("INSERT INTO kategori (nama_kategori) VALUES (%s)", (nama_kategori,))
                conn.commit()
                id_kategori = cursor.lastrowid

            cursor.execute("""
                INSERT INTO buku (
                    judul, cover, penulis, penerbit, id_kategori,
                    tahun_terbit, jumlah_total, jumlah_tersedia
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                judul, nama_file_cover, penulis, penerbit,
                id_kategori, tahun_terbit, jumlah, jumlah
            ))
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
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    conn = buat_koneksi()
    cursor = conn.cursor(dictionary=True, buffered=True)

    try:
        if request.method == 'POST':
            id_anggota = request.form.get('id_anggota')
            id_buku = request.form.get('id_buku')
            tgl_pinjam = request.form.get('tgl_pinjam')
            jatuh_tempo = request.form.get('jatuh_tempo')
            admin_id = session.get('id_user')

            # Kunci data anggota agar transaksi bersamaan
            # tidak melewati batas peminjaman.
            cursor.execute("""
                SELECT id_anggota
                FROM anggota
                WHERE id_anggota = %s
                FOR UPDATE
            """, (id_anggota,))

            anggota = cursor.fetchone()

            if not anggota:
                conn.rollback()
                return redirect(url_for(
                    'admin_peminjaman',
                    status='anggota_tidak_valid'
                ))

            # Proses pengajuan yang sudah kedaluwarsa.
            proses_pengajuan_kedaluwarsa(cursor)

            # Periksa jumlah buku yang menggunakan kuota.
            jumlah_aktif = hitung_kuota_terpakai(
                cursor, id_anggota
            )

            if jumlah_aktif >= BATAS_PEMINJAMAN:
                conn.rollback()
                return redirect(url_for(
                    'admin_peminjaman',
                    status='kuota_penuh'
                ))

            # Periksa dan kunci stok buku.
            cursor.execute("""
                SELECT jumlah_tersedia
                FROM buku
                WHERE id_buku = %s
                FOR UPDATE
            """, (id_buku,))

            buku = cursor.fetchone()

            if not buku or buku['jumlah_tersedia'] <= 0:
                conn.rollback()
                return redirect(url_for(
                    'admin_peminjaman',
                    status='stok_habis'
                ))

            # Simpan peminjaman.
            cursor.execute("""
                INSERT INTO peminjaman (
                    id_anggota,
                    id_buku,
                    tgl_pinjam,
                    jatuh_tempo,
                    status,
                    diproses_oleh
                )
                VALUES (%s, %s, %s, %s, 'dipinjam', %s)
            """, (
                id_anggota,
                id_buku,
                tgl_pinjam,
                jatuh_tempo,
                admin_id
            ))

            # Kurangi stok buku.
            cursor.execute("""
                UPDATE buku
                SET jumlah_tersedia = jumlah_tersedia - 1
                WHERE id_buku = %s
                AND jumlah_tersedia > 0
            """, (id_buku,))

            if cursor.rowcount != 1:
                conn.rollback()
                return redirect(url_for(
                    'admin_peminjaman',
                    status='stok_habis'
                ))

            conn.commit()

            return redirect(url_for(
                'admin_peminjaman',
                status='berhasil'
            ))

        # Mengambil daftar anggota.
        cursor.execute("""
            SELECT id_anggota,
                   nama_lengkap AS nama
            FROM anggota
        """)
        anggota_list = cursor.fetchall()

        # Mengambil buku yang masih tersedia.
        cursor.execute("""
            SELECT id_buku, judul, jumlah_tersedia
            FROM buku
            WHERE jumlah_tersedia > 0
        """)
        buku_list = cursor.fetchall()

        # Mengambil riwayat peminjaman.
        cursor.execute("""
            SELECT peminjaman.*,
                   buku.judul AS judul_buku,
                   COALESCE(
                       admin_user.nama,
                       admin_user.username,
                       '-'
                   ) AS nama_admin
            FROM peminjaman
            LEFT JOIN buku
                ON peminjaman.id_buku = buku.id_buku
            LEFT JOIN users AS admin_user
                ON peminjaman.diproses_oleh = admin_user.id_user
            ORDER BY peminjaman.id_peminjaman DESC
        """)
        peminjaman_list = cursor.fetchall()

        return render_template(
            'admin/peminjaman.html',
            anggota_list=anggota_list,
            buku_list=buku_list,
            peminjaman_list=peminjaman_list
        )

    except Exception as e:
        conn.rollback()
        print("Gagal memproses peminjaman admin:", e)
        return redirect(url_for(
            'admin_peminjaman',
            status='gagal'
        ))

    finally:
        cursor.close()
        conn.close()



@app.route('/admin/peminjaman/terima/<int:id_peminjaman>', methods=['POST'])
def admin_terima_peminjaman(id_peminjaman):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    conn = buat_koneksi()
    cursor = conn.cursor(dictionary=True, buffered=True)

    try:
        # Kunci pengajuan agar tidak diproses dua kali.
        cursor.execute("""
            SELECT id_peminjaman, status
            FROM peminjaman
            WHERE id_peminjaman = %s
            FOR UPDATE
        """, (id_peminjaman,))

        pengajuan = cursor.fetchone()

        if not pengajuan or pengajuan['status'] != 'menunggu':
            conn.rollback()
            return redirect(url_for(
                'admin_peminjaman',
                status='pengajuan_tidak_valid'
            ))

        # Ambil lama peminjaman dari pengaturan.
        cursor.execute("""
            SELECT nilai
            FROM pengaturan
            WHERE kunci = 'lama_pinjam_hari'
        """)
        pengaturan_pinjam = cursor.fetchone()

        lama_pinjam = int(
            pengaturan_pinjam['nilai']
        ) if pengaturan_pinjam else 7

        admin_id = session.get('id_user')

        # Stok TIDAK dikurangi lagi karena sudah dikurangi
        # saat siswa mengajukan peminjaman.
        cursor.execute("""
            UPDATE peminjaman
            SET tgl_pinjam = CURDATE(),
                jatuh_tempo = DATE_ADD(CURDATE(), INTERVAL %s DAY),
                status = 'dipinjam',
                diproses_oleh = %s
            WHERE id_peminjaman = %s
              AND status = 'menunggu'
        """, (lama_pinjam, admin_id, id_peminjaman))

        if cursor.rowcount != 1:
            conn.rollback()
            return redirect(url_for(
                'admin_peminjaman',
                status='pengajuan_tidak_valid'
            ))

        conn.commit()

        return redirect(url_for(
            'admin_peminjaman',
            status='pengajuan_diterima'
        ))

    except Exception as e:
        conn.rollback()
        print("Gagal menerima pengajuan:", e)
        return redirect(url_for(
            'admin_peminjaman',
            status='gagal'
        ))

    finally:
        cursor.close()
        conn.close()


@app.route('/admin/proses_pengajuan/<int:id_peminjaman>', methods=['POST'])
def admin_proses_pengajuan(id_peminjaman):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    aksi = request.form.get('aksi')
    admin_id = session.get('id_user')

    conn = buat_koneksi()
    cursor = conn.cursor(dictionary=True, buffered=True)

    try:
        # Periksa pengajuan yang sudah melewati 24 jam
        proses_pengajuan_kedaluwarsa(cursor)

        cursor.execute("""
            SELECT id_peminjaman, id_buku, status
            FROM peminjaman
            WHERE id_peminjaman = %s
            FOR UPDATE
        """, (id_peminjaman,))

        pengajuan = cursor.fetchone()

        if not pengajuan or pengajuan['status'] != 'menunggu':
            conn.commit()
            return redirect(url_for('admin_peminjaman'))

        if aksi == 'setujui':
            cursor.execute("""
                SELECT nilai
                FROM pengaturan
                WHERE kunci = 'lama_pinjam_hari'
            """)

            pengaturan = cursor.fetchone()
            lama_pinjam = int(pengaturan['nilai']) if pengaturan else 7

            # Stok TIDAK dikurangi lagi di sini
            cursor.execute("""
                UPDATE peminjaman
                SET
                    status = 'dipinjam',
                    diproses_oleh = %s,
                    tgl_pinjam = CURDATE(),
                    jatuh_tempo = DATE_ADD(
                        CURDATE(),
                        INTERVAL %s DAY
                    )
                WHERE id_peminjaman = %s
                AND status = 'menunggu'
            """, (admin_id, lama_pinjam, id_peminjaman))

        elif aksi == 'tolak':
            cursor.execute("""
                UPDATE peminjaman
                SET
                    status = 'ditolak',
                    diproses_oleh = %s
                WHERE id_peminjaman = %s
                AND status = 'menunggu'
            """, (admin_id, id_peminjaman))

            if cursor.rowcount == 1:
                cursor.execute("""
                    UPDATE buku
                    SET jumlah_tersedia = jumlah_tersedia + 1
                    WHERE id_buku = %s
                """, (pengajuan['id_buku'],))

        else:
            conn.rollback()
            return redirect(url_for('admin_peminjaman'))

        conn.commit()

    except Exception as e:
        conn.rollback()
        print("Gagal memproses pengajuan:", e)

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('admin_peminjaman'))




@app.route('/admin/pengembalian', methods=['GET', 'POST'])
def admin_pengembalian():
    if session.get('role') == 'admin':
        conn = buat_koneksi()
        cursor = conn.cursor(dictionary=True, buffered=True)

        try:
            if request.method == 'POST':

                id_peminjaman = request.form['id_peminjaman']
                tgl_kembali = dt.datetime.strptime(
                    request.form['tgl_kembali'], '%Y-%m-%d'
                ).date()

                kondisi_buku = request.form['kondisi_buku']
                admin_id = session.get('id_user')

                # ======================================
                # 1. AMBIL DATA PEMINJAMAN
                # ======================================

                cursor.execute("""
                    SELECT *
                    FROM peminjaman
                    WHERE id_peminjaman = %s
                    AND status = 'dipinjam'
                    FOR UPDATE
                """, (id_peminjaman,))

                peminjaman = cursor.fetchone()

                if not peminjaman:
                    conn.rollback()
                    return "Transaksi tidak ditemukan atau sudah diproses.", 400

                id_buku = peminjaman['id_buku']
                jatuh_tempo = peminjaman['jatuh_tempo']

                if isinstance(jatuh_tempo, dt.datetime):
                    jatuh_tempo = jatuh_tempo.date()
                elif isinstance(jatuh_tempo, str):
                    jatuh_tempo = dt.datetime.strptime(
                        jatuh_tempo, '%Y-%m-%d'
                    ).date()

                if tgl_kembali < jatuh_tempo:
                    hari_terlambat = 0
                else:
                    hari_terlambat = max(
                        0, (tgl_kembali - jatuh_tempo).days
                    )

                # ======================================
                # 2. AMBIL PENGATURAN DENDA
                # ======================================

                cursor.execute("""
                    SELECT kunci, nilai
                    FROM pengaturan
                """)

                pengaturan_rows = cursor.fetchall()

                settings = {
                    row['kunci']: row['nilai']
                    for row in pengaturan_rows
                }

                denda_per_hari = int(
                    settings.get('denda_telat_per_hari', 2000)
                )

                denda_ringan = int(
                    settings.get('denda_rusak_ringan', 10000)
                )

                denda_berat = int(
                    settings.get('denda_rusak_berat', 25000)
                )

                # ======================================
                # 3. HITUNG DENDA KETERLAMBATAN
                # ======================================

                denda_telat = hari_terlambat * denda_per_hari

                # ======================================
                # 4. HITUNG DENDA KONDISI BUKU
                # ======================================

                if kondisi_buku == 'Baik':
                    kondisi_enum = 'baik'
                    denda_rusak = 0

                elif kondisi_buku == 'Rusak Ringan':
                    kondisi_enum = 'rusak ringan'
                    denda_rusak = denda_ringan

                elif kondisi_buku == 'Rusak Berat':
                    kondisi_enum = 'rusak berat'
                    denda_rusak = denda_berat

                elif kondisi_buku == 'Hilang':
                    kondisi_enum = 'hilang'

                    denda_rusak = float(
                        request.form.get('biaya_hilang', 0) or 0
                    )

                    if denda_rusak < 0:
                        conn.rollback()
                        return "Biaya penggantian tidak boleh negatif.", 400

                else:
                    conn.rollback()
                    return "Kondisi buku tidak valid.", 400

                # ======================================
                # 5. TENTUKAN STATUS DENDA
                # ======================================

                total_denda_final = denda_telat + denda_rusak

                status_denda = (
                    'belum_lunas'
                    if total_denda_final > 0
                    else 'tidak_ada'
                )

                # ======================================
                # 6. SIMPAN DATA PENGEMBALIAN
                # ======================================

                cursor.execute("""
                    INSERT INTO pengembalian
                    (
                        id_peminjaman,
                        tgl_kembali,
                        kondisi_buku,
                        denda_telat,
                        denda_rusak,
                        status_denda,
                        diproses_oleh
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    id_peminjaman,
                    tgl_kembali,
                    kondisi_enum,
                    denda_telat,
                    denda_rusak,
                    status_denda,
                    admin_id
                ))

                # ======================================
                # 7. UBAH STATUS PEMINJAMAN
                # ======================================

                cursor.execute("""
                    UPDATE peminjaman
                    SET status = 'dikembalikan'
                    WHERE id_peminjaman = %s
                """, (id_peminjaman,))

                # ======================================
                # 8. TAMBAH STOK JIKA BUKU TIDAK HILANG
                # ======================================

                if kondisi_buku != 'Hilang':
                    cursor.execute("""
                        UPDATE buku
                        SET jumlah_tersedia = jumlah_tersedia + 1
                        WHERE id_buku = %s
                    """, (id_buku,))

                # Simpan seluruh proses pengembalian
                conn.commit()

                return redirect(url_for('admin_pengembalian'))

            # ======================================
            # TAMPILKAN HALAMAN PENGEMBALIAN
            # ======================================

            cursor.execute("SELECT * FROM pengaturan")
            pengaturan_rows = cursor.fetchall()

            settings = {
                row['kunci']: row['nilai']
                for row in pengaturan_rows
            }

            cursor.execute("""
                SELECT
                    peminjaman.*,
                    anggota.nama_lengkap AS nama_anggota,
                    buku.judul
                FROM peminjaman
                JOIN anggota
                    ON peminjaman.id_anggota = anggota.id_anggota
                JOIN buku
                    ON peminjaman.id_buku = buku.id_buku
                WHERE peminjaman.status = 'dipinjam'
                ORDER BY peminjaman.id_peminjaman DESC
            """)

            peminjaman_aktif = cursor.fetchall()

            return render_template(
                'admin/pengembalian.html',
                settings=settings,
                peminjaman_aktif=peminjaman_aktif
            )

        except Exception as e:
            conn.rollback()
            print("Gagal proses pengembalian:", e)

            return (
                f"Terjadi kesalahan pada proses pengembalian: {e}",
                500
            )

        finally:
            cursor.close()
            conn.close()

    return redirect(url_for('login'))



@app.route('/admin/biodataagt')
def admin_biodataagt():
    if session.get('role') == 'admin':
        conn = buat_koneksi()
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute("""
            SELECT anggota.*, users.username
            FROM anggota
            JOIN users ON anggota.id_anggota = users.id_user
            ORDER BY anggota.id_anggota DESC
        """)
        anggota_list = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('admin/biodataagt.html', anggota_list=anggota_list)
    return redirect(url_for('login'))


@app.route('/admin/tambah_anggota', methods=['POST'])
def tambah_anggota():
    if session.get('role') == 'admin':
        username = request.form['username'].strip()
        nama = request.form['nama'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        kelas = request.form.get('kelas', '-').strip()
        no_hp_raw = request.form.get('no_hp', '').strip()
        no_hp = no_hp_raw if no_hp_raw else None

        conn = buat_koneksi()
        cursor = conn.cursor(dictionary=True, buffered=True)
        try:
            cursor.execute(
                """INSERT INTO users (username, email, password_hash, nama, role, is_active)
                   VALUES (%s, %s, %s, %s, 'siswa', 1)""",
                (username, email, password, nama)
            )
            id_user_baru = cursor.lastrowid

            cursor.execute(
                """INSERT INTO anggota (id_anggota, nama_lengkap, kelas, email, no_hp, status_keanggotaan, tanggal_bergabung)
                   VALUES (%s, %s, %s, %s, %s, 'aktif', CURDATE())""",
                (id_user_baru, nama, kelas, email, no_hp)
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Error tambah anggota: {e}")

        cursor.close()
        conn.close()
        return redirect(url_for('admin_biodataagt'))
    return redirect(url_for('login'))


@app.route('/admin/hapus_anggota/<int:id_anggota>')
def hapus_anggota(id_anggota):
    if session.get('role') == 'admin':
        conn = buat_koneksi()
        cursor = conn.cursor(buffered=True)
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
        cursor = conn.cursor(dictionary=True, buffered=True)

        user_id = session.get('id_user')

        try:

            # ==========================================
            # 1. STATISTIK DASHBOARD
            # ==========================================

            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM peminjaman
                WHERE id_anggota = %s
                AND status = 'dipinjam'
            """, (user_id,))

            res1 = cursor.fetchone()
            jml_dipinjam = res1['total'] if res1 else 0


            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM peminjaman
                WHERE id_anggota = %s
                AND status = 'menunggu'
            """, (user_id,))

            res2 = cursor.fetchone()
            jml_menunggu = res2['total'] if res2 else 0


# ==========================================
# TOTAL DENDA YANG BELUM LUNAS
# ==========================================

            cursor.execute("""
        SELECT
        COALESCE(SUM(
            COALESCE(pg.denda_telat, 0) +
            COALESCE(pg.denda_rusak, 0)
        ), 0) AS total_denda
    FROM pengembalian pg
    INNER JOIN peminjaman p
        ON pg.id_peminjaman = p.id_peminjaman
    WHERE p.id_anggota = %s
    AND pg.status_denda = 'belum_lunas'
""", (user_id,))

            hasil_denda = cursor.fetchone()
            total_denda = hasil_denda['total_denda'] if hasil_denda else 0

            # ==========================================
            # 2. BUKU TERBANYAK DIPINJAM
            # ==========================================
            cursor.execute("""
                SELECT
                    b.id_buku,
                    b.judul,
                    b.penulis,
                    b.cover,
                    b.created_at,
                    COUNT(p.id_peminjaman) AS jumlah_peminjaman
                FROM buku b
                LEFT JOIN peminjaman p
                    ON b.id_buku = p.id_buku
                    AND p.status IN ('dipinjam', 'dikembalikan')
                GROUP BY
                    b.id_buku,
                    b.judul,
                    b.penulis,
                    b.cover,
                    b.created_at
                HAVING jumlah_peminjaman > 0
                ORDER BY jumlah_peminjaman DESC, b.judul ASC
                LIMIT 5
            """)

            buku_terbanyak = cursor.fetchall()


            # ==========================================
            # 3. BUKU SEDANG TREND
            #    30 HARI TERAKHIR
            # ==========================================
            cursor.execute("""
                SELECT
                    b.id_buku,
                    b.judul,
                    b.penulis,
                    b.cover,
                    b.created_at,
                    COUNT(p.id_peminjaman) AS jumlah_peminjaman
                FROM buku b
                INNER JOIN peminjaman p
                    ON b.id_buku = p.id_buku
                WHERE
                    p.status IN ('dipinjam', 'dikembalikan')
                    AND p.created_at >= NOW() - INTERVAL 30 DAY
                GROUP BY
                    b.id_buku,
                    b.judul,
                    b.penulis,
                    b.cover,
                    b.created_at
                ORDER BY jumlah_peminjaman DESC, p.created_at DESC
                LIMIT 5
            """)

            buku_tren = cursor.fetchall()


            # ==========================================
            # 4. PALING SERING SAYA PINJAM
            # ==========================================
            cursor.execute("""
                SELECT
                    b.id_buku,
                    b.judul,
                    b.penulis,
                    b.cover,
                    b.created_at,
                    COUNT(p.id_peminjaman) AS jumlah_peminjaman
                FROM buku b
                INNER JOIN peminjaman p
                    ON b.id_buku = p.id_buku
                WHERE
                    p.id_anggota = %s
                    AND p.status IN ('dipinjam', 'dikembalikan')
                GROUP BY
                    b.id_buku,
                    b.judul,
                    b.penulis,
                    b.cover,
                    b.created_at
                ORDER BY jumlah_peminjaman DESC, b.judul ASC
                LIMIT 5
            """, (user_id,))

            buku_favorit = cursor.fetchall()


            # ==========================================
            # 5. BUKU TERBARU
            # ==========================================
            cursor.execute("""
                SELECT
                    b.id_buku,
                    b.judul,
                    b.penulis,
                    b.cover,
                    b.created_at
                FROM buku b
                ORDER BY b.created_at DESC
                LIMIT 5
            """)

            buku_terbaru = cursor.fetchall()


            # ==========================================
            # RENDER DASHBOARD
            # ==========================================
            return render_template(
    'user/dashboard.html',

    jml_dipinjam=jml_dipinjam,
    jml_menunggu=jml_menunggu,
    total_denda=total_denda,

    buku_terbanyak=buku_terbanyak,
    buku_tren=buku_tren,
    buku_favorit=buku_favorit,
    buku_terbaru=buku_terbaru
)
        except Exception as e:

            print("Gagal mengambil data dashboard:", e)

            return render_template(
    'user/dashboard.html',
    jml_dipinjam=jml_dipinjam,
    jml_menunggu=jml_menunggu,
    total_denda=0,
    buku_terbanyak=[],
    buku_tren=[],
    buku_favorit=[],
    buku_terbaru=[]
)

        finally:

            cursor.close()
            conn.close()

    return redirect(url_for('login'))




@app.route('/user/laporan', methods=['GET', 'POST'])
def user_laporan():
    if session.get('role') not in ['siswa', 'user']:
        return redirect(url_for('login'))

    if request.method == 'POST':
        user_id = session.get('id_user')
        jenis = request.form.get('jenis', '').strip()
        judul = request.form.get('judul', '').strip()
        isi_laporan = request.form.get('isi_laporan', '').strip()

        # Validasi input
        if jenis not in ['bug', 'saran'] or not judul or not isi_laporan:
            return redirect(url_for('user_laporan', status='tidak_valid'))

        if len(judul) > 150:
            return redirect(url_for('user_laporan', status='judul_panjang'))

        # Persiapan foto
        foto = request.files.get('foto')
        foto_path = None
        lokasi_file = None

        if foto and foto.filename:
            ekstensi = os.path.splitext(foto.filename)[1].lower()
            ekstensi_diizinkan = ['.jpg', '.jpeg', '.png', '.webp']

            if ekstensi not in ekstensi_diizinkan:
                return redirect(url_for('user_laporan', status='format_foto'))

            nama_file = f"{uuid.uuid4().hex}{ekstensi}"

            lokasi_file = os.path.join(
                app.config['LAPORAN_UPLOAD_FOLDER'],
                nama_file
            )

            foto_path = f"uploads/laporan/{nama_file}"

        conn = None
        cursor = None

        try:
            # Simpan foto jika ada
            if lokasi_file:
                foto.save(lokasi_file)

            conn = buat_koneksi()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO laporan_masukan
                    (id_user, jenis, judul, isi_laporan, foto)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                user_id,
                jenis,
                judul,
                isi_laporan,
                foto_path
            ))

            conn.commit()

            return redirect(url_for(
                'user_laporan',
                status='berhasil'
            ))

        except Exception as e:
            if conn:
                conn.rollback()

            # Hapus foto jika penyimpanan laporan gagal
            if lokasi_file and os.path.exists(lokasi_file):
                os.remove(lokasi_file)

            print("Gagal mengirim laporan:", e)

            return redirect(url_for(
                'user_laporan',
                status='gagal'
            ))

        finally:
            if cursor:
                cursor.close()

            if conn:
                conn.close()

    # Biodata sudah disediakan oleh inject_biodata()
    return render_template('user/laporan.html')



@app.route('/user/databuku')
def user_databuku():
    if session.get('role') in ['siswa', 'user']:
        conn = buat_koneksi()
        cursor = conn.cursor(dictionary=True, buffered=True)

        user_id = session.get('id_user')

        cursor.execute("""
            SELECT
                buku.*,
                kategori.nama_kategori AS kategori,

                (
                    SELECT COUNT(DISTINCT p.id_anggota)
                    FROM peminjaman p
                    WHERE p.id_buku = buku.id_buku
                    AND p.status IN ('dipinjam', 'dikembalikan')
                ) AS total_pernah_dipinjam,

                (
                    SELECT COUNT(DISTINCT p.id_anggota)
                    FROM peminjaman p
                    WHERE p.id_buku = buku.id_buku
                    AND p.status = 'dipinjam'
                ) AS sedang_dipinjam

            FROM buku

            LEFT JOIN kategori
            ON buku.id_kategori = kategori.id_kategori

            ORDER BY buku.id_buku DESC
        """)

        buku_list = cursor.fetchall()

        cursor.execute("""
            SELECT id_buku, status
            FROM peminjaman
            WHERE id_anggota = %s
            AND status IN ('menunggu', 'dipinjam')
        """, (user_id,))

        pengajuan = cursor.fetchall()

        status_peminjaman = {
            item['id_buku']: item['status']
            for item in pengajuan
        }

        cursor.close()
        conn.close()

        return render_template(
            'user/Databuku.html',
            buku_list=buku_list,
            status_peminjaman=status_peminjaman
        )

    return redirect(url_for('login'))




@app.route('/user/ajukan_peminjaman', methods=['POST'])
def user_ajukan_peminjaman():

    if session.get('role') not in ['siswa', 'user']:
        return redirect(url_for('login'))

    user_id = session.get('id_user')
    id_buku = request.form.get('id_buku')

    if not id_buku:
        return redirect(url_for('user_databuku'))

    conn = buat_koneksi()
    cursor = conn.cursor(dictionary=True, buffered=True)

    try:
        # Kunci data anggota.
        cursor.execute("""
            SELECT id_anggota
            FROM anggota
            WHERE id_anggota = %s
            FOR UPDATE
        """, (user_id,))

        anggota = cursor.fetchone()

        if not anggota:
            conn.rollback()
            return redirect(url_for(
                'user_databuku',
                pinjam='gagal'
            ))

        # Bebaskan kuota untuk pengajuan yang kedaluwarsa.
        proses_pengajuan_kedaluwarsa(cursor)

        # Hitung kuota yang sedang digunakan.
        jumlah_aktif = hitung_kuota_terpakai(
            cursor, user_id
        )

        if jumlah_aktif >= BATAS_PEMINJAMAN:
            conn.rollback()
            return redirect(url_for(
                'user_databuku',
                pinjam='kuota_penuh'
            ))

        # Periksa stok buku.
        cursor.execute("""
            SELECT jumlah_tersedia
            FROM buku
            WHERE id_buku = %s
            FOR UPDATE
        """, (id_buku,))

        buku = cursor.fetchone()

        if not buku or buku['jumlah_tersedia'] <= 0:
            conn.rollback()
            return redirect(url_for(
                'user_databuku',
                pinjam='stok_habis'
            ))

        # Cegah peminjaman buku yang sama secara bersamaan.
        cursor.execute("""
            SELECT id_peminjaman
            FROM peminjaman
            WHERE id_anggota = %s
            AND id_buku = %s
            AND status IN ('menunggu', 'dipinjam')
            LIMIT 1
        """, (user_id, id_buku))

        if cursor.fetchone():
            conn.rollback()
            return redirect(url_for(
                'user_databuku',
                pinjam='duplikat'
            ))

        # Kurangi stok saat permintaan dibuat.
        cursor.execute("""
            UPDATE buku
            SET jumlah_tersedia = jumlah_tersedia - 1
            WHERE id_buku = %s
            AND jumlah_tersedia > 0
        """, (id_buku,))

        if cursor.rowcount != 1:
            conn.rollback()
            return redirect(url_for(
                'user_databuku',
                pinjam='stok_habis'
            ))

        # Masukkan permintaan peminjaman.
        cursor.execute("""
            INSERT INTO peminjaman (
                id_anggota,
                id_buku,
                tgl_pinjam,
                jatuh_tempo,
                status,
                diproses_oleh
            )
            VALUES (%s, %s, NULL, NULL, 'menunggu', NULL)
        """, (user_id, id_buku))

        conn.commit()

        return redirect(url_for(
            'user_peminjaman',
            pinjam='berhasil'
        ))

    except Exception as e:
        conn.rollback()
        print("Gagal mengajukan peminjaman:", e)

        return redirect(url_for(
            'user_databuku',
            pinjam='gagal'
        ))

    finally:
        cursor.close()
        conn.close()



@app.route('/user/batal_peminjaman/<int:id_peminjaman>', methods=['POST'])
def user_batal_peminjaman(id_peminjaman):
    if session.get('role') not in ['siswa', 'user']:
        return redirect(url_for('login'))

    user_id = session.get('id_user')

    conn = buat_koneksi()
    cursor = conn.cursor(dictionary=True, buffered=True)

    try:
        cursor.execute("""
            SELECT id_peminjaman, id_buku, status
            FROM peminjaman
            WHERE id_peminjaman = %s
            AND id_anggota = %s
            FOR UPDATE
        """, (id_peminjaman, user_id))

        pengajuan = cursor.fetchone()

        if not pengajuan or pengajuan['status'] != 'menunggu':
            conn.rollback()
            return redirect(url_for('user_peminjaman'))

        # Pastikan pengajuan belum melewati batas 24 jam
        cursor.execute("""
            SELECT created_at <= DATE_SUB(
                NOW(), INTERVAL 24 HOUR
            ) AS sudah_kedaluwarsa
            FROM peminjaman
            WHERE id_peminjaman = %s
        """, (id_peminjaman,))

        waktu = cursor.fetchone()

        if waktu and waktu['sudah_kedaluwarsa']:
            proses_pengajuan_kedaluwarsa(cursor)
            conn.commit()
            return redirect(url_for('user_peminjaman'))

        cursor.execute("""
            UPDATE peminjaman
            SET status = 'dibatalkan'
            WHERE id_peminjaman = %s
            AND id_anggota = %s
            AND status = 'menunggu'
        """, (id_peminjaman, user_id))

        if cursor.rowcount == 1:
            cursor.execute("""
                UPDATE buku
                SET jumlah_tersedia = jumlah_tersedia + 1
                WHERE id_buku = %s
            """, (pengajuan['id_buku'],))

        conn.commit()

    except Exception as e:
        conn.rollback()
        print("Gagal membatalkan peminjaman:", e)

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('user_peminjaman'))



def proses_pengajuan_kedaluwarsa(cursor):
    """
    Membatalkan pengajuan yang sudah menunggu selama 24 jam.
    Stok dikembalikan hanya jika status berhasil diubah.
    """

    cursor.execute("""
        SELECT id_peminjaman, id_buku
        FROM peminjaman
        WHERE status = 'menunggu'
        AND created_at <= DATE_SUB(NOW(), INTERVAL 24 HOUR)
        FOR UPDATE
    """)

    daftar_kedaluwarsa = cursor.fetchall()

    for item in daftar_kedaluwarsa:
        cursor.execute("""
            UPDATE peminjaman
            SET status = 'kedaluwarsa'
            WHERE id_peminjaman = %s
            AND status = 'menunggu'
        """, (item['id_peminjaman'],))

        if cursor.rowcount == 1:
            cursor.execute("""
                UPDATE buku
                SET jumlah_tersedia = jumlah_tersedia + 1
                WHERE id_buku = %s
            """, (item['id_buku'],))




@app.route('/user/peminjaman')
def user_peminjaman():
    if session.get('role') in ['siswa', 'user']:

        conn = buat_koneksi()
        cursor = conn.cursor(dictionary=True, buffered=True)

        user_id = session.get('id_user')

        try:
            # Jalankan pemeriksaan pengajuan kedaluwarsa
            proses_pengajuan_kedaluwarsa(cursor)
            conn.commit()

            # Ambil daftar peminjaman beserta detail buku
            cursor.execute("""
                SELECT
                    peminjaman.*,
                    buku.judul,
                    buku.penulis,
                    buku.cover,
                    buku.penerbit,
                    buku.tahun_terbit,
                    buku.jumlah_total,
                    buku.jumlah_tersedia,
                    kategori.nama_kategori AS kategori,

                    UNIX_TIMESTAMP(
                        DATE_ADD(
                            peminjaman.created_at,
                            INTERVAL 24 HOUR
                        )
                    ) AS batas_persetujuan_ts

                FROM peminjaman

                JOIN buku
                    ON peminjaman.id_buku = buku.id_buku

                LEFT JOIN kategori
                    ON buku.id_kategori = kategori.id_kategori

                WHERE peminjaman.id_anggota = %s

                AND peminjaman.status IN (
                    'menunggu',
                    'dipinjam'
                )

                ORDER BY peminjaman.id_peminjaman DESC

            """, (user_id,))

            peminjaman_list = cursor.fetchall()

            return render_template(
                'user/peminjaman.html',
                peminjaman_list=peminjaman_list
            )

        except Exception as e:
            conn.rollback()
            print("Gagal memuat peminjaman:", e)

            return "Gagal memuat data peminjaman.", 500

        finally:
            cursor.close()
            conn.close()

    return redirect(url_for('login'))





@app.route('/user/riwayat')
def user_riwayat():
    if session.get('role') in ['siswa', 'user']:
        conn = buat_koneksi()
        cursor = conn.cursor(dictionary=True, buffered=True)

        try:
            user_id = session.get('id_user')

            cursor.execute("""
                SELECT
                    peminjaman.id_peminjaman,
                    peminjaman.id_anggota,
                    peminjaman.status,
                    peminjaman.created_at,
                    peminjaman.tgl_pinjam,
                    peminjaman.jatuh_tempo,

                    buku.judul,
                    buku.penulis,
                    buku.cover,

                    COALESCE(
                        pengembalian.tgl_kembali,
                        NULL
                    ) AS tgl_kembali,

                    CASE
                        WHEN peminjaman.status = 'dipinjam'
                             AND peminjaman.jatuh_tempo IS NOT NULL
                             AND peminjaman.jatuh_tempo < CURDATE()
                        THEN 'terlambat'

                        ELSE peminjaman.status
                    END AS status_tampilan

                FROM peminjaman

                JOIN buku
                    ON peminjaman.id_buku = buku.id_buku

                LEFT JOIN pengembalian
                    ON peminjaman.id_peminjaman =
                       pengembalian.id_peminjaman

                WHERE peminjaman.id_anggota = %s

                ORDER BY peminjaman.id_peminjaman DESC
            """, (user_id,))

            riwayat_list = cursor.fetchall()

            return render_template(
                'user/riwayat.html',
                riwayat_list=riwayat_list
            )

        except Exception as e:
            print("Gagal memuat riwayat peminjaman:", e)
            return "Gagal memuat riwayat peminjaman.", 500

        finally:
            cursor.close()
            conn.close()

    return redirect(url_for('login'))




@app.route('/user/biodata')
def user_biodata():
    if session.get('role') in ['siswa', 'user']:

        conn = buat_koneksi()
        cursor = conn.cursor(dictionary=True, buffered=True)
        user_id = session.get('id_user')

        try:
            # =================================
            # 1. MENGAMBIL DATA BIODATA ANGGOTA
            # =================================
            cursor.execute("""
                SELECT *
                FROM anggota
                WHERE id_anggota = %s
            """, (user_id,))

            biodata = cursor.fetchone()

            if not biodata:
                biodata = {
                    'nama_lengkap': session.get('nama', '-'),
                    'email': '-',
                    'no_hp': '-',
                    'status_keanggotaan': 'aktif',
                    'tanggal_bergabung': '-',
                    'masa_berlaku': '-',
                    'kelas': '-'
                }

            # =================================
            # 2. MENGHITUNG STATISTIK PEMINJAMAN
            # =================================
            cursor.execute("""
                SELECT
                    COUNT(
                        CASE
                            WHEN status IN ('dipinjam', 'dikembalikan')
                            THEN 1
                        END
                    ) AS total_peminjaman,

                    COUNT(
                        CASE
                            WHEN status = 'dipinjam'
                            THEN 1
                        END
                    ) AS sedang_dipinjam,

                    COUNT(
                        CASE
                            WHEN status = 'dikembalikan'
                            THEN 1
                        END
                    ) AS total_dikembalikan,

                    COUNT(
                        CASE
                            WHEN status = 'dipinjam'
                            AND jatuh_tempo IS NOT NULL
                            AND jatuh_tempo < CURDATE()
                            THEN 1
                        END
                    ) AS peminjaman_terlambat

                FROM peminjaman
                WHERE id_anggota = %s
            """, (user_id,))

            statistik = cursor.fetchone()

            # Jika hasil statistik kosong, gunakan nilai 0
            if not statistik:
                statistik = {
                    'total_peminjaman': 0,
                    'sedang_dipinjam': 0,
                    'total_dikembalikan': 0,
                    'peminjaman_terlambat': 0
                }

            return render_template(
                'user/biodata.html',
                biodata=biodata,
                statistik=statistik
            )

        except Exception as e:
            print("Gagal memuat biodata dan statistik:", e)
            return "Gagal memuat biodata dan statistik.", 500

        finally:
            cursor.close()
            conn.close()

    return redirect(url_for('login'))





@app.route('/user/update_biodata', methods=['POST'])
def user_update_biodata():

    if session.get('role') not in ['siswa', 'user']:
        return redirect(url_for('login'))

    user_id = session.get('id_user')

    nama = request.form.get('nama', '').strip()
    kelas = request.form.get('kelas', '').strip()
    email = request.form.get('email', '').strip()
    telepon_raw = request.form.get('telepon', '').strip()

    no_hp = telepon_raw if telepon_raw else None

    # Tujuan kembali ke halaman sebelumnya
    next_url = request.form.get('next', '')

    if not next_url.startswith('/user/') or next_url.startswith('//'):
        next_url = url_for('user_biodata')

    # Validasi data
    if not nama or not kelas or not email:
        return redirect(next_url)

    if len(nama) > 100 or len(kelas) > 50:
        return redirect(next_url)

    if len(email) > 100 or (no_hp and len(no_hp) > 20):
        return redirect(next_url)

    conn = None
    cursor = None

    try:
        conn = buat_koneksi()
        cursor = conn.cursor(buffered=True)

        # Update tabel anggota
        cursor.execute("""
            UPDATE anggota
            SET
                nama_lengkap = %s,
                kelas = %s,
                email = %s,
                no_hp = %s
            WHERE id_anggota = %s
        """, (nama, kelas, email, no_hp, user_id))

        # Sinkronisasi nama dan email tabel users
        cursor.execute("""
            UPDATE users
            SET
                nama = %s,
                email = %s
            WHERE id_user = %s
        """, (nama, email, user_id))

        conn.commit()

        # Perbarui session
        session['nama'] = nama
        session['kelas'] = kelas

        print("Biodata anggota berhasil diperbarui.")

    except Exception as e:

        if conn:
            conn.rollback()

        print("Gagal memperbarui biodata:", e)

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

    return redirect(next_url)



@app.route('/user/pembayaran')
def user_pembayaran():
    if session.get('role') in ['siswa', 'user']:

        conn = buat_koneksi()
        cursor = conn.cursor(dictionary=True, buffered=True)

        user_id = session.get('id_user')

        try:
            # ======================================
            # 1. AMBIL DAFTAR DENDA BELUM LUNAS
            # ======================================

            cursor.execute("""
                SELECT
                    pg.id_pengembalian,
                    p.id_peminjaman,
                    b.judul,
                    pg.tgl_kembali,
                    pg.kondisi_buku,
                    pg.denda_telat,
                    pg.denda_rusak,
                    (
                        COALESCE(pg.denda_telat, 0) +
                        COALESCE(pg.denda_rusak, 0)
                    ) AS total_denda
                FROM pengembalian pg
                JOIN peminjaman p
                    ON pg.id_peminjaman = p.id_peminjaman
                JOIN buku b
                    ON p.id_buku = b.id_buku
                WHERE p.id_anggota = %s
                AND pg.status_denda = 'belum_lunas'
                ORDER BY pg.tgl_kembali DESC
            """, (user_id,))

            daftar_denda = cursor.fetchall()

            total_denda = sum(
                float(item['total_denda'] or 0)
                for item in daftar_denda
            )

            # ======================================
            # 2. AMBIL RIWAYAT TRANSAKSI
            # ======================================

            cursor.execute("""
                SELECT *
                FROM pembayaran_denda
                WHERE id_anggota = %s
                ORDER BY created_at DESC
            """, (user_id,))

            riwayat_pembayaran = cursor.fetchall()

            return render_template(
                'user/pembayaran.html',
                daftar_denda=daftar_denda,
                total_denda=total_denda,
                riwayat_pembayaran=riwayat_pembayaran
            )

        except Exception as e:
            conn.rollback()
            print("Gagal memuat pembayaran:", e)
            return "Gagal memuat halaman pembayaran.", 500

        finally:
            cursor.close()
            conn.close()

    return redirect(url_for('login'))



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)