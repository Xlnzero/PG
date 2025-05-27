let is3DMode = false;
let images = [];
let currentIndex = 0;
let isDragging = false;
let startX = 0;
let startY = 0;
let currentFrame = 1;
let currentFolder = null;

const totalFrames = 25;

const modal = document.getElementById("modal");
const modalImageContainer = document.getElementById("modal-image-container");
const modalImageName = document.getElementById("modal-image-name");

// Универсальная функция открытия модального окна
function openModal(containerID, imageSrc, folder = null) {
    is3DMode = folder !== null;
    if (is3DMode) {
        currentFolder = folder;
    }

    const container = document.getElementById(containerID);
    images = Array.from(container.querySelectorAll('.aks_box_img')).map(img => {
        const match = img.style.backgroundImage.match(/url\(["']?(.*?)["']?\)/);
        return match ? match[1] : '';
    });

    const fileName = imageSrc.split('/').pop();
    currentIndex = images.findIndex(url => url.split('/').pop() === fileName);
    if (currentIndex === -1) currentIndex = 0;

    modal.style.display = "flex";
    modalImageContainer.style.backgroundImage = `url('${imageSrc}')`;
    modalImageName.textContent = fileName.split('.')[0];

    if (is3DMode) {
        preloadFrames(folder);
        setup3DRotation(folder, fileName);
    }
}

// Предзагрузка кадров 3D модели
function preloadFrames(folder) {
    for (let i = 1; i <= totalFrames; i++) {
        const img = new Image();
        img.src = `/static/main/img/360/${folder}/${i}.gif`;
    }
}

// Настройка вращения 3D модели
function setup3DRotation(folder, startingFile) {
    currentFrame = parseInt(startingFile.split('.')[0]) || 17;

    modalImageContainer.ondragstart = () => false;

    modalImageContainer.onmousedown = (e) => {
        e.preventDefault();
        isDragging = true;
        startX = e.clientX;
    };

    window.onmousemove = (e) => {
        if (!isDragging || !is3DMode) return;

        let delta = e.clientX - startX;
        let frameChange = Math.round(-delta / 20);
        let newFrame = currentFrame + frameChange;

        if (newFrame < 1) newFrame = totalFrames;
        if (newFrame > totalFrames) newFrame = 1;

        if (newFrame !== currentFrame) {
            // Используем глобальную currentFolder вместо folder
            modalImageContainer.style.backgroundImage = `url('/static/main/img/360/${currentFolder}/${newFrame}.gif')`;
            currentFrame = newFrame;
            startX = e.clientX;
        }
    };

    window.onmouseup = () => isDragging = false;
}

// Переход к следующему изображению
function nextImage() {
    resetTransform();
    currentIndex = (currentIndex + 1) % images.length;
    if (is3DMode) {
        let newImageUrl = images[currentIndex];
        // Извлекаем папку из URL
        let folderMatch = newImageUrl.match(/360\/([^\/]+)/);
        if (folderMatch) {
            currentFolder = folderMatch[1];
        }
        let fileName = newImageUrl.split('/').pop();
        currentFrame = parseInt(fileName.split('.')[0]) || 17;
        preloadFrames(currentFolder);
        modalImageContainer.style.backgroundImage = `url('/static/main/img/360/${currentFolder}/${currentFrame}.gif')`;
        modalImageName.textContent = fileName.split('.')[0];
    } else {
        modalImageContainer.style.backgroundImage = `url('${images[currentIndex]}')`;
        modalImageName.textContent = images[currentIndex].split('/').pop().split('.')[0];
    }
}


// Переход к предыдущему изображению
function prevImage() {
    resetTransform();
    currentIndex = (currentIndex - 1 + images.length) % images.length;
    if (is3DMode) {
        let newImageUrl = images[currentIndex];
        // Извлекаем папку из URL
        let folderMatch = newImageUrl.match(/360\/([^\/]+)/);
        if (folderMatch) {
            currentFolder = folderMatch[1];
        }
        let fileName = newImageUrl.split('/').pop();
        currentFrame = parseInt(fileName.split('.')[0]) || 17;
        preloadFrames(currentFolder);
        modalImageContainer.style.backgroundImage = `url('/static/main/img/360/${currentFolder}/${currentFrame}.gif')`;
        modalImageName.textContent = fileName.split('.')[0];
    } else {
        modalImageContainer.style.backgroundImage = `url('${images[currentIndex]}')`;
        modalImageName.textContent = images[currentIndex].split('/').pop().split('.')[0];
    }
}

// Масштабирование
modalImageContainer.addEventListener("wheel", function (event) {
    if (is3DMode) return;
    event.preventDefault();
    let scale = parseFloat(this.style.transform.replace(/[^0-9.]/g, '')) || 1;
    scale += event.deltaY < 0 ? 0.1 : -0.1;
    this.style.transform = `scale(${Math.max(1, scale)})`;
});

// Перетаскивание
modalImageContainer.addEventListener("mousedown", function (event) {
    if (is3DMode) return;
    isDragging = true;
    startX = event.clientX - this.offsetLeft;
    startY = event.clientY - this.offsetTop;
    this.style.cursor = "grabbing";
});

document.addEventListener("mousemove", function (event) {
    if (!is3DMode && isDragging) {
        modalImageContainer.style.position = "absolute";
        modalImageContainer.style.left = (event.clientX - startX) + "px";
        modalImageContainer.style.top = (event.clientY - startY) + "px";
    }
});

document.addEventListener("mouseup", function () {
    if (!is3DMode) {
        isDragging = false;
        modalImageContainer.style.cursor = "grab";
    }
});

// Закрытие модального окна
function closeModal() {
    is3DMode = false;
    resetTransform();
    modal.style.display = "none";
}

function resetTransform() {
    modalImageContainer.style.transform = "scale(1)";
    modalImageContainer.style.position = "relative";
    modalImageContainer.style.left = "auto";
    modalImageContainer.style.top = "auto";
}

document.querySelector(".close").addEventListener("click", closeModal);
modal.addEventListener("click", function (event) {
    if (event.target === modal) closeModal();
});

// Переключение блоков
function toggleBlocks(containerID, visibleCount = 5) {
    const container = document.getElementById(containerID);
    const toggleBtn = container.querySelector('.toggle-btn');
    const allBlocks = container.querySelectorAll('.aks_box_img');
    const hiddenBlocks = container.querySelectorAll('.aks_box_img.hidden');

    if (hiddenBlocks.length > 0) {
        allBlocks.forEach(block => block.classList.remove('hidden'));
        toggleBtn.textContent = "СВЕРНУТЬ";
    } else {
        allBlocks.forEach((block, index) => {
            if (index >= visibleCount) block.classList.add('hidden');
        });
        toggleBtn.textContent = "ПОКАЗАТЬ ВСЕ";
    }
}

// Удаление расширений у названий
document.addEventListener("DOMContentLoaded", function () {
    const images = document.querySelectorAll(".image-name");
    images.forEach((img) => {
        const filename = img.textContent.trim();
        const nameWithoutExtension = filename.replace(/\.[^.]+$/, '');
        img.textContent = nameWithoutExtension;
    });
});
