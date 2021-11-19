from django.db.models import DateField, Model


class TimeStampMixin(Model):
    created_at = DateField(auto_now_add=True)
    updated_at = DateField(auto_now=True)

    class Meta:
        abstract = True
