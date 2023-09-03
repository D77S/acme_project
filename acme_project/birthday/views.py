from django.shortcuts import get_object_or_404, redirect, render

from .forms import BirthdayForm
from .models import Birthday
from .utils import calculate_birthday_countdown


def birthday(request, pk=None):
    if pk is not None:
        # Получаем объект модели или выбрасываем 404 ошибку.
        print('\npk не является None. А является', pk)
        instance = get_object_or_404(Birthday, pk=pk)
        print('\nИзвлекли из базы объект по ключу pk и записали его в instance. Он такой: ', instance)
        # Если в запросе не указан pk
    # (если получен запрос к странице создания записи):
    else:
        # Связывать форму с объектом не нужно, установим значение None.
        print('\npk является None.')
        instance = None
        print('\nУстановим instance в None. Он такой: ', instance)
        # Передаём в форму либо данные из запроса, либо None.
    # В случае редактирования прикрепляем объект модели.
    print('\nrequest такой:', request)
    print('\nrequest.POST такой: ', request.POST)
    print('\nrequest.POST or None такой: ', (request.POST or None))
    form = BirthdayForm(
        request.POST or None,
        # Файлы, переданные в запросе, указываются отдельно.
        files=request.FILES or None,
        instance=instance)
    print('\nВ form попало такое: ', form)
    # Остальной код без изменений.
    context = {'form': form}
    # Сохраняем данные, полученные из формы, и отправляем ответ:
    print('\nform.is_valid такой: ', form.is_valid())
    if not (request.POST) and (not (form.is_valid())):
        print('\nФорма с GET-запросом. Вроде не содержит ничего невалидного, но почему-то признана невалидной.')
    if form.is_valid():
        print('\nСохраняем форму в базу')
        form.save()
        birthday_countdown = calculate_birthday_countdown(
            form.cleaned_data['birthday']
        )
        context.update({'birthday_countdown': birthday_countdown})
    else:
        print('\nНе сохраняем форму в базу.')
    print('\nДошли до рендера. Context такой: ', context)
    return render(request, 'birthday/birthday.html', context)


def birthday_list(request):
    birthdays = Birthday.objects.all()
    context = {'birthdays': birthdays}
    return render(request, 'birthday/birthday_list.html', context)


def delete_birthday(request, pk):
    # Получаем объект модели или выбрасываем 404 ошибку.
    instance = get_object_or_404(Birthday, pk=pk)
    # В форму передаём только объект модели;
    # передавать в форму параметры запроса не нужно.
    form = BirthdayForm(instance=instance)
    context = {'form': form}
    # Если был получен POST-запрос...
    if request.method == 'POST':
        # ...удаляем объект:
        instance.delete()
        # ...и переадресовываем пользователя на страницу со списком записей.
        return redirect('birthday:list')
    # Если был получен GET-запрос — отображаем форму.
    return render(request, 'birthday/birthday.html', context)
