from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from taggit.managers import TaggableManager
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
from django import forms
from django.core.files.storage import FileSystemStorage
from phone_field import PhoneField


# how to create a custom manager to retrieve all published posts.
class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset() \
                                            .filter(status='published')


class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date='publish')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    # body = models.TextField()
    body = MarkdownxField()
    post_img = models.ImageField(upload_to='post_images/', null=True)
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    tags = TaggableManager()
    objects = models.Manager()  # default manager.
    published = PublishedManager()  # our custom manager.

    class Meta:
        ordering = ('-publish',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail',
                       args=[self.publish.year,
                             self.publish.month,
                             self.publish.day,
                             self.slug])

    # Create a property that returns the markdown instead
    @property
    def formatted_markdown(self):
        return markdownify(self.body)


class Comment(models.Model):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='comments')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    comment = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return f'Comment by {self.name} on {self.post}'


class Contact(models.Model):
    heading = MarkdownxField()
    phone = PhoneField(blank=True, help_text="Company's Phone number")
    email = models.EmailField()
    address = models.TextField(default='')

    def __str__(self):
        return self.heading

    # Create a property that returns the markdown instead
    @property
    def formatted_markdown(self):
        return markdownify(self.heading)


class About(models.Model):
    about = MarkdownxField()
    name = models.CharField(max_length=20, default='')
    logo = models.ImageField(upload_to='site_images/', null=True)

    def __str__(self):
        return self.name

    # Create a property that returns the markdown instead
    @property
    def formatted_markdown(self):
        return markdownify(self.about)
