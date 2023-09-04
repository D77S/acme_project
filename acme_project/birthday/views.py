from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from django.urls import reverse_lazy

from .forms import BirthdayForm
from .models import Birthday
from .utils import calculate_birthday_countdown


class BirthdayMixin:
    model = Birthday
    form_class = BirthdayForm
    template_name = 'birthday/birthday.html'
    success_url = reverse_lazy('birthday:list')


# Наследуем класс от встроенного ListView.
class BirthdayListView(ListView):
    # Указываем модель, с которой работает CBV...
    model = Birthday
    # ...сортировку, которая будет применена при выводе списка объектов:
    ordering = 'id'
    # ...и даже настройки пагинации:
    paginate_by = 10


# Добавляем миксин первым по списку родительских классов.
class BirthdayCreateView(BirthdayMixin, CreateView):
    # Не нужно описывать атрибуты: все они унаследованы от BirthdayMixin.
    pass


class BirthdayUpdateView(BirthdayMixin, UpdateView):
    # И здесь все атрибуты наследуются от BirthdayMixin.
    pass


class BirthdayDeleteView(DeleteView):
    model = Birthday
    template_name = 'birthday/birthday.html'
    success_url = reverse_lazy('birthday:list')


def birthday(request, pk=None):
    if pk is not None:
        # Получаем объект модели или выбрасываем 404 ошибку.
        print('\npk не является None. А является', pk)
        instance = get_object_or_404(Birthday, pk=pk)
        print('\ninstance такой: ', instance)
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
        print('\nФорма с GET-запросом, признана невалидной.')
    if form.is_valid():
        print('\nСохраняем форму в базу')
        form.save()
        birthday_countdown = calculate_birthday_countdown(
            form.cleaned_data['birthday']
        )
        context.update(
            {'birthday_countdown': birthday_countdown})  # type: ignore
    else:
        print('\nНе сохраняем форму в базу.')
    print('\nДошли до рендера. Context такой: ', context)
    return render(request, 'birthday/birthday.html', context)


def birthday_list(request):
    # Получаем список всех объектов с сортировкой по id.
    birthdays = Birthday.objects.order_by('id')
    # Создаём объект пагинатора с количеством 10 записей на страницу.
    paginator = Paginator(birthdays, 10)
    # Получаем из запроса значение параметра page.
    page_number = request.GET.get('page')
    # Получаем запрошенную страницу пагинатора.
    # Если параметра page нет в запросе или его значение не приводится к числу,
    # вернётся первая страница.
    page_obj = paginator.get_page(page_number)
    # Вместо полного списка объектов передаём в контекст
    # объект страницы пагинатора
    context = {'page_obj': page_obj}
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
