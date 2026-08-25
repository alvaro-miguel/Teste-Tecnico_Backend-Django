from django.db import models

# Create your models here.

class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        return self.update(ativo=False)


class ActiveManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).filter(ativo=True)


class CommonModel(models.Model):
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    ativo = models.BooleanField(default=True)
    objects = ActiveManager()
    all_objects = SoftDeleteQuerySet.as_manager()

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        self.ativo = False
        self.save()

