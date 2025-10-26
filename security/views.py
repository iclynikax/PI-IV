from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from usuarios.models import Get_cGrp_Usuario
from .models import Security_Logs
from datetime import datetime, date
from django.utils.timezone import localtime
from datetime import datetime, date, timedelta
import locale


from django.utils.timezone import make_aware


# define o idioma para os nomes dos meses (ex: 'pt_BR.UTF-8' para português)
locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')


@login_required(login_url='/usuarios/login/')
def fnct_security(request):

    filtro = request.GET.get('filtro', 'hoje')  # padrão "hoje"
    hoje = datetime.now().date()

    if filtro == 'hoje':
        data_inicio = make_aware(datetime.combine(hoje, datetime.min.time()))
        data_fim = make_aware(datetime.combine(hoje, datetime.max.time()))

        info_Periodo = hoje

        # Considerando que a data de hoje é 30 de Setembro de 2025
        # data_inicio = make_aware(datetime(2025, 9, 30, 0, 0, 0))
        # data_fim = make_aware(datetime(2025, 9, 30, 23, 59, 59))

    elif filtro == 'mes':
        data_inicio = make_aware(datetime(hoje.year, hoje.month, 1))

        # último dia do mês
        if hoje.month == 12:
            proximo_mes = date(hoje.year + 1, 1, 1)
        else:
            proximo_mes = date(hoje.year, hoje.month + 1, 1)
        data_fim = make_aware(datetime.combine(
            proximo_mes - timedelta(days=1), datetime.max.time()))

        # obtém o nome do mês por extenso e o ano
        mes_extenso = hoje.strftime('%B').capitalize()  # exemplo: 'Setembro'
        info_Periodo = f"Mês: {mes_extenso} {hoje.year}"

    elif filtro == 'ano':
        data_inicio = make_aware(datetime(hoje.year, 1, 1))
        data_fim = make_aware(datetime(hoje.year, 12, 31, 23, 59, 59))

        # obtém o ano
        info_Periodo = f"Ano: {hoje.year}"

    else:
        # padrão fallback
        data_inicio = data_fim = make_aware(datetime(2025, 9, 30))

    slct_Rgstrs = Security_Logs.objects.filter(
        DtHr_Atividade__range=(data_inicio, data_fim))

    # slct_Rgstrs = Security_Logs.objects.filter(DtHr_Atividade__date=date(2025, 9, 30))

    # slct_Rgstrs = Security_Logs.objects.all()
    # slct_Rgstrs = [
    #    log for log in Security_Logs.objects.all()
    #    if localtime(log.DtHr_Atividade).date() == date(2025, 9, 30)
    # ]

    return render(request, 'dashboard.html', {'cGrp_Usuario': Get_cGrp_Usuario(request.user), 'Rgstrs_Logs': slct_Rgstrs, 'slct_Periodo': info_Periodo})


@login_required(login_url='/usuarios/login/')
def fnct_My_Profile(request):

    return render(request, 'My_Profile.html', {'cGrp_Usuario': Get_cGrp_Usuario(request.user)})


def fnct_scrty_sobre(request):

    return render(request, 'sobre.html', {'cGrp_Usuario': Get_cGrp_Usuario(request.user)})
