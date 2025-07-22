from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ClassForm, CollectionForm
from textbook.models import Collection, CollectionRequests
from user.models import get_role, User

redirect_link = '/catalog'
index_link = '/catalog/collections'
private_index_link = '/catalog/collections/private'

def index(request):
    
    query = request.GET.get("q", "")
    collections = Collection.get_collections_by_user(request.user, query)
    role = get_role(request.user)

    params = {
        "query": query,
        "collections": collections,
        'role': role,
        'user':request.user
        }

    return render(request, "textbook/collections/index.html", params)

def private_index(request):
    
    query = request.GET.get("q", "")
    
    collections = Collection.get_private_collections(query)

    collection_requests = CollectionRequests.objects.filter(user=request.user)
    requests= [cr.collection for cr in collection_requests] 
    role = get_role(request.user)

    params = {
        "query": query,
        "collections": collections,
        'role': role,
        'requests': requests
        }
    
    return render(request, "textbook/collections/private_index.html", params)

@login_required
def request_collection_access(request, pk):
    collection = get_object_or_404(Collection, pk=pk)
    user = request.user
    if request.method == "POST":
        if CollectionRequests.objects.filter(user=user, collection=collection).exists():
            print("Hi")
            return redirect("catalog:collections_private_index")
        else:
            CollectionRequests.objects.create(collection=collection, user=user)
            return redirect("catalog:collections_private_index")
    return redirect("catalog:collections_private_index")

@login_required
def create(request):
    role = get_role(request.user)
    
    if request.method == 'POST':
        collection_form = CollectionForm(request.POST)
        
        if collection_form.is_valid():
            cleaned_data = collection_form.cleaned_data
            textbooks = cleaned_data.pop('textbooks')
            cleaned_data['user'] = request.user
            
            instance = Collection.objects.create(**cleaned_data)
            
            instance.textbooks.set(textbooks)
            
            if instance.private:
                for tb in textbooks:
                    public_cols = Collection.objects.filter(private=False, textbooks=tb)
                    for pub in public_cols:
                        pub.textbooks.remove(tb)
            
            messages.success(request, 'Collection created successfully.')
            return redirect(index_link)
    else:
        collection_form = CollectionForm()
    
    return render(request, 'textbook/collections/create.html', {
        'collection_form': collection_form,
        'role': role
    })

@login_required   
def update(request, pk):
    role = get_role(request.user)
    collection = get_object_or_404(Collection, pk=pk)
    if role != 'librarian' and request.user != collection.user:
        return redirect(index_link)
    
    if request.method == 'POST':
        collection_form = CollectionForm(request.POST, instance=collection)
        
        if collection_form.is_valid():
            saved = collection_form.save()
            
            if saved.private:
                for tb in saved.textbooks.all():
                    public_cols = Collection.objects.filter(private=False, textbooks=tb)
                    for pub in public_cols:
                        pub.textbooks.remove(tb)
            
            messages.success(request, 'Collection updated successfully.')
            return redirect(index_link)
    else:
        collection_form = CollectionForm(instance=collection)
    
    return render(request, 'textbook/collections/update.html', {
        'collection_form': collection_form,
        'role': role
    })

@login_required   
def delete(request, pk):
    role = get_role(request.user)
    collection = get_object_or_404(Collection, pk=pk)
    if role != 'librarian' and request.user != collection.user:
        return redirect(index_link)
    if request.method == 'POST':
        collection.delete()
        messages.success(request, 'Collection deleted successfully.')
        return redirect(index_link)
    
    return redirect(index_link)

def detail(request, pk):
    collection = get_object_or_404(Collection, id=pk)
    if collection.private and get_role(request.user) != 'librarian' and not collection.is_patron_allowed(request.user):
        return redirect(private_index_link)
    
    params = {
        "collection": collection,
        "role": get_role(request.user),
        "user": request.user
            }
    return render(request, "textbook/collections/detail.html", params)

@login_required
def view_add_patrons(request, pk):
    
    collection = get_object_or_404(Collection, id=pk)
    
    if get_role(request.user) != "librarian" or collection.user != request.user:
        return redirect("catalog:collections_index")

    patrons = User.objects.filter(profile__role="patron")
    allowed_patrons = []
    disallowed_patrons = []
    for patron in patrons:
        if collection.is_patron_allowed(patron):
            allowed_patrons.append(patron)
        else:
            disallowed_patrons.append(patron)
    return render(request, "textbook/collections/add_patrons.html", {
        "allowed_patrons": allowed_patrons,
        "disallowed_patrons": disallowed_patrons,
        "collection": collection
    })

@login_required
def perform_add_patron(request, pk, user_id):
    collection = get_object_or_404(Collection, id=pk)
    if get_role(request.user) != "librarian" or collection.user != request.user:
        return redirect("catalog:collections_index")
    
    user = get_object_or_404(User, id=user_id)
    
    # Prevent upgrading oneself or already upgraded users (optional)
    if user == request.user:
        messages.warning(request, "You cannot add yourself.")
        return redirect(f"catalog:collections_add_patron_view", pk=pk)

    if user.profile.role == "librarian" or collection.is_patron_allowed(user):
        messages.info(request, f"{user.username} is already allowed.")
        return redirect(f"catalog:collections_add_patron_view",pk=pk)

    collection.add_patron(user)
    messages.success(request, f"{user.username} has been added to {collection.name}.")
    return redirect(f"catalog:collections_add_patron_view",pk=pk)

@login_required
def perform_remove_patron(request, pk, user_id):
    collection = get_object_or_404(Collection, id=pk)
    if get_role(request.user) != "librarian" or collection.user != request.user:
        return redirect("catalog:collections_index")
    
    user = get_object_or_404(User, id=user_id)
    
    # Prevent upgrading oneself or already upgraded users (optional)
    if user == request.user:
        messages.warning(request, "You cannot remove yourself.")
        return redirect(f"catalog:collections_add_patron_view", pk=pk)

    if user.profile.role == "librarian" or not collection.is_patron_allowed(user):
        messages.info(request, f"{user.username} is already not allowed.")
        return redirect(f"catalog:collections_add_patron_view",pk=pk)

    collection.remove_patron(user)
    messages.success(request, f"{user.username} has been removed from {collection.name}.")
    return redirect(f"catalog:collections_add_patron_view",pk=pk)