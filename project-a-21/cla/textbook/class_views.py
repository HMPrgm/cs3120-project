from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ClassForm
from textbook.models import Class
from user.models import get_role

redirect_link = '/catalog'
index_link = '/catalog/class'

@login_required
def index(request):
    query = request.GET.get("q", "")
    classes = Class.objects.filter(name__icontains=query) if query else Class.objects.all()
    role = get_role(request.user)

    if role != 'librarian':
        return redirect(redirect_link)
    
    params = {
        "query": query,
        "classes": classes
        }

    return render(request, "textbook/class/index.html", params)

@login_required
def create(request):
    if get_role(request.user) != 'librarian':
        return redirect(redirect_link)
    
    if request.method == 'POST':
        class_form = ClassForm(request.POST)
        
        if class_form.is_valid():
            class_obj = class_form.save()
            messages.success(request, 'Class created successfully.')
            return redirect(index_link)
    else:
        class_form = ClassForm()
    
    return render(request, 'textbook/class/create.html', {'class_form': class_form})


@login_required   
def update(request, pk):
    if get_role(request.user) != 'librarian':
        return redirect(index_link)
    class_obj = get_object_or_404(Class, pk=pk)
    
    if request.method == 'POST':
        class_form = ClassForm(request.POST, instance=class_obj)
        
        if class_form.is_valid():
            class_form.save()
            messages.success(request, 'Class updated successfully.')
            return redirect(index_link)
    else:
        class_form = ClassForm(instance=class_obj)
    
    return render(request, 'textbook/class/update.html', {'class_form': class_form})

@login_required   
def delete(request, pk):
    if get_role(request.user) != 'librarian':
        return redirect(redirect_link)
    class_obj = get_object_or_404(Class, pk=pk)
    if request.method == 'POST':
        class_obj.delete()
        messages.success(request, 'Class deleted successfully.')
    return redirect(index_link)

login_required
def detail(request, pk):
    if get_role(request.user) != 'librarian':
        return redirect(index_link)
    class_obj = get_object_or_404(Class, id=pk)
    
    
    params = {
        "class_obj": class_obj,
            }
    return render(request, "textbook/class/detail.html", params)