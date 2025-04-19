from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Count, Avg, Q, F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.db import IntegrityError
from .models import Book, Review, Genre, UserProfile, ReadingList, ReviewVote, UserFollowing

class BookListView(ListView):
    model = Book
    template_name = 'reviews/book_list.html'
    context_object_name = 'books'
    paginate_by = 10

    def get_queryset(self):
        queryset = Book.objects.all()
        search_query = self.request.GET.get('search')
        genre = self.request.GET.get('genre')
        
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(author__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        if genre:
            queryset = queryset.filter(genres__name=genre)
        
        # Advanced search filters
        year_from = self.request.GET.get('year_from')
        year_to = self.request.GET.get('year_to')
        rating_from = self.request.GET.get('rating_from')
        rating_to = self.request.GET.get('rating_to')
        sort = self.request.GET.get('sort', '-published_date')
        
        if year_from:
            queryset = queryset.filter(published_date__year__gte=year_from)
        if year_to:
            queryset = queryset.filter(published_date__year__lte=year_to)
            
        if rating_from or rating_to:
            queryset = queryset.annotate(avg_rating=Avg('review__rating'))
            if rating_from:
                queryset = queryset.filter(avg_rating__gte=rating_from)
            if rating_to:
                queryset = queryset.filter(avg_rating__lte=rating_to)
                
        return queryset.order_by(sort).distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genres'] = Genre.objects.all()
        return context

class BookDetailView(DetailView):
    model = Book
    template_name = 'reviews/book_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_review'] = Review.objects.filter(
            book=self.object, 
            user=self.request.user
        ).first() if self.request.user.is_authenticated else None
        return context

class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    fields = ['rating', 'text']
    template_name = 'reviews/review_form.html'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.book = Book.objects.get(pk=self.kwargs['book_id'])
        try:
            return super().form_valid(form)
        except IntegrityError:
            messages.error(self.request, 'You have already reviewed this book.')
            return redirect('book-detail', pk=self.kwargs['book_id'])
    
    def get(self, request, *args, **kwargs):
        # Check if user already has a review for this book
        if Review.objects.filter(book_id=self.kwargs['book_id'], user=request.user).exists():
            messages.error(request, 'You have already reviewed this book.')
            return redirect('book-detail', pk=self.kwargs['book_id'])
        return super().get(request, *args, **kwargs)
    
    def get_success_url(self):
        return self.object.book.get_absolute_url()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book'] = Book.objects.get(pk=self.kwargs['book_id'])
        return context

class ReviewUpdateView(LoginRequiredMixin, UpdateView):
    model = Review
    fields = ['rating', 'text']
    template_name = 'reviews/review_form.html'
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise PermissionDenied
        self.book = obj.book
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book'] = self.book
        return context
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return self.object.book.get_absolute_url()

class ReviewDeleteView(LoginRequiredMixin, DeleteView):
    model = Review
    template_name = 'reviews/review_confirm_delete.html'
    
    def get_success_url(self):
        return self.object.book.get_absolute_url()

class ReviewDetailView(DetailView):
    model = Review
    template_name = 'reviews/review_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book'] = self.object.book
        return context

class SignUpView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('login')

class HomeView(ListView):
    template_name = 'reviews/home.html'
    model = Book
    context_object_name = 'books'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_reviews'] = Review.objects.select_related('book').order_by('-created_at')[:5]
        context['top_rated_books'] = Book.objects.annotate(
            avg_rating=Avg('review__rating')
        ).order_by('-avg_rating')[:5]
        context['most_reviewed'] = Book.objects.annotate(
            review_count=Count('review')
        ).order_by('-review_count')[:5]
        return context

class UserProfileView(LoginRequiredMixin, DetailView):
    model = UserProfile
    template_name = 'reviews/user_profile.html'
    context_object_name = 'profile'
    
    def get_object(self):
        return UserProfile.objects.get_or_create(user=self.request.user)[0]

class UserProfileEditView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    template_name = 'reviews/profile_edit.html'
    fields = ['avatar', 'bio', 'favorite_genres', 'reading_goal']
    success_url = reverse_lazy('user-profile')
    
    def get_object(self):
        return UserProfile.objects.get_or_create(user=self.request.user)[0]

class BookCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Book
    fields = ['title', 'author', 'published_date', 'cover_image', 'description', 'genres', 'language', 'pages']
    template_name = 'reviews/book_form.html'
    success_url = reverse_lazy('book-list')

    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_genres'] = Genre.objects.all().order_by('name')
        return context

class BookUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Book
    fields = ['title', 'author', 'published_date', 'cover_image', 'description', 'genres', 'language', 'pages']
    template_name = 'reviews/book_form.html'

    def test_func(self):
        return self.request.user.is_staff

    def get_success_url(self):
        return reverse_lazy('book-detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_genres'] = Genre.objects.all().order_by('name')
        return context

class BookDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Book
    template_name = 'reviews/book_confirm_delete.html'
    success_url = reverse_lazy('book-list')

    def test_func(self):
        return self.request.user.is_staff

class ReadingListCreateView(LoginRequiredMixin, CreateView):
    model = ReadingList
    fields = ['name', 'is_public']
    template_name = 'reviews/reading_list_form.html'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return self.object.get_absolute_url()

class ReadingListDetailView(DetailView):
    model = ReadingList
    template_name = 'reviews/reading_list_detail.html'
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return ReadingList.objects.filter(
                Q(is_public=True) | Q(user=self.request.user)
            )
        return ReadingList.objects.filter(is_public=True)

class ReviewVoteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        review = get_object_or_404(Review, pk=pk)
        is_helpful = request.POST.get('is_helpful') == 'true'
        
        vote, created = ReviewVote.objects.update_or_create(
            user=request.user,
            review=review,
            defaults={'is_helpful': is_helpful}
        )
        
        return JsonResponse({'status': 'success'})

class UserFollowView(LoginRequiredMixin, View):
    def post(self, request, user_id):
        user_to_follow = get_object_or_404(UserProfile, user_id=user_id)
        from_user_profile = request.user.userprofile
        
        UserFollowing.objects.get_or_create(
            from_user=from_user_profile,
            to_user=user_to_follow
        )
        return JsonResponse({'status': 'success'})