
// ==========================================
// MODAL EDIT BIODATA GLOBAL FREX
// ==========================================

function openEditProfileModal() {

    const modalProfil = document.getElementById('waProfileModal');
    const modalEdit = document.getElementById('modalEditBiodata');

    if (modalProfil) {
        modalProfil.style.display = 'none';
    }

    if (modalEdit) {
        modalEdit.style.display = 'flex';
    }
}


// ==========================================
// TUTUP MODAL EDIT DAN KEMBALI KE PROFIL
// ==========================================

function closeEditProfileModal() {

    const modalEdit = document.getElementById('modalEditBiodata');
    const modalProfil = document.getElementById('waProfileModal');

    if (modalEdit) {
        modalEdit.style.display = 'none';
    }

    if (modalProfil) {
        modalProfil.style.display = 'flex';
    }
}
