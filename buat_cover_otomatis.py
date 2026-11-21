
import os
import math
import mysql.connector

from PIL import Image, ImageDraw, ImageFont
from koneksi import buat_koneksi


# ==========================================
# PENGATURAN COVER
# ==========================================

LEBAR = 600
TINGGI = 900

FOLDER_COVER = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "static",
    "uploads",
    "covers"
)

os.makedirs(FOLDER_COVER, exist_ok=True)


# Palet warna berdasarkan kategori
PALET_WARNA = {
    "sejarah": ("#243B53", "#D6A85F"),
    "fiksi": ("#42275A", "#E8A87C"),
    "novel": ("#42275A", "#E8A87C"),
    "manajemen": ("#123C69", "#F4B942"),
    "teknologi": ("#102A43", "#35C6D6"),
    "ilmu pengetahuan": ("#174A3A", "#A8D5A2"),
    "pendidikan": ("#34495E", "#F1C75B"),
    "default": ("#26364A", "#7EC8E3")
}


# ==========================================
# FONT
# ==========================================

def ambil_font(ukuran, tebal=False):
    folder_font = r"C:\Windows\Fonts"

    if tebal:
        pilihan = [
            os.path.join(folder_font, "arialbd.ttf"),
            os.path.join(folder_font, "calibrib.ttf")
        ]
    else:
        pilihan = [
            os.path.join(folder_font, "arial.ttf"),
            os.path.join(folder_font, "calibri.ttf")
        ]

    for path in pilihan:
        if os.path.exists(path):
            return ImageFont.truetype(path, ukuran)

    return ImageFont.load_default()


# ==========================================
# MEMBUNGKUS JUDUL AGAR TIDAK KELUAR COVER
# ==========================================

def bungkus_teks(teks, font, draw, lebar_maks):
    kata = str(teks).split()
    baris = []
    baris_sekarang = ""

    for item in kata:
        percobaan = (
            item if not baris_sekarang
            else baris_sekarang + " " + item
        )

        ukuran = draw.textbbox(
            (0, 0), percobaan, font=font
        )

        if ukuran[2] <= lebar_maks:
            baris_sekarang = percobaan
        else:
            if baris_sekarang:
                baris.append(baris_sekarang)
            baris_sekarang = item

    if baris_sekarang:
        baris.append(baris_sekarang)

    return baris


# ==========================================
# MEMBUAT DESAIN COVER
# ==========================================

