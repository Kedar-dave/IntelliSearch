// Function to show modal message with specified type
function showModal(type, title, message) {
    const modal = document.getElementById('modal');
    const modalIcon = document.getElementById('modal-icon');
    const modalTitle = document.getElementById('modal-headline');
    const modalMessage = document.getElementById('modal-message');
    const closebutton = document.getElementById('modal-close')
    const modalBorder = document.getElementById('modalBorder');
    modalTitle.textContent = title;
    modalMessage.textContent = message;
    // Set icon based on type
    if (type === 'success') {
        modalBorder.classList.add('border-green-700')
        closebutton.classList.add('bg-green-600', 'hover:bg-green-700');
        modalIcon.classList.add('border-green-600');
        modalIcon.innerHTML = `<svg class="h-12 w-12 text-green-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>`;
    } else if (type === 'warning') {
        modalBorder.classList.add('border-yellow-700')

        closebutton.classList.add('bg-yellow-600', 'hover:bg-yellow-700');
        modalIcon.classList.add('border-yellow-600');
        modalIcon.innerHTML = `<svg class="h-12 w-12 text-yellow-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>`;
    } else if (type === 'error') {
        modalBorder.classList.add('border-red-700')
        closebutton.classList.add('bg-red-600', 'hover:bg-red-700');
        modalIcon.classList.add('border-red-600');
        modalIcon.innerHTML = `<svg class="h-12 w-12 text-red-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>`;
    }

    modal.classList.remove('hidden');
}

function closeModal() {
    const modal = document.getElementById('modal');
    modal.classList.add('hidden');
}

document.getElementById('modal-close').addEventListener('click', closeModal);
