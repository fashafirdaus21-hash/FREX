-- 1. Bersihkan database lama
DROP DATABASE IF EXISTS db_perpustakaan;
CREATE DATABASE db_perpustakaan;
USE db_perpustakaan;

-- 2. Tabel USERS
CREATE TABLE IF NOT EXISTS users (
    id_user VARCHAR(50) PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nama VARCHAR(100) NULL,
    role ENUM('siswa', 'admin', 'kepsek', 'programmer') NOT NULL,
    is_active TINYINT(1) DEFAULT 1,
    last_login DATETIME NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Tabel ANGGOTA
CREATE TABLE IF NOT EXISTS anggota (
    id_anggota VARCHAR(50) PRIMARY KEY,
    nama_lengkap VARCHAR(100) NULL,
    kelas VARCHAR(50) NULL,
    email VARCHAR(100) NULL,
    no_hp VARCHAR(20) NULL,
    foto VARCHAR(255) NULL,
    status_keanggotaan ENUM('aktif', 'nonaktif', 'ditangguhkan') DEFAULT 'aktif',
    tanggal_bergabung DATE NULL,
    masa_berlaku DATE NULL,
    CONSTRAINT fk_anggota_user FOREIGN KEY (id_anggota) REFERENCES users(id_user) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 4. Tabel KATEGORI BUKU
CREATE TABLE IF NOT EXISTS kategori (
    id_kategori INT AUTO_INCREMENT PRIMARY KEY,
    nama_kategori VARCHAR(100) UNIQUE NOT NULL
);

-- 5. Tabel BUKU
CREATE TABLE IF NOT EXISTS buku (
    id_buku INT AUTO_INCREMENT PRIMARY KEY,
    judul VARCHAR(255) NOT NULL,
    penulis VARCHAR(255) NOT NULL,
    id_kategori INT NOT NULL,
    tahun_terbit INT NOT NULL,
    jumlah_total INT NOT NULL,
    jumlah_tersedia INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_buku_kategori FOREIGN KEY (id_kategori) REFERENCES kategori(id_kategori) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- 6. Tabel PEMINJAMAN
CREATE TABLE IF NOT EXISTS peminjaman (
    id_peminjaman INT AUTO_INCREMENT PRIMARY KEY,
    id_anggota VARCHAR(50) NOT NULL,
    id_buku INT NOT NULL,
    tgl_pinjam DATE NOT NULL,
    jatuh_tempo DATE NOT NULL,
    status ENUM('menunggu', 'dipinjam', 'dikembalikan', 'ditolak') DEFAULT 'menunggu',
    diproses_oleh VARCHAR(50) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_peminjaman_anggota FOREIGN KEY (id_anggota) REFERENCES anggota(id_anggota) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_peminjaman_buku FOREIGN KEY (id_buku) REFERENCES buku(id_buku) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_peminjaman_admin FOREIGN KEY (diproses_oleh) REFERENCES users(id_user) ON DELETE SET NULL ON UPDATE CASCADE
);

-- 7. Tabel PENGEMBALIAN
CREATE TABLE IF NOT EXISTS pengembalian (
    id_pengembalian INT AUTO_INCREMENT PRIMARY KEY,
    id_peminjaman INT NOT NULL UNIQUE,
    tgl_kembali DATE NOT NULL,
    kondisi_buku ENUM('baik', 'rusak ringan', 'rusak berat') NOT NULL,
    denda_telat DECIMAL(10,2) DEFAULT 0.00,
    denda_rusak DECIMAL(10,2) DEFAULT 0.00,
    diproses_oleh VARCHAR(50) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_pengembalian_peminjaman FOREIGN KEY (id_peminjaman) REFERENCES peminjaman(id_peminjaman) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_pengembalian_admin FOREIGN KEY (diproses_oleh) REFERENCES users(id_user) ON DELETE SET NULL ON UPDATE CASCADE
);

-- 8. Tabel PENGATURAN
CREATE TABLE IF NOT EXISTS pengaturan (
    kunci VARCHAR(50) PRIMARY KEY,
    nilai VARCHAR(255) NOT NULL,
    keterangan TEXT NULL
);

-- ==========================================================
-- DATA AWAL (SEEDER)
-- ==========================================================

INSERT INTO pengaturan (kunci, nilai, keterangan) VALUES
('lama_pinjam_hari', '7', 'Batas waktu peminjaman buku dalam hari'),
('denda_telat_per_hari', '2000', 'Besaran denda keterlambatan per hari (Rupiah)'),
('denda_rusak_ringan', '10000', 'Besaran denda jika buku rusak ringan (Rupiah)'),
('denda_rusak_berat', '25000', 'Besaran denda jika buku rusak berat (Rupiah)');

INSERT INTO kategori (id_kategori, nama_kategori) VALUES
(1, 'Fiksi'),
(2, 'Non-Fiksi'),
(3, 'Referensi'),
(4, 'Komik'),
(5, 'Novel'),
(6, 'Sejarah');

INSERT INTO users (id_user, email, password_hash, nama, role, is_active) VALUES
('Andika0909', 'admin@sekolah.sch.id', 'Lasut9926', 'Admin Perpustakaan', 'admin', 1),
('KEP01', 'kepsek@sekolah.sch.id', 'hash_password_kepsek', 'Kepala Sekolah', 'kepsek', 1),
('1001', 'budi@sekolah.sch.id', 'hash_password_siswa', 'Budi Santoso', 'siswa', 1),
('1002', 'siti@sekolah.sch.id', 'hash_password_siswa', 'Siti Rahma', 'siswa', 1);

INSERT INTO anggota (id_anggota, nama_lengkap, kelas, email, no_hp, status_keanggotaan, tanggal_bergabung, masa_berlaku) VALUES
('1001', 'Budi Santoso', 'RS-3', 'budi@sekolah.sch.id', '081234567890', 'aktif', '2026-01-10', '2027-01-10'),
('1002', 'Siti Rahma', 'RT-1', 'siti@sekolah.sch.id', '089876543210', 'aktif', '2026-01-10', '2027-01-10');

INSERT INTO buku (id_buku, judul, penulis, id_kategori, tahun_terbit, jumlah_total, jumlah_tersedia) VALUES
(1, 'Fisika Dasar', 'Halliday & Resnick', 1, 2014, 5, 5),
(2, 'Sejarah Indonesia Modern', 'M.C. Ricklefs', 2, 2008, 3, 3);