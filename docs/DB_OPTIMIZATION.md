# Database Optimization
To dealing with a bunch of data we should use the database *indexes* this will help database query faster.

## How can I debug the Database Query?
There has library calls `django_debug_toolbar`. It is helpful tool to do the Database performance debugging.
for more detail please visit [django_debug_toolbar](https://django-debug-toolbar.readthedocs.io/en/latest/).

### Set Up
Put code below into local settings file
```python
DEBUG = True
LOGGING = {
    "version": 1,
    "loggers": {
        "django.db.backends": {
            "level": "DEBUG"
        }
    }
}

# for django-debug-toolbar
if DEBUG:
    import socket  # only if you haven't already imported this

    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + ["127.0.0.1", "10.0.2.2"]

```
---

## Query Faster
Add *index* to field that ***frequently*** use to **filtering** or **ordering**.

for example please see `BookWithIndex` model in `demo_manager/models/book.py`

---

## REST API

### Provide List API that support **Pagination**
It's a bad idea to return all data in 1 request if database has a bunch of data.

We may suggest doing the `Pagination`
if the model has more than 100 data.
We've provided the `PaginationListViewSetMixin` in `config/mixins.py`.

`PaginationListViewSetMixin` will handling most use cases (i.e. filtering, ordering)

for usage example please see `BookViewSetV1` in `demo_manager/views/book.py`

---

### Caching Related Field in Queryset
The related model field(s) in queryset is not cached.
We need to use 
[`prefetch_related`](https://docs.djangoproject.com/en/4.1/ref/models/querysets/#prefetch-related) 
or [`select_related`](https://docs.djangoproject.com/en/4.1/ref/models/querysets/#select-related) 
to cache them.

- `prefetch_related` for ManytoMany and OneToMany related field
- `select_related` for OneToOne and ManyToOne related field

for usage example please see `BookViewSetV1` in `demo_manager/views/book.py` and `BookSerializer` in `demo_manager/serializers/book.py`

#### Explain Example List API

`Book` model has `authors` many to many related field
```python

class Book(models.Model):
    id = models.UUIDField(_("ID"), primary_key=True, default=uuid.uuid4, editable=False)
    isbn = models.CharField(_("ISBN: The International Standard Book Number"), max_length=255, blank=True)
    title = models.CharField(_("Title"), max_length=255)
    authors = models.ManyToManyField(Author, blank=False, related_name="books")
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
```
and in the `ViewSet`
```python
class BookViewSetV1(viewsets.ReadOnlyModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = BookSerializer
    queryset = Book.objects.all()
```
and in the `Selializer` has `authors` field there
```python
class BookSerializer(serializers.ModelSerializer):
    authors = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")

    class Meta:
        model = Book
        fields = ("id", "isbn", "title", "authors", "created_at")
```

##### List API Query Flow
1. Query all `Book` in database
2. Iteration each book to query `book.authors`
3. Return response

This is mean for each request it'll hit database **1+n** times which is not good.

##### Caching
We can simply use `prefetch_related` with `Queryset` in the `ViewSet`.

The query will reduce from **1+n** to **1** time.
```python
class BookViewSetV1(viewsets.ReadOnlyModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = BookSerializer
    queryset = Book.objects.prefetch_related("authors")
```

Alternative way, We've provided the `EagerLoadingViewSetMixin` in `config/mixins.py`.

`EagerLoadingViewSetMixin` will call `serializer.setup_eager_loading` function in `viewset.get_queryset`.

We can simply update code as below
```python
# views.py
class BookViewSetV1(EagerLoadingViewSetMixin, viewsets.ReadOnlyModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = BookSerializer
    queryset = Book.objects.all()

# serializer.py
class BookSerializer(serializers.ModelSerializer):
    authors = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")

    class Meta:
        model = Book
        fields = ("id", "isbn", "title", "authors", "created_at")
    
    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.prefetch_related('authors')
        return queryset
```
---

## Django Admin Page

### Pagination in List Page
By default, Django use `Pagination` in admin list page.

---

### Avoid related field and query the database in `Model.__str__` 
By default, Django will display model object with `Model.__str__` 
to reduce the query time we may suggest you to ***avoid*** adding related field(s).

If you want to use them to display please see next section ***Caching Related Field in List Page***

### Caching Related Field in List Page
The related model field(s) in queryset is not cached. 
We need to use 
[`prefetch_related`](https://docs.djangoproject.com/en/4.1/ref/models/querysets/#prefetch-related) 
or [`select_related`](https://docs.djangoproject.com/en/4.1/ref/models/querysets/#select-related) 
to cache them.


The reason and solution is almost exactly the same to caching queryset REST List API.


We've provided the `EagerLoadingAdminChangeListMixin` in `config/mixins.py`.
We just put the caching logic into the `setup_eager_loading` function, and it's done!

#### Caching Logic
The caching logic has almost exactly the same to REST List API 
except the `prefetch_related` will not work in Django admin list page.
Fortunately, Django queryset has `annotate` we can use it in this case.

##### Example Book
We want to add column book's authors we can simply put the code below into the admin view.
```python

class BookAdminView(EagerLoadingAdminChangeListMixin, ImportExportModelAdmin):
    model = Book
    fields = get_all_field_names(Book)
    readonly_fields = ("id", "created_at", )
    list_display = ("id", "title", "author_names", )
    search_fields = ("id", "title", "authors", )
    autocomplete_fields = ["authors"]

    def setup_eager_loading(self, queryset):
        return queryset.annotate(
            author_names=StringAgg("authors__name", delimiter=", ", ordering="authors__name"),
        )

    def author_names(self, book):
        return book.author_names
```


for usage example please see `BookAdminView` in `demo_manager/admin/book.py`

