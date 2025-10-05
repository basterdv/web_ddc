import asyncio
import json
from datetime import datetime

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

from .models import StatusCatalog, TypeCatalog, CategoryCatalog, SubCategoryCatalog, CashFlow

# главная страница
def index(request):
    # Получение записей из журнала движения денежных средств
    try:
        cashflow_db = CashFlow.objects.all()
        status_db = StatusCatalog.objects.all()
        type_db = TypeCatalog.objects.all()
        category_db = CategoryCatalog.objects.all()
        sub_category_db = SubCategoryCatalog.objects.all()
    except Exception as e:
        print('error')
        cashflow_db = []
        status_db = []
        type_db = []
        category_db = []
        sub_category_db = []

    filter_params = {}

    # Получаем GET данные для фильтра
    if request.method == 'GET':

        status = request.GET.get('status')
        if status == 'status_all':
            status = None

        type = request.GET.get('type')
        if type == 'type_all':
            type = None

        category = request.GET.get('category')
        if category == 'category_all':
            category = None

        subcategory = request.GET.get('subcategory')
        if subcategory == 'subcategory_all':
            subcategory = None

        filterStartDate = request.GET.get('filterStartDate')
        filterEndDate = request.GET.get('filterEndDate')

        if filterStartDate and filterEndDate:
            filterStartDate = datetime.strptime(filterStartDate, '%Y-%m-%d')
            filterEndDate = datetime.strptime(filterEndDate, '%Y-%m-%d')

            cashflow_db = CashFlow.objects.filter(date__gte=filterStartDate, date__lte=filterEndDate)

        if category is not None:
            cashflow_db = CashFlow.objects.filter(category=category)

        if status is not None:
            cashflow_db = CashFlow.objects.filter(status=status)

        if type is not None:
            cashflow_db = CashFlow.objects.filter(type=type)

        if subcategory is not None:
            subcategory_db = SubCategoryCatalog.objects.filter(subcategory=subcategory)

        # Получаем параметры
        filter_params = {
            'filterStartDate': filterStartDate,
            'filterEndDate': filterEndDate,
            'status': status,
            'type': type,
            'category': category,
            'subcategory': subcategory
        }

    context = {
        'title': 'Веб-сервис для управления движением денежных средств',
        'status_db': status_db,
        'type_db': type_db,
        'filters': filter_params,
        'category_db': category_db,
        'sub_category_db': sub_category_db,
        'cashflow_db': cashflow_db,
    }

    return render(request, 'index.html', context=context)


def get_catalog_objects(data):
    status_id = get_object_or_404(StatusCatalog, id=data['status'])
    type_id = get_object_or_404(TypeCatalog, id=data['type'])
    category_id = get_object_or_404(CategoryCatalog, id=data['category'])
    if data['subcategory'] != '':
        subcategory_id = get_object_or_404(SubCategoryCatalog, id=data['subcategory'])
    else:
        subcategory_id = None
    return status_id, type_id, category_id, subcategory_id


async def async_create_cashflow(data, status_id, type_id, category_id, subcategory_id):
    await CashFlow.objects.acreate(
        date=data['date'],
        status=status_id,
        type=type_id,
        category=category_id,
        sum=data['amount'],
        subcategory=subcategory_id,
        comment=data['comment']
    )


async def async_update_cashflow(data, status_id, type_id, category_id, subcategory_id):
    await CashFlow.objects.filter(id=data['cashflow_id']).aupdate(
        date=data['date'],
        status=status_id,
        type=type_id,
        category=category_id,
        sum=data['amount'],
        subcategory=subcategory_id,
        comment=data['comment']
    )


async def async_delete_cashflow(data):
    await CashFlow.objects.filter(id=data['cashflow_id']).adelete()


def get_catalog_data():
    try:
        status_db = StatusCatalog.objects.all()
        type_db = TypeCatalog.objects.all()
        category_db = CategoryCatalog.objects.select_related('types').all()
        sub_category_db = SubCategoryCatalog.objects.all()
    except Exception as e:
        print('error')
        status_db = []
        type_db = []
        category_db = []
        sub_category_db = []
    return status_db, type_db, category_db, sub_category_db


def get_catalog_item(catalog_type, card_id):
    try:
        if catalog_type == 'status':
            record = StatusCatalog.objects.get(id=card_id)
            types = None
        elif catalog_type == 'type':
            record = TypeCatalog.objects.get(id=card_id)
            types = None
        elif catalog_type == 'category':
            record = CategoryCatalog.objects.get(id=card_id)
            types = record.types.id
        elif catalog_type == 'subcategory':
            record = SubCategoryCatalog.objects.get(id=card_id)
            types = None
        else:
            record = None

        data = {
            'id': record.id,
            'name': record.name,
            'types': types,
        }

        return JsonResponse(data, safe=False)
    except Exception as e:
        print(f'error - {e}')
        return JsonResponse({}, safe=False)

# Добавляем запись

def create_cashflow(request):
    # Парсим данные из тела запроса
    data = json.loads(request.body)

    # Получаем объекты по идентификаторам из формы
    status_id, type_id, category_id, subcategory_id = get_catalog_objects(data)

    # Создаем запись
    async def acreate_cashflow():
        await async_create_cashflow(data, status_id, type_id, category_id, subcategory_id)

    # запускаем асинхронную функцию
    asyncio.run(acreate_cashflow())

    return redirect('home')

