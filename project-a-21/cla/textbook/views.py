from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import TextbookForm, TextbookPhotoForm, LibraryForm, TextbookRatingForm
from textbook.models import Textbook, TextbookPhoto, TextbookRequest, Library, Collection, TextbookRating
from user.models import get_role

index_link = '/catalog'

def index(request):
    query = request.GET.get("q", "")

    qs = Textbook.objects.all()

    if query:
        qs = qs.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query)
        )

    textbooks = qs.exclude(collection__private=True).distinct()

    role = get_role(request.user)

    return render(request, "textbook/index.html", {
        "query": query,
        "textbooks": textbooks,
        "role": role,
    })

@login_required
def create(request):
    user_profile = request.user.profile
    if user_profile.role != 'librarian':
        return redirect(index_link)
    
    if request.method == 'POST':
        textbook_form = TextbookForm(request.POST)
        photo_form = TextbookPhotoForm(request.POST, request.FILES)
        
        if textbook_form.is_valid() and photo_form.is_valid():
            textbook = textbook_form.save()
            photo = photo_form.save(commit=False)
            photo.textbook = textbook
            photo.save()
            messages.success(request, 'Textbook created successfully.')
            return redirect(index_link)
    else:
        textbook_form = TextbookForm()
        photo_form = TextbookPhotoForm()
    
    return render(request, 'textbook/create.html', {'textbook_form': textbook_form, 'photo_form': photo_form})


@login_required
def update(request, pk):
    role = get_role(request.user)
    if role != 'librarian':
        return redirect(index_link)

    textbook = get_object_or_404(Textbook, pk=pk)
    photo = textbook.get_picture()

    if request.method == 'POST':
        textbook_form = TextbookForm(request.POST, instance=textbook)
        photo_form = TextbookPhotoForm(request.POST, request.FILES, instance=photo)

        if textbook_form.is_valid() and photo_form.is_valid():
            saved_textbook = textbook_form.save()
            picture_uploaded = photo_form.cleaned_data.get('picture')

            if picture_uploaded:
                new_photo = photo_form.save(commit=False)
                new_photo.textbook = saved_textbook
                new_photo.save()
            elif not picture_uploaded and photo:
                # Keep existing photo — no action needed
                pass
            elif not picture_uploaded and photo is None:
                # No existing photo and none uploaded — still valid
                pass

            messages.success(request, 'Textbook updated successfully.')
            return redirect(index_link)

    else:
        textbook_form = TextbookForm(instance=textbook)
        photo_form = TextbookPhotoForm(instance=photo)

    return render(request, 'textbook/update.html', {
        'textbook_form': textbook_form,
        'photo_form': photo_form,
    })


@login_required   
def delete(request, pk):
    role = get_role(request.user)
    if role != 'librarian':
        return redirect(index_link)
    textbook = get_object_or_404(Textbook, pk=pk)
    if request.method == 'POST':
        textbook.delete()
        messages.success(request, 'Textbook deleted successfully.')
        return redirect(index_link)
    
    return redirect(index_link)

@login_required  
def textbook_detail(request, pk):
    textbook = get_object_or_404(Textbook, id = pk)
    img = textbook.get_picture().picture if textbook.get_picture() else None

    role = get_role(request.user)

    approved = False
    already_reviewed = False
    if role == 'patron':
        approved = TextbookRequest.objects.filter(
            user=request.user,
            textbook=textbook,
            status='APPROVED'
        ).exists()
        already_reviewed = TextbookRating.objects.filter(
            user=request.user,
            textbook=textbook
        ).exists()

    return render(request, "textbook/textbook_detail.html", {
        "textbook": textbook,
        "role": role,
        "img": img,
        "approved": approved,
        "has_review": already_reviewed,
    })

@login_required
def request_textbook(request, pk):
    role = get_role(request.user)
    if role != 'patron':
        return redirect(index_link)

    textbook = get_object_or_404(Textbook, id=pk)

    if textbook.checked_out:
        messages.warning(request, "This textbook is already checked out and unavailable.")
        return redirect("catalog:textbook_detail", pk=pk)

    existing_request = TextbookRequest.objects.filter(
        user=request.user,
        textbook=textbook,
        status__in=['PENDING', 'APPROVED'] 
    ).first()

    if existing_request:
        messages.info(request, "You've already requested this textbook.")
    else:
        TextbookRequest.objects.create(user=request.user, textbook=textbook)
        messages.success(request, "Your textbook request has been submitted.")

    return redirect("catalog:textbook_detail", pk=pk)

