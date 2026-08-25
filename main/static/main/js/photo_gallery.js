let is3DMode = false;
let images = [];
let currentIndex = 0;
let isDragging = false;
let startX = 0;
let startY = 0;
let currentFrame = 1;
let currentFolder = null;
const totalFrames = 100;
const modal = document.getElementById("modal");
const modalImageContainer = document.getElementById("modal-image-container");
const modalImageName = document.getElementById("modal-image-name");
let frameCache = []; // Кеш всех кадров текущей 3D модели
let framesLoaded = false; // Флаг, что кадры подгружены

// Универсальная функция открытия модального окна
function openModal(containerID, imageSrc, folder = null) {
    // Очистка старого кеша при открытии нового модального окна
    frameCache = [];
    framesLoaded = false;
    isDragging = false;

    is3DMode = folder !== null;
    if (is3DMode) currentFolder = folder;

    const container = document.getElementById(containerID);
    images = Array.from(container.querySelectorAll('.aks_box_img')).map(img => {
        const match = img.style.backgroundImage.match(/url\(["']?(.*?)["']?\)/);
        return match ? match[1] : '';
    });

    const fileName = imageSrc.split('/').pop();

    // ИСПРАВЛЕНО: раньше индекс искался по имени файла (fileName),
    // из-за чего все 360-модели с одинаковым превью (17.webp) находили
    // всегда первое совпадение в массиве. Теперь сравниваем полный путь.
    currentIndex = images.findIndex(url => url === imageSrc);
    if (currentIndex === -1) currentIndex = 0;

    modal.style.display = "flex";
    modalImageContainer.style.backgroundImage = `url('${imageSrc}')`;
    if (modalImageName) modalImageName.textContent = fileName.split('.')[0];

    document.getElementById("modal-loader").style.display = "block";

    if (is3DMode) {
        preloadFrames(folder, () => {
            framesLoaded = true;
            document.getElementById("modal-loader").style.display = "none";
            setup3DRotation(folder, fileName);
        });
    } else {
        document.getElementById("modal-loader").style.display = "none";
    }
}

// Предзагрузка кадров 3D модели
function preloadFrames(folder, onComplete) {
    let loaded = 0;
    for (let i = 1; i <= totalFrames; i++) {
        const img = new Image();
        img.onload = img.onerror = () => {
            loaded++;
            if (loaded === totalFrames && typeof onComplete === "function") onComplete();
        };
        img.src = `/static/main/img/360/${folder}/${i}.webp`;
        frameCache[i] = img; // сразу добавляем в кеш
    }
}

// Настройка вращения 3D модели
function setup3DRotation(folder, startingFile) {
    currentFrame = parseInt(startingFile.split('.')[0]) || 1;
    modalImageContainer.ondragstart = () => false;

    function updateFrame(newFrame) {
        if (!framesLoaded) return; // запрещаем вращение до полной загрузки
        if (newFrame < 1) newFrame = totalFrames;
        if (newFrame > totalFrames) newFrame = 1;

        currentFrame = newFrame;

        // Используем кадр из кеша
        if (!frameCache[currentFrame]) {
            let img = new Image();
            img.src = `/static/main/img/360/${currentFolder}/${currentFrame}.webp`;
            frameCache[currentFrame] = img;
        }

        modalImageContainer.style.backgroundImage = `url('${frameCache[currentFrame].src}')`;

        bufferFrames(currentFrame);
    }

    function bufferFrames(centerFrame) {
        for (let i = -15; i <= 15; i++) { // увеличенный буфер
            let frame = centerFrame + i;
            if (frame < 1) frame += totalFrames;
            if (frame > totalFrames) frame -= totalFrames;
            if (!frameCache[frame]) {
                let img = new Image();
                img.src = `/static/main/img/360/${currentFolder}/${frame}.webp`;
                frameCache[frame] = img;
            }
        }
    }

    modalImageContainer.onmousedown = (e) => {
        e.preventDefault();
        if (!framesLoaded) return; // блокируем перетаскивание
        isDragging = true;
        startX = e.clientX;
    };

    window.onmousemove = (e) => {
        if (!isDragging || !is3DMode) return;

        let delta = e.clientX - startX;
        let frameChange = Math.round(-delta / 20);

        if (frameChange !== 0) {
            updateFrame(currentFrame + frameChange);
            startX = e.clientX;
        }
    };

    window.onmouseup = () => isDragging = false;

    // Первоначальная подгрузка буфера
    updateFrame(currentFrame);
}

// Переключение изображений
function nextImage() {
    changeImage(1);
}

function prevImage() {
    changeImage(-1);
}

function changeImage(direction) {
    resetTransform();
    currentIndex = (currentIndex + direction + images.length) % images.length;
    let newImageUrl = images[currentIndex];

    if (is3DMode) {
        let folderMatch = newImageUrl.match(/360\/([^\/]+)/);
        if (folderMatch) currentFolder = folderMatch[1];

        let fileName = newImageUrl.split('/').pop();
        currentFrame = parseInt(fileName.split('.')[0]) || 1;

        // Показ loader при смене изображения
        document.getElementById("modal-loader").style.display = "block";
        frameCache = []; // очищаем старый кеш
        framesLoaded = false;
        isDragging = false;

        preloadFrames(currentFolder, () => {
            framesLoaded = true;
            document.getElementById("modal-loader").style.display = "none";
            setup3DRotation(currentFolder, fileName);
            if (modalImageName) modalImageName.textContent = fileName.split('.')[0];
        });
    } else {
        modalImageContainer.style.backgroundImage = `url('${newImageUrl}')`;
        if (modalImageName) modalImageName.textContent = newImageUrl.split('/').pop().split('.')[0];
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

// Перетаскивание обычного изображения
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
    frameCache = []; // очищаем кеш при закрытии
    framesLoaded = false;
    isDragging = false;
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

// Удаление расширений у названий превью
document.addEventListener("DOMContentLoaded", function () {
    const images = document.querySelectorAll(".image-name");
    images.forEach((img) => {
        const filename = img.textContent.trim();
        const nameWithoutExtension = filename.replace(/\.[^.]+$/, '');
        img.textContent = nameWithoutExtension;
    });
});