from django.db import models
from django.contrib.auth.models import User
from usuarios.models import UfEstados
import datetime


class Security_Logs(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    Usuario = models.CharField(max_length=225, null=True, blank=True)
    CEP = models.CharField(max_length=9, null=True, default='')  # 17800-000
    Endereco = models.CharField(max_length=200, null=True, default='')
    Numero = models.CharField(max_length=10, default='0')
    Bairro = models.CharField(
        max_length=125, blank=True, null=True, default='')
    urlGgleMaps = models.URLField(max_length=2000, blank=True, null=True)
    Cidade = models.CharField(max_length=175, blank=True, null=True)
    Country = models.CharField(max_length=100, default='Brasil')
    UF = models.ForeignKey(
        UfEstados, on_delete=models.DO_NOTHING, null=True, blank=True)
    IP = models.CharField(max_length=15)  # 192.125.852.964
    Perfil_User = models.CharField(max_length=125, blank=True, null=True)
    Atividade = models.TextField(null=True, blank=True)
    # Data e hora da ocorrência da atividade
    DtHr_Atividade = models.DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return self.user.username
