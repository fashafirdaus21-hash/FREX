
-- MIGRASI ALUR PEMINJAMAN FREX
-- Jalankan satu kali pada database db_perpustakaan.

ALTER TABLE peminjaman
MODIFY COLUMN status ENUM(
    'menunggu',
    'dipinjam',
    'dikembalikan',
    'ditolak',
    'dibatalkan',
    'kedaluwarsa'
) DEFAULT 'menunggu';
