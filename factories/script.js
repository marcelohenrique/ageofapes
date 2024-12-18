// Abre o modal com a imagem selecionada
function openModal(imgElement) {
    const modal = document.getElementById("modal");
    const modalImage = document.getElementById("modal-image");

    modalImage.src = imgElement.src;
    modal.style.display = "flex";
}

// Fecha o modal
function closeModal() {
    const modal = document.getElementById("modal");
    modal.style.display = "none";
}
