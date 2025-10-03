// Обработчик открытия модального окна
document.getElementById('editModal_catalog').addEventListener('show.bs.modal', function (event) {
    const button = event.relatedTarget; // Кнопка, которая открыла модальное окно
    const cardId = button.getAttribute('data-catalog-id'); // Получаем ID записи из атрибута кнопки

    const catalog_type = button.getAttribute('data-catalog-type'); //Получаем тип справочника
    const editForm = document.getElementById('editModal_catalog');

    const catalogType = button.getAttribute('data-catalog-type'); //Тип каталога
    const typeSection = editForm.querySelector('#typeSection');

    if (catalogType === '"category"') {
        typeSection.style.display = 'block';
    }else{
        typeSection.style.display = 'none';
    }

    // Запрашиваем данные записи с сервера
    fetch(`/get_catalog_edit/${catalog_type}/${cardId}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('card_name').value = data.name;
        })
        .catch(error => console.error('Ошибка при загрузке данных записи:', error))

    // Обработчик события отправки формы
    editForm.addEventListener('submit', function (event) {
        event.preventDefault(); // Предотвращаем стандартное поведение формы

        // Получаем CSRF токен из формы
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        // Получаем данные формы
        const name = document.getElementById('card_name').value;

        // Создаем объект с данными формы
        const formData = {
            name: name,
            card_id_: cardId,
            catalog_type:catalog_type,
        };

        // Отправляем данные на сервер с использованием Fetch API
        fetch(`/catalog_edit/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken, // Добавляем CSRF токен в заголовки
            },
            body: JSON.stringify(formData),
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    console.log('Успешно отправлено:', data);
                } else {
                    console.error('Ошибка:', data.message);
                }
            })
            .catch(error => console.error('Ошибка при отправке данных:', error))
            .finally(() => {
                // Закрываем модальное окно после отправки
                // const modal = bootstrap.Modal.getInstance(editModal);
                // modal.hide();
                // Обновляем страницу после закрытия окна
                location.reload();
            });

    });
});

