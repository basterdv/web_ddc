document.addEventListener('DOMContentLoaded', function () {
    const categorySelect = document.getElementById('editCategory');
    const subcategorySelect = document.getElementById('editSubcategory');
    const editForm = document.getElementById('editForm');
    const editModal = document.getElementById('editModal');
    const editSubmit = document.getElementById('editSubmit');
    const cashflowIdInput = document.getElementById('cashflow_id');

    // Функция для обновления подкатегорий
    function updateSubcategories(categoryId) {
        subcategorySelect.innerHTML = '';
        if (categoryId) {
            fetch(`/get_subcategories/${categoryId}`)
                .then(response => response.json())
                .then(data => {
                    data.forEach(subcategory => {
                        const option = document.createElement('option');
                        option.value = subcategory.id;
                        option.textContent = subcategory.name;
                        subcategorySelect.appendChild(option);
                    });
                })
                .catch(error => console.error('Ошибка при загрузке подкатегорий:', error));
        }
    }

    // Обработчик события изменения категории
    categorySelect.addEventListener('change', function () {
        const categoryId = this.value;
        updateSubcategories(categoryId);
    });

    // Обработчик события открытия модального окна
    // editModal.addEventListener('shown.bs.modal', function () {
    //     const categoryId = categorySelect.value;
    //     updateSubcategories(categoryId);
    // });

    // Обработчик события показа модального окна
    editModal.addEventListener('show.bs.modal', function (event) {
        // Получаем кнопку, которая открыла модальное окно
        const button = event.relatedTarget;

        // Очищаем значения всех полей формы
        document.getElementById('editDate').value = '';
        document.getElementById('editStatus').value = '';
        document.getElementById('editType').value = '';
        document.getElementById('editCategory').value = '';
        document.getElementById('editSubcategory').innerHTML = ''; // Очищаем опции подкатегорий
        document.getElementById('editAmount').value = '0';
        document.getElementById('editComment').value = '';
        cashflowIdInput.value = ''; // Очищаем cashflow_id

        // Устанавливаем текущую дату в поле editDate
        const currentDate = new Date().toISOString().split('T')[0];
        document.getElementById('editDate').value = currentDate;

        // Если кнопка имеет атрибут data-cashflow-id, значит мы редактируем запись
        if (button && button.getAttribute('data-cashflow-id')) {
            const cashflowId = button.getAttribute('data-cashflow-id');

            cashflowIdInput.value = cashflowId;

            // Запрашиваем данные записи с сервера
            fetch(`/get_cashflow/${cashflowId}`)
                .then(response => response.json())
                .then(data => {
                    document.getElementById('editDate').value = data.date;
                    document.getElementById('editStatus').value = data.status;
                    document.getElementById('editType').value = data.type;
                    document.getElementById('editCategory').value = data.category;
                    document.getElementById('editAmount').value = data.amount;
                    document.getElementById('editComment').value = data.comment;
                    document.getElementById('editSubcategory').value=data.subcategory;


                    // Обновляем подкатегории для выбранной категории
                    updateSubcategories(data.category);
                    if (data.subcategory) {
                        document.getElementById('editSubcategory').innerHTML = data.subcategory;
                    }
                })
                .catch(error => console.error('Ошибка при загрузке данных записи:', error));
        }
    });

    // Обработчик события отправки формы
    editForm.addEventListener('submit', function (event) {
        event.preventDefault(); // Предотвращаем стандартное поведение формы


        // Получаем CSRF токен из формы
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        // Получаем данные формы
        const date = document.getElementById('editDate').value;
        const statusId = document.getElementById('editStatus').value;
        const typeId = document.getElementById('editType').value;
        const categoryId = document.getElementById('editCategory').value;
        const subcategoryId = document.getElementById('editSubcategory').value;
        const amount = document.getElementById('editAmount').value;
        const comment = document.getElementById('editComment').value;
        const cashflow_id = cashflowIdInput.value;

        // Создаем объект с данными формы
        const formData = {
            date: date,
            status: statusId,
            type: typeId,
            category: categoryId,
            subcategory: subcategoryId,
            amount: amount,
            comment: comment,
            cashflow_id: cashflow_id,
        };

        // Отправляем данные на сервер с использованием Fetch API
        fetch(cashflow_id ? `/` : '/', {
            method: cashflow_id ? 'POST' : 'POST',
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
})
;