def buat_gambar_cover(buku):

    judul = str(buku["judul"])
    penulis = str(buku["penulis"])
    kategori = str(buku["nama_kategori"])
    tahun = str(buku["tahun_terbit"])

    warna = PALET_WARNA.get(
        kategori.lower(),
        PALET_WARNA["default"]
    )

    warna_dasar = warna[0]
    warna_aksen = warna[1]

    # Background gradasi
    gambar = Image.new(
        "RGB",
        (LEBAR, TINGGI),
        warna_dasar
    )

    draw = ImageDraw.Draw(gambar)

    warna_atas = tuple(
        int(warna_dasar[i:i+2], 16)
        for i in (1, 3, 5)
    )

    warna_bawah = tuple(
        max(0, nilai - 25)
        for nilai in warna_atas
    )

    for y in range(TINGGI):
        rasio = y / TINGGI

        warna_gradasi = tuple(
            int(
                warna_atas[i] * (1 - rasio)
                + warna_bawah[i] * rasio
            )
            for i in range(3)
        )

        draw.line(
            (0, y, LEBAR, y),
            fill=warna_gradasi
        )

    # Ornamen geometris
    draw.ellipse(
        (350, -120, 750, 280),
        outline=warna_aksen,
        width=5
    )

    draw.ellipse(
        (390, -80, 700, 230),
        outline=warna_aksen,
        width=2
    )

    draw.arc(
        (30, 260, 570, 800),
        start=190,
        end=345,
        fill=warna_aksen,
        width=4
    )

    draw.polygon(
        [(0, 650), (250, 450), (600, 700), (600, 900), (0, 900)],
        fill=warna_dasar
    )

    # Garis dekoratif
    for x in range(55, 550, 35):
        draw.line(
            (x, 250, x + 80, 170),
            fill=warna_aksen,
            width=1
        )

    # Nama perpustakaan
    font_logo = ambil_font(25, True)

    draw.text(
        (55, 55),
        "FREX LIBRARY",
        font=font_logo,
        fill="white"
    )

    draw.line(
        (55, 100, 545, 100),
        fill=warna_aksen,
        width=3
    )

    # Label kategori
    font_kategori = ambil_font(20, True)

    draw.rounded_rectangle(
        (55, 145, 330, 190),
        radius=18,
        fill=warna_aksen
    )

    draw.text(
        (72, 154),
        kategori.upper(),
        font=font_kategori,
        fill=warna_dasar
    )

    # Judul buku
    ukuran_judul = 64

    while ukuran_judul > 35:
        font_judul = ambil_font(
            ukuran_judul, True
        )

        baris = bungkus_teks(
            judul,
            font_judul,
            draw,
            480
        )

        if len(baris) <= 4:
            break

        ukuran_judul -= 4

    posisi_y = 330

    for baris_judul in baris:
        draw.text(
            (55, posisi_y),
            baris_judul,
            font=font_judul,
            fill="white"
        )

        posisi_y += ukuran_judul + 15

    # Garis pemisah
    draw.line(
        (55, 700, 545, 700),
        fill=warna_aksen,
        width=4
    )

    # Nama penulis
    font_penulis = ambil_font(25)

    draw.text(
        (55, 730),
        "PENULIS",
        font=ambil_font(17, True),
        fill=warna_aksen
    )

    draw.text(
        (55, 765),
        penulis[:55],
        font=font_penulis,
        fill="white"
    )

    # Tahun terbit
    draw.text(
        (55, 830),
        "TAHUN TERBIT  |  " + tahun,
        font=ambil_font(20, True),
        fill=warna_aksen
    )

    # Bingkai luar
    draw.rectangle(
        (15, 15, LEBAR - 15, TINGGI - 15),
        outline=warna_aksen,
        width=3
    )

    return gambar


# ==========================================
# PROSES SELURUH BUKU DARI MYSQL
# ==========================================

def proses_semua_cover():

    conn = None
    cursor = None

    try:
        conn = buat_koneksi()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                buku.id_buku,
                buku.judul,
                buku.penulis,
                buku.tahun_terbit,
                kategori.nama_kategori
            FROM buku
            INNER JOIN kategori
                ON buku.id_kategori = kategori.id_kategori
            ORDER BY buku.id_buku
        """)

        daftar_buku = cursor.fetchall()

        if not daftar_buku:
            print("Tidak ada data buku.")
            return

        berhasil = 0

        for buku in daftar_buku:

            id_buku = buku["id_buku"]

            nama_file = f"frex_cover_{id_buku}.jpg"

            lokasi_file = os.path.join(
                FOLDER_COVER,
                nama_file
            )

            gambar = buat_gambar_cover(buku)

            gambar.save(
                lokasi_file,
                format="JPEG",
                quality=95
            )

            cursor.execute("""
                UPDATE buku
                SET cover = %s
                WHERE id_buku = %s
            """, (nama_file, id_buku))

            berhasil += 1

            print(
                f"[BERHASIL] {buku['judul']} "
                f"-> {nama_file}"
            )

        conn.commit()

        print("\n================================")
        print("PEMBUATAN COVER SELESAI")
        print(f"Total cover dibuat: {berhasil}")
        print(f"Lokasi: {FOLDER_COVER}")
        print("================================")

    except Exception as error:
        if conn:
            conn.rollback()

        print("\nTerjadi kesalahan:")
        print(error)

    finally:
        if cursor:
            cursor.close()

        if conn and conn.is_connected():
            conn.close()


if __name__ == "__main__":
    proses_semua_cover()
