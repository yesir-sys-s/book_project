from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse

class Genre(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    published_date = models.DateField()
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    description = models.TextField(blank=True)
    genres = models.ManyToManyField(Genre, related_name='books')
    language = models.CharField(max_length=50, default='English')
    pages = models.PositiveIntegerField(null=True, blank=True)
    
    def __str__(self):
        return self.title
    
    def get_average_rating(self):
        reviews = self.review_set.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0

    def get_share_url(self):
        return f"/book/{self.pk}/"

    def get_absolute_url(self):
        return reverse('book-detail', kwargs={'pk': self.pk})

class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('book', 'user')  # One review per user per book
    
    def __str__(self):
        return f"{self.user.username}'s review of {self.book.title}"

class ReviewVote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    is_helpful = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'review')

class ReviewComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class ReadingList(models.Model):
    name = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    books = models.ManyToManyField(Book, through='ReadingListItem')
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse('reading-list-detail', kwargs={'pk': self.pk})
    
    def __str__(self):
        return self.name

class ReadingListItem(models.Model):
    READING_STATUS = [
        ('want', 'Want to Read'),
        ('reading', 'Currently Reading'),
        ('read', 'Read')
    ]
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    reading_list = models.ForeignKey(ReadingList, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=READING_STATUS, default='want')
    progress = models.IntegerField(default=0) # Page number or percentage
    added_at = models.DateTimeField(auto_now_add=True)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    favorite_genres = models.ManyToManyField(Genre, blank=True)
    reading_goal = models.IntegerField(default=0)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    following = models.ManyToManyField(
        'self',
        through='UserFollowing',
        through_fields=('from_user', 'to_user'),
        symmetrical=False,
        related_name='followers'
    )
    
    def __str__(self):
        return f"{self.user.username}'s profile"

class UserFollowing(models.Model):
    from_user = models.ForeignKey(UserProfile, related_name='following_relationships', on_delete=models.CASCADE)
    to_user = models.ForeignKey(UserProfile, related_name='follower_relationships', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')
        
    def __str__(self):
        return f"{self.from_user.user.username} follows {self.to_user.user.username}"