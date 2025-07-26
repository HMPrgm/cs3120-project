from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import get_role
from textbook.models import Collection, TextbookRequest, CollectionRequests
from .forms import ProfileUpdateForm
from django.contrib import messages

@login_required
def user_profile(request):
    form = ProfileUpdateForm(instance=request.user.profile)
    
    params = {
        "user":request.user, 
        "img":request.user.profile.get_profile_picture(), 
        }
    
    return render(request, f"user/user_profile.html", params)

@login_required
def upload(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Update existing profile photo
                profile_photo = request.user.profile.user_profile
                form = ProfileUpdateForm(request.POST, request.FILES, instance=profile_photo)
                form.save()
            except AttributeError:
                # If no profile photo exists, create a new one
                profile_photo = form.save(commit=False)
                profile_photo.user_profile = request.user.profile
                profile_photo.save()
            return redirect('/user')
        else:
            print(form.errors)  # Print errors for debugging
    else:
        try:
            profile_photo = request.user.profile.user_profile
            form = ProfileUpdateForm(instance=profile_photo)
        except AttributeError:
            form = ProfileUpdateForm()
    
    return render(request, 'user/profile_photo_upload.html', {'form': form})


@login_required
def patron_borrowed_books(request):
    user = request.user
    approved_requests = TextbookRequest.objects.filter(user=user, status="APPROVED")
    
    return render(request, "user/patron_borrowed_books.html", {
        "approved_requests": approved_requests
    })

@login_required
def librarian_dashboard(request):
    return render(request, "user/librarian_dashboard.html")

@login_required
def patron_dashboard(request):
    return render(request, "user/patron_dashboard.html")

@login_required
def redirect_dashboard(request):
    role = request.user.profile.role
    if role == "librarian":
        return redirect("user:librarian_dashboard")
    elif role == "patron":
        return redirect("user:patron_dashboard")
    return redirect("home:index")

@login_required
def collections(request):
    role = get_role(request.user)
    if role != 'librarian':
        return redirect_dashboard(request)
    query = request.GET.get("q", "")
    collections = Collection.objects.filter(title__icontains=query, user=request.user) if query else Collection.objects.filter(user=request.user)

    params = {
        "query": query,
        "collections": collections,
        'role': role
        }

    return render(request, "user/librarian_collections.html", params)

@login_required
def lib_view_requests(request):
    if get_role(request.user) != "librarian":
        return redirect("home:index")  # or anywhere else
    
    requests = TextbookRequest.objects.select_related("user", "textbook").order_by("-request_date")
    return render(request, "user/lib_view_requests.html", {"requests": requests})

@login_required
def patron_view_requests(request):
    if get_role(request.user) != "patron":
        return redirect("home:index")

    requests = TextbookRequest.objects.filter(user=request.user).select_related("textbook").order_by("-request_date")

    return render(request, "user/patron_view_requests.html", {
        "requests": requests
    })

@login_required
def lib_upgrade_patrons(request):
    if get_role(request.user) != "librarian":
        return redirect("home:index")

    patrons = User.objects.filter(profile__role="patron")
    return render(request, "user/lib_upgrade_patrons.html", {
        "patrons": patrons
    })
    
@login_required
def lib_patron_collection_request(request):
    if get_role(request.user) != "librarian":
        return redirect("home:index")

    requests = CollectionRequests.objects.filter(collection__user=request.user)
    return render(request, "user/lib_view_collection_requests.html", {
        "requests": requests
    })
    
@login_required
def collection_request_detail(request, pk):
    role = get_role(request.user)
    req = get_object_or_404(CollectionRequests, id=pk)
    
    if role != "librarian" or req.collection.user != request.user:
        return redirect("home:index")

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "approve":
            req.status = "APPROVED"
            req.save()

            req.collection.add_patron(req.user)

            messages.success(request, "Request approved and user added.")
        elif action == "deny":
            req.status = "DENIED"
            req.save()
            messages.success(request, "Request denied successfully.")
        return redirect("user:collection_request_detail", pk=pk)

    return render(request, "user/collection_request_detail.html", {
        "request_obj": req
    })

@login_required
def perform_upgrade(request, user_id):
    if get_role(request.user) != "librarian":
        return redirect("home:index")

    user = get_object_or_404(User, id=user_id)

    # Prevent upgrading oneself or already upgraded users (optional)
    if user == request.user:
        messages.warning(request, "You cannot upgrade yourself.")
        return redirect("user:lib_upgrade_patrons")

    if user.profile.role == "librarian":
        messages.info(request, f"{user.username} is already a librarian.")
        return redirect("user:lib_upgrade_patrons")

    user.profile.role = "librarian"
    user.profile.save()
    messages.success(request, f"{user.username} has been upgraded to librarian.")
    return redirect("user:lib_upgrade_patrons")