# Редактируем запись
def update_cashflow(request):
    data = json.loads(request.body)

    # Получаем объекты по идентификаторам из формы
    status_id, type_id, category_id, subcategory_id = get_catalog_objects(data)

    # Создаем изменение записи
    async def ardit_cashflow():
        await async_update_cashflow(data, status_id, type_id, category_id, subcategory_id)

    # запускаем асинхронную функцию
    asyncio.run(ardit_cashflow())

    return redirect('home')

# Удаляем запись
async def delete_cashflow(request):
    item_id = request.POST.get('del_cashflow_form')

    await CashFlow.objects.filter(id=item_id).adelete()

    return redirect('home')


def catalog(request):
    # Получение записей из справочников
    try:
        status_db, type_db, category_db, sub_category_db = get_catalog_data()


    except Exception as e:
        print('error')
        status_db = []
        type_db = []
        category_db = []
        sub_category_db = []

    context = {
        'title': 'Каталог',
        'status_db': status_db,
        'type_db': type_db,
        'category_db': category_db,
        'sub_category_db': sub_category_db
    }

    return render(request, 'catalog.html', context=context)

def get_categories_by_type(request,typeId):
    categories = CategoryCatalog.objects.filter(types_id=typeId)
    categories_list = [{'id': category.id, 'name': category.name} for category in categories]
    return JsonResponse(categories_list, safe=False)


def get_subcategories(request, category_id):
    subcategories = SubCategoryCatalog.objects.filter(category_id=category_id)
    subcategories_list = [{'id': subcategory.id, 'name': subcategory.name} for subcategory in subcategories]
    return JsonResponse(subcategories_list, safe=False)


def get_cashflow(request, cashflow_id):
    try:
        cashflow_db = get_object_or_404(CashFlow.objects, id=cashflow_id)

        if cashflow_db.subcategory_id is not None:
            subcategory_id = cashflow_db.subcategory.id
        else:
            subcategory_id = None

        data = {
            'id': cashflow_db.id,
            'date': cashflow_db.date,
            'status': cashflow_db.status.id,
            'type': cashflow_db.type.id,
            'category': cashflow_db.category.id,
            'amount': cashflow_db.sum,
            'comment': cashflow_db.comment,
            'subcategory': subcategory_id,
        }

        return JsonResponse(data, safe=False)


    except Exception as e:
        print(f'error - {e}')
        cashflow_db = []


def get_catalog_edit(request, catalog_type, card_id):
    try:
        types = None
        if catalog_type == 'status':
            record = StatusCatalog.objects.get(id=card_id)
        elif catalog_type == 'type':
            record = TypeCatalog.objects.get(id=card_id)
        elif catalog_type == 'category':
            record = CategoryCatalog.objects.get(id=card_id)
            types = record.types.id
        elif catalog_type == 'subcategory':
            record = SubCategoryCatalog.objects.get(id=card_id)
        else:
            record = None

        data = {
            'id': record.id,
            'name': record.name,
            'types': types,
        }

        return JsonResponse(data, safe=False)
    except Exception as e:
        print(f'error - {e}')


# Добовляем в справочник запись
async def catalog_add(request):
    catalog_list = {
        'status_form': [StatusCatalog, 'status_name'],
        'type_form': [TypeCatalog, 'type_name'],
        'category_form': [CategoryCatalog, 'category_name'],
        'subcategory_form': [SubCategoryCatalog, 'subcategory_name'],
    }

    for form_key, model in catalog_list.items():
        if form_key in request.POST:
            item_name = request.POST.get(model[1])
            category_id = request.POST.get(form_key)
            type_id = request.POST.get('typefrocategory')

            if category_id != '':
                await model[0].objects.acreate(name=item_name, category_id=category_id)
            elif type_id is not None:
                await model[0].objects.acreate(name=item_name, types_id=type_id)
            else:
                await model[0].objects.acreate(name=item_name)

    return redirect('catalog')


# Удаляем запись из справочника
async def catalog_del(request):
    catalog_list = {
        'status_del_form': StatusCatalog,
        'type_del_form': TypeCatalog,
        'category_del_form': CategoryCatalog,
        'subcategory_del_form': SubCategoryCatalog,
    }

    for form_key, model in catalog_list.items():
        if form_key in request.POST:
            item_id = request.POST.get(form_key)

            await model.objects.filter(id=item_id).adelete()
            break

    return redirect('catalog')


# Редактируем запись в справочнике
async def catalog_edit(request):
    # Парсим данные из тела запроса
    data = json.loads(request.body)

    catalog_list = {
        'status': StatusCatalog,
        'type': TypeCatalog,
        'category': CategoryCatalog,
        'subcategory': SubCategoryCatalog,
    }

    for form_key, model in catalog_list.items():
        if form_key in data['catalog_type']:
            if form_key == 'category':
                await model.objects.filter(id=data['card_id_']).aupdate(
                    name=data["name"],
                    types_id=data['categoryTypes']
                )
            else:
                await model.objects.filter(id=data['card_id_']).aupdate(
                    name=data["name"],
                )

    return redirect('catalog')
