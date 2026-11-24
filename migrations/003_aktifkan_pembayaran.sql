USE db_perpustakaan;

-- Tambahkan status pembayaran denda pada pengembalian
ALTER TABLE pengembalian
ADD COLUMN status_denda ENUM(
    'belum_lunas',
    'menunggu',
    'lunas',
    'ditolak'
) NOT NULL DEFAULT 'belum_lunas'
AFTER denda_rusak;


-- Buat tabel pembayaran denda
CREATE TABLE pembayaran_denda (
    id_pembayaran INT(11) NOT NULL AUTO_INCREMENT,
    id_anggota INT(11) NOT NULL,
    id_pengembalian INT(11) NOT NULL,
    jumlah_bayar DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    metode_pembayaran ENUM(
        'tunai',
        'qris'
    ) NOT NULL,
    status_pembayaran ENUM(
        'menunggu',
        'berhasil',
        'ditolak'
    ) NOT NULL DEFAULT 'menunggu',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_pembayaran),

    CONSTRAINT fk_pembayaran_anggota
        FOREIGN KEY (id_anggota)
        REFERENCES anggota(id_anggota)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_pembayaran_pengembalian
        FOREIGN KEY (id_pengembalian)
        REFERENCES pengembalian(id_pengembalian)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);