from django.contrib import admin
from .models import User, Items, Bids, Comments

# Register your models here.
admin.site.register(User)
admin.site.register(Items)
admin.site.register(Bids)
admin.site.register(Comments)

