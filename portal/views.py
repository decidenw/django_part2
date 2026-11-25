from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Application, Category
from .forms import (
    RegistrationForm,
    LoginForm,
    ApplicationCreateForm,
    StatusInProgressForm,
    StatusCompletedForm,
    CategoryForm,
)

def is_admin(user):
    return user.is_authenticated and user.is_staff

def index(request):
    completed_applications = Application.objects.filter(
        status=Application.Status.COMPLETED
    ).select_related('category')[:4]

    in_progress_count = Application.objects.filter(
        status=Application.Status.IN_PROGRESS
    ).count()

    context = {
        'completed_applications': completed_applications,
        'in_progress_count': in_progress_count,
    }
    return render(request, 'portal/index.html', context)

def register_view(request):
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно! Добро пожаловать в личный кабинет.')
            return redirect('profile')
    else:
        form = RegistrationForm()

    return render(request, 'portal/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('admin_dashboard' if request.user.is_staff else 'profile')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.is_staff:
                return redirect('admin_dashboard')
            return redirect('profile')
    else:
        form = LoginForm()

    return render(request, 'portal/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('index')

@login_required
def profile_view(request):
    applications = Application.objects.filter(user=request.user).select_related('category')
    selected_status = request.GET.get('status', '')

    if selected_status in [choice[0] for choice in Application.Status.choices]:
        applications = applications.filter(status=selected_status)

    context = {
        'applications': applications,
        'selected_status': selected_status,
        'statuses': Application.Status.choices,
    }
    return render(request, 'portal/profile.html', context)

@login_required
def create_application_view(request):
    if request.method == 'POST':
        form = ApplicationCreateForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.status = Application.Status.NEW
            application.save()
            messages.success(request, 'Заявка успешно создана и отправлена на рассмотрение!')
            return redirect('profile')
    else:
        form = ApplicationCreateForm()

    return render(request, 'portal/application_form.html', {'form': form})

@login_required
def delete_application_view(request, pk):
    application = get_object_or_404(Application, pk=pk, user=request.user)

    if application.status != Application.Status.NEW:
        messages.error(
            request,
            'Невозможно удалить заявку, так как её статус уже изменен администратором.'
        )
        return redirect('profile')

    if request.method == 'POST':
        application.delete()
        messages.success(request, 'Заявка успешно удалена.')
        return redirect('profile')

    return render(request, 'portal/application_confirm_delete.html', {'application': application})

@user_passes_test(is_admin, login_url='login')
def admin_dashboard_view(request):
    applications = Application.objects.all().select_related('user', 'category')
    selected_status = request.GET.get('status', '')

    if selected_status in [choice[0] for choice in Application.Status.choices]:
        applications = applications.filter(status=selected_status)

    categories = Category.objects.all()
    category_form = CategoryForm()

    context = {
        'applications': applications,
        'categories': categories,
        'category_form': category_form,
        'selected_status': selected_status,
        'statuses': Application.Status.choices,
    }
    return render(request, 'portal/admin_dashboard.html', context)

@user_passes_test(is_admin, login_url='login')
def set_status_in_progress_view(request, pk):
    application = get_object_or_404(Application, pk=pk)

    if application.status != Application.Status.NEW:
        messages.error(request, 'Смена статуса невозможна: заявка уже не находится в статусе «Новая».')
        return redirect('admin_dashboard')

    if request.method == 'POST':
        form = StatusInProgressForm(request.POST, instance=application)
        if form.is_valid():
            app = form.save(commit=False)
            app.status = Application.Status.IN_PROGRESS
            app.save()
            messages.success(request, f'Заявка «{app.title}» переведена в статус «Принято в работу».')
            return redirect('admin_dashboard')
    else:
        form = StatusInProgressForm(instance=application)

    return render(request, 'portal/status_in_progress.html', {
        'form': form,
        'application': application,
    })

@user_passes_test(is_admin, login_url='login')
def set_status_completed_view(request, pk):
    application = get_object_or_404(Application, pk=pk)

    if application.status != Application.Status.NEW:
        messages.error(request, 'Смена статуса невозможна: заявка уже не находится в статусе «Новая».')
        return redirect('admin_dashboard')

    if request.method == 'POST':
        form = StatusCompletedForm(request.POST, request.FILES, instance=application)
        if form.is_valid():
            app = form.save(commit=False)
            app.status = Application.Status.COMPLETED
            app.save()
            messages.success(request, f'Заявка «{app.title}» успешно выполнена!')
            return redirect('admin_dashboard')
    else:
        form = StatusCompletedForm(instance=application)

    return render(request, 'portal/status_completed.html', {
        'form': form,
        'application': application,
    })

@user_passes_test(is_admin, login_url='login')
def add_category_view(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Новая категория добавлена.')
        else:
            for error in form.errors.get('name', []):
                messages.error(request, error)
    return redirect('admin_dashboard')

@user_passes_test(is_admin, login_url='login')
def delete_category_view(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        category_name = category.name
        category.delete()
        messages.success(request, f'Категория «{category_name}» и все её заявки удалены.')
        return redirect('admin_dashboard')

    return render(request, 'portal/category_confirm_delete.html', {'category': category})