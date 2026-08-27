from django.db import models, router, transaction

# Create your models here.

class SoftDeleteQuerySet(models.QuerySet):
    @transaction.atomic
    def delete(self):
        quantidade_total = 0
        detalhes = {}

        for objeto in self.select_for_update():
            quantidade, detalhes_objeto = objeto.delete(using=self.db)
            quantidade_total += quantidade
            for modelo, total in detalhes_objeto.items():
                detalhes[modelo] = detalhes.get(modelo, 0) + total

        return quantidade_total, detalhes


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
        if not self.ativo:
            return 0, {}

        using = kwargs.get('using') or router.db_for_write(
            self.__class__,
            instance=self,
        )
        self.ativo = False
        self.save(using=using, update_fields=['ativo', 'atualizado_em'])
        modelo = self._meta.label
        return 1, {modelo: 1}