@login_required
def request_detail(request, pk):
    role = get_role(request.user)
    if role != "librarian":
        return redirect("home:index")

    req = get_object_or_404(TextbookRequest, id=pk)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "approve":
            req.status = "APPROVED"
            req.save()

            textbook = req.textbook
            textbook.checked_out = True
            textbook.save()

            messages.success(request, "Request approved and textbook marked as checked out.")
        elif action == "deny":
            req.status = "DENIED"
            req.save()
            messages.success(request, "Request denied successfully.")
        return redirect("catalog:request_detail", pk=pk)

    return render(request, "textbook/request_detail.html", {
        "request_obj": req
    })

def libraries_index(request):
    query = request.GET.get("q", "")
    if query:
        libraries = Library.objects.filter(name__icontains=query)
    else:
        libraries = Library.objects.all()

    role = get_role(request.user)

    return render(request, "textbook/libraries_index.html", {
        "libraries": libraries,
        "query": query,
        "role": role,
    })

@login_required
def libraries_create(request):
    if request.user.profile.role != 'librarian':
        return redirect('catalog:libraries_index')

    if request.method == 'POST':
        form = LibraryForm(request.POST)
        if form.is_valid():
            library = form.save(commit=False)
            library.user = request.user
            library.save()
            form.save_m2m()
            messages.success(request, "Library created successfully!")
            return redirect('catalog:libraries_index')
    else:
        form = LibraryForm()

    return render(request, 'textbook/libraries_create.html', {
        'library_form': form,
        'role': get_role(request.user),
    })

def library_detail(request, library_id):
    library = get_object_or_404(Library, id=library_id)
    collections = library.collections.all()
    role = get_role(request.user)
    return render(request, "textbook/library_detail.html", {
        "library": library,
        "collections": collections,
        "role": role,
    })

@login_required
def library_update(request, library_id):
    library = get_object_or_404(Library, id=library_id)

    if request.user != library.user and get_role(request.user) != "librarian":
        return redirect("catalog:libraries_index")

    if request.method == "POST":
        form = LibraryForm(request.POST, instance=library)
        if form.is_valid():
            updated_library = form.save(commit=False)
            updated_library.user = request.user
            updated_library.save()
            form.save_m2m() 
            return redirect("catalog:libraries_detail", library_id=library.id)
    else:
        form = LibraryForm(instance=library)

    role = get_role(request.user)

    return render(request, "textbook/library_update.html", {
        "library_form": form,
        "role": role,
        "library": library,
    })

def public_collections_index(request):

    query = request.GET.get('q', '')
    collections = Collection.objects.filter(private=False)

    if query:
        collections = collections.filter(Q(name__icontains=query) | Q(user__username__icontains=query))
    

    return render(request, 'textbook/collections/index.html', {
        'collections': collections,
        'query': query,
        'role': get_role(request.user),
    })


def private_collections_index(request):
    query = request.GET.get('q', '')
    collections = Collection.objects.filter(private=True)

    if query:
        collections = collections.filter(
            Q(name__icontains=query) | 
            Q(user__username__icontains=query)
        )


    return render(request, 'catalog/collections/private.html', {
        'collections': collections,
        'query': query,
        'role': get_role(request.user),
    })


@login_required
def create_review(request, pk):

    if get_role(request.user) != 'patron':
        return redirect('catalog:textbook_detail', pk=pk)

    textbook = get_object_or_404(Textbook, pk=pk)


    approved = TextbookRequest.objects.filter(
        user=request.user, textbook=textbook, status='APPROVED'
    ).exists()
    if not approved:
        messages.error(request, "You can only review books you’ve been approved to borrow.")
        return redirect('catalog:textbook_detail', pk=pk)


    if TextbookRating.objects.filter(user=request.user, textbook=textbook).exists():
        messages.info(request, "You’ve already reviewed this book.")
        return redirect('catalog:textbook_detail', pk=pk)

    if request.method == 'POST':
        form = TextbookRatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.user = request.user
            rating.textbook = textbook
            rating.save()
            messages.success(request, "Thanks for your review!")
            return redirect('catalog:textbook_detail', pk=pk)
    else:
        form = TextbookRatingForm()

    return render(request, "textbook/create_review.html", {
        'form': form,
        'textbook': textbook
    })

@login_required
def return_textbook(request, pk):

    if get_role(request.user) != 'patron':
        return redirect('catalog:index')


    textbook = get_object_or_404(Textbook, pk=pk)
    req = TextbookRequest.objects.filter(
        user=request.user,
        textbook=textbook,
        status='APPROVED'
    ).first()

    if not req:
        messages.error(request, "You don’t have an active borrowing of that book.")
        return redirect('user:patron_borrowed_books')


    req.delete()
    textbook.checked_out = False
    textbook.save()

    messages.success(request, "Book returned—thank you!")
    return redirect('user:patron_borrowed_books')