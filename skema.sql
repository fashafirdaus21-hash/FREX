
-- ==========================================
-- DATABASE PERPUSTAKAAN FREX
-- Versi lengkap untuk sinkronisasi tim
-- ==========================================

DROP DATABASE IF EXISTS db_perpustakaan;

CREATE DATABASE db_perpustakaan
CHARACTER SET utf8mb4
COLLATE utf8mb4_general_ci;

USE db_perpustakaan;

-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Waktu pembuatan: 20 Nov 2026 pada 14.15
-- Versi server: 10.4.32-MariaDB
-- Versi PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `db_perpustakaan`
--

-- --------------------------------------------------------

--
-- Struktur dari tabel `anggota`
--

CREATE TABLE `anggota` (
  `id_anggota` int(11) NOT NULL,
  `nama_lengkap` varchar(100) DEFAULT NULL,
  `kelas` varchar(50) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `no_hp` varchar(20) DEFAULT NULL,
  `foto` varchar(255) DEFAULT NULL,
  `status_keanggotaan` enum('aktif','nonaktif','ditangguhkan') DEFAULT 'aktif',
  `tanggal_bergabung` date DEFAULT NULL,
  `masa_berlaku` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `anggota`
--

INSERT INTO `anggota` (`id_anggota`, `nama_lengkap`, `kelas`, `email`, `no_hp`, `foto`, `status_keanggotaan`, `tanggal_bergabung`, `masa_berlaku`) VALUES
(4, 'Budi Santoso', 'RS-3', 'budi@sekolah.sch.id', '081234567890', NULL, 'aktif', '2026-01-10', '2027-01-10'),
(5, 'Siti Rahma', 'RT-1', 'siti@sekolah.sch.id', '089876543210', NULL, 'aktif', '2026-01-10', '2027-01-10');

-- --------------------------------------------------------

--
-- Struktur dari tabel `buku`
--

CREATE TABLE `buku` (
  `id_buku` int(11) NOT NULL,
  `judul` varchar(255) NOT NULL,
  `cover` varchar(255) DEFAULT 'default_cover.jpg',
  `penulis` varchar(255) NOT NULL,
  `penerbit` varchar(255) DEFAULT NULL,
  `id_kategori` int(11) NOT NULL,
  `tahun_terbit` int(11) NOT NULL,
  `jumlah_total` int(11) NOT NULL,
  `jumlah_tersedia` int(11) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `buku`
--

INSERT INTO `buku` (`id_buku`, `judul`, `cover`, `penulis`, `penerbit`, `id_kategori`, `tahun_terbit`, `jumlah_total`, `jumlah_tersedia`, `created_at`) VALUES
(1, 'Fisika Dasar', 'fisika.jpg', 'Halliday & Resnick', NULL, 1, 2014, 5, 5, '2026-11-20 12:26:11'),
(2, 'Sejarah Indonesia Modern', 'sejarah.jpg', 'M.C. Ricklefs', NULL, 6, 2008, 3, 3, '2026-11-20 12:26:11'),
(3, 'Jejak Peradaban Nusantara', 'default_cover.jpg', 'Ardiansyah Putra', 'Pustaka Mandiri', 6, 2020, 5, 5, '2026-11-20 12:38:34'),
(4, 'Sejarah Indonesia Modern', 'default_cover.jpg', 'M.C. Ricklefs', 'Pustaka Sejarah', 6, 2008, 3, 3, '2026-11-20 12:38:34'),
(5, 'Catatan dari Masa Kolonial', 'default_cover.jpg', 'Rendra Mahardika', 'Lentera Ilmu', 6, 2019, 4, 4, '2026-11-20 12:38:34'),
(6, 'Kerajaan Besar Nusantara', 'default_cover.jpg', 'Dimas Pratama', 'Cakrawala Media', 6, 2021, 6, 6, '2026-11-20 12:38:34'),
(7, 'Perjalanan Bangsa Indonesia', 'default_cover.jpg', 'Fajar Nugraha', 'Pustaka Nasional', 6, 2022, 4, 4, '2026-11-20 12:38:34'),
(8, 'Senja di Kota Hujan', 'default_cover.jpg', 'Nabila Azzahra', 'Aksara Pena', 1, 2023, 5, 5, '2026-11-20 12:38:34'),
(9, 'Langit yang Berbeda', 'default_cover.jpg', 'Raka Mahendra', 'Penerbit Bintang', 1, 2021, 4, 4, '2026-11-20 12:38:34'),
(10, 'Rahasia di Balik Jendela', 'default_cover.jpg', 'Alina Putri', 'Karya Remaja', 1, 2022, 3, 3, '2026-11-20 12:38:34'),
(11, 'Rumah di Ujung Jalan', 'default_cover.jpg', 'Farhan Akbar', 'Aksara Pena', 1, 2020, 5, 5, '2026-11-20 12:38:34'),
(12, 'Sebelum Waktu Berakhir', 'default_cover.jpg', 'Nadia Permata', 'Lentera Kata', 1, 2024, 6, 6, '2026-11-20 12:38:34'),
(13, 'Dasar-Dasar Manajemen', 'default_cover.jpg', 'Andi Wijaya', 'Cendekia Press', 7, 2021, 5, 5, '2026-11-20 12:38:34'),
(14, 'Manajemen Pemasaran', 'default_cover.jpg', 'Melati', 'Edu Media', 7, 2021, 4, 4, '2026-11-20 12:38:34'),
(15, 'Strategi Bisnis Modern', 'default_cover.jpg', 'Bima Santoso', 'Pustaka Bisnis', 7, 2023, 3, 3, '2026-11-20 12:38:34'),
(16, 'Pengantar Administrasi Bisnis', 'default_cover.jpg', 'Rina Kurniawati', 'Cendekia Press', 7, 2022, 5, 5, '2026-11-20 12:38:34'),
(17, 'Kepemimpinan dan Organisasi', 'default_cover.jpg', 'Yudha Prakoso', 'Media Akademika', 7, 2020, 4, 4, '2026-11-20 12:38:34'),
(18, 'Belajar Pemrograman Python', 'default_cover.jpg', 'Aditya Firmansyah', 'Teknologi Kita', 8, 2024, 6, 6, '2026-11-20 12:38:34'),
(19, 'Dasar-Dasar Jaringan Komputer', 'default_cover.jpg', 'Rizky Ramadhan', 'Informatika Media', 8, 2022, 5, 5, '2026-11-20 12:38:34'),
(20, 'Pengantar Kecerdasan Buatan', 'default_cover.jpg', 'Bagas Wicaksono', 'Digital Press', 8, 2024, 4, 4, '2026-11-20 12:38:34'),
(21, 'Membangun Website Modern', 'default_cover.jpg', 'Deni Saputra', 'Teknologi Kita', 8, 2023, 5, 5, '2026-11-20 12:38:34'),
(22, 'Basis Data untuk Pemula', 'default_cover.jpg', 'Reza Firmansyah', 'Informatika Media', 8, 2021, 3, 3, '2026-11-20 12:38:34'),
(23, 'Fisika Dasar', 'default_cover.jpg', 'Halliday & Resnick', 'Erlangga', 9, 2014, 5, 5, '2026-11-20 12:38:34'),
(24, 'Pengantar Ilmu Matematika', 'default_cover.jpg', 'Satria Hidayat', 'Edu Media', 9, 2020, 4, 4, '2026-11-20 12:38:34'),
(25, 'Biologi Kehidupan', 'default_cover.jpg', 'Maya Lestari', 'Pustaka Sains', 9, 2022, 5, 5, '2026-11-20 12:38:34'),
(26, 'Dasar-Dasar Ekonomi', 'default_cover.jpg', 'Rudi Hartono', 'Cendekia Press', 10, 2021, 4, 4, '2026-11-20 12:38:34'),
(27, 'Metode Penelitian Kuantitatif', 'default_cover.jpg', 'Adhi Kusumastuti', 'Deepublish', 10, 2022, 3, 3, '2026-11-20 12:38:34');

-- --------------------------------------------------------

--
-- Struktur dari tabel `kategori`
--

CREATE TABLE `kategori` (
  `id_kategori` int(11) NOT NULL,
  `nama_kategori` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `kategori`
--

INSERT INTO `kategori` (`id_kategori`, `nama_kategori`) VALUES
(1, 'Fiksi'),
(9, 'Ilmu Pengetahuan'),
(4, 'Komik'),
(7, 'Manajemen'),
(2, 'Non-Fiksi'),
(5, 'Novel'),
(10, 'Pendidikan'),
(3, 'Referensi'),
(6, 'Sejarah'),
(8, 'Teknologi');

-- --------------------------------------------------------

--
-- Struktur dari tabel `peminjaman`
--


--
-- Struktur tabel peminjaman FREX
--

CREATE TABLE `peminjaman` (
  `id_peminjaman` int(11) NOT NULL,
  `id_anggota` int(11) NOT NULL,
  `id_buku` int(11) NOT NULL,

  -- Diisi setelah admin menyetujui
  `tgl_pinjam` date DEFAULT NULL,
  `jatuh_tempo` date DEFAULT NULL,

  -- Status lengkap peminjaman
  `status` enum(
    'menunggu',
    'dipinjam',
    'dikembalikan',
    'ditolak',
    'dibatalkan',
    'kedaluwarsa'
  ) DEFAULT 'menunggu',

  `diproses_oleh` int(11) DEFAULT NULL,

  -- Waktu pengajuan otomatis dicatat
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


--
-- Dumping data untuk tabel `peminjaman`
--

INSERT INTO `peminjaman` (`id_peminjaman`, `id_anggota`, `id_buku`, `tgl_pinjam`, `jatuh_tempo`, `status`, `diproses_oleh`, `created_at`) VALUES
(1, 5, 2, '2026-11-20', '2026-11-27', 'menunggu', NULL, '2026-11-20 12:31:54'),
(2, 5, 1, '2026-11-20', '2026-11-27', 'menunggu', NULL, '2026-11-20 12:34:58');

-- --------------------------------------------------------

--
-- Struktur dari tabel `pengaturan`
--

CREATE TABLE `pengaturan` (
  `kunci` varchar(50) NOT NULL,
  `nilai` varchar(255) NOT NULL,
  `keterangan` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `pengaturan`
--

INSERT INTO `pengaturan` (`kunci`, `nilai`, `keterangan`) VALUES
('denda_rusak_berat', '25000', 'Besaran denda jika buku rusak berat (Rupiah)'),
('denda_rusak_ringan', '10000', 'Besaran denda jika buku rusak ringan (Rupiah)'),
('denda_telat_per_hari', '2000', 'Besaran denda keterlambatan per hari (Rupiah)'),
('lama_pinjam_hari', '7', 'Batas waktu peminjaman buku dalam hari');

-- --------------------------------------------------------

--
-- Struktur dari tabel `pengembalian`
--

CREATE TABLE `pengembalian` (
  `id_pengembalian` int(11) NOT NULL,
  `id_peminjaman` int(11) NOT NULL,
  `tgl_kembali` date NOT NULL,
  `kondisi_buku` enum('baik','rusak ringan','rusak berat') NOT NULL,
  `denda_telat` decimal(10,2) DEFAULT 0.00,
  `denda_rusak` decimal(10,2) DEFAULT 0.00,
  `diproses_oleh` int(11) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `users`
--

CREATE TABLE `users` (
  `id_user` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `nama` varchar(100) DEFAULT NULL,
  `role` enum('siswa','admin','kepsek','programmer') NOT NULL,
  `is_active` tinyint(1) DEFAULT 1,
  `last_login` datetime DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `users`
--

INSERT INTO `users` (`id_user`, `username`, `email`, `password_hash`, `nama`, `role`, `is_active`, `last_login`, `created_at`) VALUES
(1, 'Andika0909', 'admin@sekolah.sch.id', 'Lasut9926', 'Andika', 'admin', 1, NULL, '2026-11-20 12:26:11'),
(2, 'Ajijah0909', 'ajijah@sekolah.sch.id', 'password123', 'Ajijah', 'admin', 1, NULL, '2026-11-20 12:26:11'),
(3, 'Fraxx', 'kepsek@sekolah.sch.id', 'Fasha234', 'Kepala Sekolah', 'kepsek', 1, NULL, '2026-11-20 12:26:11'),
(4, 'Budi', 'budi@sekolah.sch.id', 'budi0876', 'Budi Santoso', 'siswa', 1, NULL, '2026-11-20 12:26:11'),
(5, 'Siti', 'siti@sekolah.sch.id', 'siti085', 'Siti Rahma', 'siswa', 1, NULL, '2026-11-20 12:26:11');

--
-- Indexes for dumped tables
--

--
-- Indeks untuk tabel `anggota`
--
ALTER TABLE `anggota`
  ADD PRIMARY KEY (`id_anggota`);

--
-- Indeks untuk tabel `buku`
--
ALTER TABLE `buku`
  ADD PRIMARY KEY (`id_buku`),
  ADD KEY `fk_buku_kategori` (`id_kategori`);

--
-- Indeks untuk tabel `kategori`
--
ALTER TABLE `kategori`
  ADD PRIMARY KEY (`id_kategori`),
  ADD UNIQUE KEY `nama_kategori` (`nama_kategori`);

--
-- Indeks untuk tabel `peminjaman`
--

ALTER TABLE `peminjaman`
  ADD PRIMARY KEY (`id_peminjaman`),
  ADD KEY `fk_peminjaman_anggota` (`id_anggota`),
  ADD KEY `fk_peminjaman_buku` (`id_buku`),
  ADD KEY `fk_peminjaman_admin` (`diproses_oleh`),
  ADD KEY `idx_peminjaman_status_created` (`status`, `created_at`);


--
-- Indeks untuk tabel `pengaturan`
--
ALTER TABLE `pengaturan`
  ADD PRIMARY KEY (`kunci`);

--
-- Indeks untuk tabel `pengembalian`
--
ALTER TABLE `pengembalian`
  ADD PRIMARY KEY (`id_pengembalian`),
  ADD UNIQUE KEY `id_peminjaman` (`id_peminjaman`),
  ADD KEY `fk_pengembalian_admin` (`diproses_oleh`);

--
-- Indeks untuk tabel `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id_user`),
  ADD UNIQUE KEY `username` (`username`);


-- ==========================================
-- TABEL LAPORAN BUG DAN SARAN
-- ==========================================

CREATE TABLE `laporan_masukan` (
    `id_laporan` int(11) NOT NULL AUTO_INCREMENT,
    `id_user` int(11) NOT NULL,
    `jenis` enum('bug', 'saran') NOT NULL,
    `judul` varchar(150) NOT NULL,
    `isi_laporan` text NOT NULL,
    `status` enum('baru', 'diproses', 'selesai') NOT NULL DEFAULT 'baru',
    `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
    `updated_at` timestamp NOT NULL DEFAULT current_timestamp()
        ON UPDATE current_timestamp(),

    PRIMARY KEY (`id_laporan`),
    KEY `idx_laporan_user` (`id_user`),
    KEY `idx_laporan_status_created` (`status`, `created_at`),

    CONSTRAINT `fk_laporan_user`
        FOREIGN KEY (`id_user`)
        REFERENCES `users` (`id_user`)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_general_ci;


--
-- AUTO_INCREMENT untuk tabel yang dibuang
--

--
-- AUTO_INCREMENT untuk tabel `buku`
--
ALTER TABLE `buku`
  MODIFY `id_buku` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=34;

--
-- AUTO_INCREMENT untuk tabel `kategori`
--
ALTER TABLE `kategori`
  MODIFY `id_kategori` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT untuk tabel `peminjaman`
--
ALTER TABLE `peminjaman`
  MODIFY `id_peminjaman` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT untuk tabel `pengembalian`
--
ALTER TABLE `pengembalian`
  MODIFY `id_pengembalian` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `users`
--
ALTER TABLE `users`
  MODIFY `id_user` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- Ketidakleluasaan untuk tabel pelimpahan (Dumped Tables)
--

--
-- Ketidakleluasaan untuk tabel `anggota`
--
ALTER TABLE `anggota`
  ADD CONSTRAINT `fk_anggota_user` FOREIGN KEY (`id_anggota`) REFERENCES `users` (`id_user`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Ketidakleluasaan untuk tabel `buku`
--
ALTER TABLE `buku`
  ADD CONSTRAINT `fk_buku_kategori` FOREIGN KEY (`id_kategori`) REFERENCES `kategori` (`id_kategori`) ON UPDATE CASCADE;

--
-- Ketidakleluasaan untuk tabel `peminjaman`
--
ALTER TABLE `peminjaman`
  ADD CONSTRAINT `fk_peminjaman_admin` FOREIGN KEY (`diproses_oleh`) REFERENCES `users` (`id_user`) ON DELETE SET NULL ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_peminjaman_anggota` FOREIGN KEY (`id_anggota`) REFERENCES `anggota` (`id_anggota`) ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_peminjaman_buku` FOREIGN KEY (`id_buku`) REFERENCES `buku` (`id_buku`) ON UPDATE CASCADE;

--
-- Ketidakleluasaan untuk tabel `pengembalian`
--
ALTER TABLE `pengembalian`
  ADD CONSTRAINT `fk_pengembalian_admin` FOREIGN KEY (`diproses_oleh`) REFERENCES `users` (`id_user`) ON DELETE SET NULL ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_pengembalian_peminjaman` FOREIGN KEY (`id_peminjaman`) REFERENCES `peminjaman` (`id_peminjaman`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
