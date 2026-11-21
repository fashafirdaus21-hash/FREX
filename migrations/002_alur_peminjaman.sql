
USE db_perpustakaan;

-- Tanggal pinjam dan jatuh tempo baru diisi saat disetujui admin
ALTER TABLE peminjaman
MODIFY tgl_pinjam DATE NULL,
MODIFY jatuh_tempo DATE NULL;

-- Tambahkan status pembatalan dan kedaluwarsa
ALTER TABLE peminjaman
MODIFY status ENUM(
    'menunggu',
    'dipinjam',
    'dikembalikan',
    'ditolak',
    'dibatalkan',
    'kedaluwarsa'
) DEFAULT 'menunggu';

-- Index untuk pengecekan pengajuan kedaluwarsa
ALTER TABLE peminjaman
ADD INDEX idx_peminjaman_status_created (status, created_at);
