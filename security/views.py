import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# Agrupa os registros por hora usando  TruncHour do Django.
from django.db.models.functions import TruncHour, TruncDay, TruncMonth
from django.db.models import Count, DateTimeField
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from usuarios.models import Get_cGrp_Usuario
from .models import Security_Logs

from datetime import datetime, date, timedelta
import locale
import random

from django.utils.timezone import now, make_aware, localtime
from collections import defaultdict


# define o idioma para os nomes dos meses (ex: 'pt_BR.UTF-8' para português)
locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')


# ====================================================================================================
# ----------------------------------------------------------------------------------------------------
@login_required(login_url='/usuarios/login/')
def fnct_scrty_test(request):

    filtro = request.GET.get('filtro', 'hoje')  # padrão "hoje"
    hoje = datetime.now().date()

    mes_extenso = hoje.strftime('%B').capitalize()  # exemplo: 'Setembro'
    mesAnoCrrnte = f"{mes_extenso}"

    anoCrrnte = f"{hoje.year}"

    # Define o início e o fim do dia atual
    incioHoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    data_fim = incioHoje + timedelta(days=1)

    # Conta o total de registros de hoje
    nTtlHjeCorrente = Security_Logs.objects.filter(
        DtHr_Atividade__range=(incioHoje, data_fim)).count()

    # Conta o Total de Usuários que realizaram acesso no mês atual
    # Início do mês corrente
    dtHoje = datetime.now()
    incioMes = dtHoje.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Retorna os últimos 5 registros de hoje
    incioDia = make_aware(datetime.combine(hoje, datetime.min.time()))
    fimDia = make_aware(datetime.combine(hoje, datetime.max.time()))

    agora = datetime.now()
    inicio = agora.replace(hour=0, minute=0, second=0, microsecond=0)
    fim = inicio + timedelta(days=1)

    incioDia = inicio.replace(tzinfo=None)
    fimDia = fim.replace(tzinfo=None)

    n5UltmosRgstrosDeHoje = (Security_Logs.objects.filter(DtHr_Atividade__range=(incioDia, fimDia), DtHr_Atividade__lt=now())
                             .order_by('-DtHr_Atividade')[:6]
                             )

    # Início do próximo mês
    if dtHoje.month == 12:
        fimMes = dtHoje.replace(year=dtHoje.year + 1, month=1,
                                day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        fimMes = dtHoje.replace(month=dtHoje.month + 1, day=1,
                                hour=0, minute=0, second=0, microsecond=0)

    # Consulta filtrando registros do mês corrente
    nTtlMesCorrente = Security_Logs.objects.filter(
        DtHr_Atividade__range=(incioMes, fimMes)).count()

    # Início do ano corrente
    incioAno = dtHoje.replace(month=1, day=1, hour=0,
                              minute=0, second=0, microsecond=0)

    # Início do próximo ano
    fimAno = dtHoje.replace(year=dtHoje.year + 1, month=1,
                            day=1, hour=0, minute=0, second=0, microsecond=0)

    # Consulta filtrando registros do ano corrente
    nTtlAnoCorrente = Security_Logs.objects.filter(
        DtHr_Atividade__range=(incioAno, fimAno)).count()

    if filtro == 'hoje':

        data_inicio = make_aware(datetime.combine(hoje, datetime.min.time())).replace(
            microsecond=0).astimezone(None).replace(tzinfo=None)
        data_fim = make_aware(datetime.combine(hoje, datetime.max.time())).replace(
            microsecond=0).astimezone(None).replace(tzinfo=None)

        info_Periodo = hoje
        info_AntPrdo = make_aware(datetime(hoje.year, hoje.month, hoje.day-1))
        info_PrxPrdo = make_aware(datetime(hoje.year, hoje.month, hoje.day+1))

        # Considerando que a data de hoje é 30 de Setembro de 2025
        # data_inicio = make_aware(datetime(2025, 9, 30, 0, 0, 0))
        # data_fim = make_aware(datetime(2025, 9, 30, 23, 59, 59))

        nTtlRgstrsMaxAtvddes = 25

    elif filtro == 'mes':
        # Início do mês
        data_inicio = make_aware(datetime.combine(datetime(hoje.year, hoje.month, 1), datetime.min.time())).replace(
            microsecond=0).astimezone(None).replace(tzinfo=None)

        # Último dia do mês

        if hoje.month == 1:
            anterior_mes = date(hoje.year - 1, 12, 1)
        else:
            anterior_mes = date(hoje.year, hoje.month - 1, 1)

        # Último dia do mês
        if hoje.month == 12:
            proximo_mes = date(hoje.year + 1, 1, 1)
        else:
            proximo_mes = date(hoje.year, hoje.month + 1, 1)

        ultimo_dia_mes = proximo_mes - timedelta(days=1)
        data_fim_teorica = make_aware(datetime.combine(ultimo_dia_mes, datetime.max.time())).replace(
            microsecond=0).astimezone(None).replace(tzinfo=None)

        # Data atual (agora)
        agora = datetime.now().replace(microsecond=0)

        # Garante que data_fim não ultrapasse hoje
        data_fim = min(data_fim_teorica, agora)

        # obtém o nome do mês por extenso e o ano
        mes_extenso = hoje.strftime('%B').capitalize()  # exemplo: 'Setembro'
        info_Periodo = f"Mês: {mes_extenso}/{hoje.year}"

        mes_extenso = proximo_mes.strftime(
            '%B').capitalize()  # exemplo: 'Setembro'
        info_AntPrdo = f"{mes_extenso}/{hoje.year}"
        info_PrxPrdo = f"{mes_extenso}/{hoje.year}"

        nTtlRgstrsMaxAtvddes = 250

    elif filtro == 'ano':
        data_inicio = make_aware(datetime(hoje.year, 1, 1))
        data_fim = make_aware(datetime(hoje.year, 12, 31, 23, 59, 59))

        data_inicio = make_aware(datetime.combine(data_inicio, datetime.min.time())).replace(
            microsecond=0).astimezone(None).replace(tzinfo=None)
        data_fim = make_aware(datetime.combine(data_fim, datetime.max.time())).replace(
            microsecond=0).astimezone(None).replace(tzinfo=None)

        # obtém o ano
        info_Periodo = f"Ano: {hoje.year}"
        info_PrxPrdo = f"{hoje.year+1}"

        nTtlRgstrsMaxAtvddes = 750
    else:
        # padrão fallback
        data_inicio = data_fim = make_aware(datetime(2025, 9, 30))

    # Seleciona todos os registros de acordo com o periodo
    slct_Rgstrs = Security_Logs.objects.filter(
        DtHr_Atividade__range=(data_inicio, data_fim))

    # Define intervalo de hoje (00:00 até 23:59)
    agora = datetime.now()
    inicio = agora.replace(hour=0, minute=0, second=0, microsecond=0)
    fim = inicio + timedelta(days=1)

    inicio_naive = inicio.replace(tzinfo=None)
    fim_naive = fim.replace(tzinfo=None)

    # Consulta registros
    slct_Rgstrs = Security_Logs.objects.filter(
        DtHr_Atividade__range=(inicio_naive, fim_naive))

    # Seleção das Atividades por cidades. Usado no Gráfico tipo 'radar'.
    slct_Cidades = (
        Security_Logs.objects.filter(
            DtHr_Atividade__range=(data_inicio, data_fim))
        # Retorna só os nomes das cidades
        .values_list('Cidade', flat=True)
        .distinct()                        # Remove duplicadas
        # Ordena alfabeticamente
        .order_by('Cidade')
    )

    slct_Atividades = (
        Security_Logs.objects
        .filter(DtHr_Atividade__range=(data_inicio, data_fim))
        .values('Atividade')         # Agrupa por atividade
        .annotate(total=Count('id'))  # Conta quantos registros por atividade
        .order_by('Atividade')       # Ordena por nome (opcional)
    )

    # Filtra pelo período desejado
    dados = (
        Security_Logs.objects
        .filter(DtHr_Atividade__range=(data_inicio, data_fim))
        .values('Cidade', 'Atividade')
        .annotate(total=Count('id'))
    )

    dt_Incio_Radar = make_aware(datetime(hoje.year, hoje.month, 1))
    # último dia do mês
    if hoje.month == 12:
        proximo_mes = date(hoje.year + 1, 1, 1)
    else:
        proximo_mes = date(hoje.year, hoje.month + 1, 1)
    dt_fim_Radar = make_aware(datetime.combine(
        proximo_mes - timedelta(days=1), datetime.max.time())
    )

    dadosRadar = (
        Security_Logs.objects
        .filter(DtHr_Atividade__range=(dt_Incio_Radar, dt_fim_Radar))
        .values('Cidade', 'Atividade')
        .annotate(total=Count('id'))
    )

    # Cria listas
    atividades = sorted(set(d['Atividade'] for d in dados))
    cidades = sorted(set(d['Cidade'] for d in dados))

    # Calcula o valor máximo de cada atividade
    max_por_atividade = defaultdict(int)
    for d in dados:
        if d['total'] > max_por_atividade[d['Atividade']]:
            max_por_atividade[d['Atividade']] = d['total']

    # 🔹 Combina atividade + máximo em uma lista de dicionários
    atividades_info = [
        {'nome': atividade, 'max': max_por_atividade[atividade]}
        for atividade in atividades
    ]

    # - Estrutura para o gráfico

    # A partir das variáveis: incioHoje e data_fim, definimos início e fim do dia atual, com um exemplo de dados fictícios para 24 horas

    # Inicializa listas com 24 posições
    acessos = [0] * 25
    usuarios = [0] * 25
    cliente = [0] * 25
    medico = [0] * 25
    atendente = [0] * 25
    gerente = [0] * 25
    estagiario = [0] * 25

    hoje = datetime.now()
    data_fim = data_inicio + timedelta(days=1)

    # Acessos por hora
    acessos_por_hora = (
        Security_Logs.objects
        .filter(DtHr_Atividade__range=(data_inicio, data_fim))
        .annotate(hora=TruncHour('DtHr_Atividade'))
        .values('hora')
        .annotate(total=Count('id'))
    )

    for item in acessos_por_hora:
        if item['hora'] is not None:
            hora = item['hora'].hour
            acessos[hora] = item['total']

    # Acessos por hora
    cliente_por_hora = (
        Security_Logs.objects
        .filter(DtHr_Atividade__range=(data_inicio, data_fim), Perfil_User='Cliente')
        .annotate(hora=TruncHour('DtHr_Atividade', output_field=DateTimeField(), tzinfo=None))
        .values('hora')
        .annotate(total=Count('id'))
    )

    for item in cliente_por_hora:
        if item['hora'] is not None:
            hora = item['hora'].hour
            cliente[hora] = item['total']

    # Exemplo: filtrando por tipo de atividade
    usuarios_por_hora = (
        Security_Logs.objects
        .filter(DtHr_Atividade__range=(data_inicio, data_fim), Perfil_User='Atendente')
        .annotate(hora=TruncHour('DtHr_Atividade'))
        .values('hora')
        .annotate(total=Count('id'))
    )
    for item in usuarios_por_hora:
        hora = item['hora'].hour
        usuarios[hora] = item['total']

    medico_por_hora = (
        Security_Logs.objects
        .filter(DtHr_Atividade__range=(data_inicio, data_fim), Perfil_User='Médico')
        .annotate(hora=TruncHour('DtHr_Atividade'))
        .values('hora')
        .annotate(total=Count('id'))
    )
    for item in medico_por_hora:
        hora = item['hora'].hour
        medico[hora] = item['total']

    estagiario_por_hora = (
        Security_Logs.objects
        .filter(DtHr_Atividade__range=(data_inicio, data_fim), Perfil_User='Estagiário')
        .annotate(hora=TruncHour('DtHr_Atividade'))
        .values('hora')
        .annotate(total=Count('id'))
    )
    for item in estagiario_por_hora:
        hora = item['hora'].hour
        estagiario[hora] = item['total']

    gerente_por_hora = (
        Security_Logs.objects
        .filter(DtHr_Atividade__range=(data_inicio, data_fim), Perfil_User='Gerente')
        .annotate(hora=TruncHour('DtHr_Atividade', output_field=DateTimeField(), tzinfo=None))
        .values('hora')
        .annotate(total=Count('id'))
    )

    for item in gerente_por_hora:
        hora = item['hora'].hour
        gerente[hora] = item['total']

    atendente_por_hora = (
        Security_Logs.objects
        .filter(DtHr_Atividade__range=(data_inicio, data_fim), Perfil_User='Atendente')
        .annotate(hora=TruncHour('DtHr_Atividade'))
        .values('hora')
        .annotate(total=Count('id'))
    )
    for item in atendente_por_hora:
        hora = item['hora'].hour
        atendente[hora] = item['total']

    # ----------------------------------------------------

    # Monta estrutura para o gráfico radar
    series_data = []
    for cidade in cidades:
        valores = []
        for atividade in atividades:
            registro = next(
                (r for r in dados if r['Cidade'] == cidade and r['Atividade'] == atividade), None)
            valores.append(registro['total'] if registro else 0)
        series_data.append({'value': valores, 'name': cidade})

    # Monta estrutura para o gráfico pizza
    sries_dta_Atvddes = []
    for atividade in atividades:
        registro = next(
            (r for r in dados if r['Atividade'] == atividade), None)
        vlres_atvdde = registro['total'] if registro else 0
        sries_dta_Atvddes.append(
            {'atvddeValor': vlres_atvdde * 100, 'atvddeNome': atividade})

    # Envia ao template
    context = {
        'Rgstrs_Atvddes': sries_dta_Atvddes,
        'Rgstrs_Series': series_data,
        'Rgstrs_MaxAtvddes': [max_por_atividade[a] for a in atividades],
        'cGrp_Usuario': Get_cGrp_Usuario(request.user),
        'Rgstrs_Cddes': slct_Cidades,
        'Rgstrs_Logs': slct_Rgstrs,
        'diaAnoCorrente': hoje,

        'nTtldiaCorrente': nTtlHjeCorrente,
        'nTtlMesCorrente': nTtlMesCorrente,
        'nTtlAnoCorrente': nTtlAnoCorrente,


        'mesAnoCorrente': mesAnoCrrnte,
        'anoCorrente': anoCrrnte,

        # 'Rgstrs_MaxAtvddes': [max_por_atividade[a] for a in atividades],
        'Rgstrs_MaxAtvddes': nTtlRgstrsMaxAtvddes,

        'slct_Filtro': filtro,
        'slct_Periodo': info_Periodo,
        'slct_AntPrdo': info_AntPrdo,
        'slct_PrxPrdo': info_PrxPrdo,

        'slct_Acessos': acessos,
        'slct_Cliente': cliente,
        'slct_Medico': medico,
        'slct_Atendente': atendente,
        'slct_Gerente': gerente,
        'slct_Estagiario': estagiario,
        'Slct5UltmosRgstrosDeHoje': n5UltmosRgstrosDeHoje,
    }
    return render(request, 'dashboard-test.html', context)
# =======================================================================================================


# ====================================================================================================
# ----------------------------------------------------------------------------------------------------
@login_required(login_url='/usuarios/login/')
def fnct_security(request):

    filtro = request.GET.get('filtro', 'hoje')  # padrão "hoje"
    hoje = datetime.now().date()

    mes_extenso = hoje.strftime('%B').capitalize()  # exemplo: 'Setembro'
    mesAnoCrrnte = f"{mes_extenso}"

    anoCrrnte = f"{hoje.year}"

    # Define o início e o fim do dia atual
    incioHoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    data_fim = incioHoje + timedelta(days=1)

    # Conta o total de registros de hoje
    nTtlHjeCorrente = Security_Logs.objects.filter(
        DtHr_Atividade__range=(incioHoje, data_fim)).count()

    # Conta o Total de Usuários que realizaram acesso no mês atual
    # Início do mês corrente
    dtHoje = datetime.now()
    incioMes = dtHoje.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Retorna os últimos 5 registros de hoje
    incioDia = make_aware(datetime.combine(hoje, datetime.min.time()))
    fimDia = make_aware(datetime.combine(hoje, datetime.max.time()))

    agora = datetime.now()
    inicio = agora.replace(hour=0, minute=0, second=0, microsecond=0)
    fim = inicio + timedelta(days=1)

    incioDia = inicio.replace(tzinfo=None)
    fimDia = fim.replace(tzinfo=None)

    n5UltmosRgstrosDeHoje = (Security_Logs.objects.filter(DtHr_Atividade__range=(incioDia, fimDia), DtHr_Atividade__lt=now())
                             .order_by('-DtHr_Atividade')[:6]
                             )

    # Início do próximo mês
    if dtHoje.month == 12:
        fimMes = dtHoje.replace(year=dtHoje.year + 1, month=1,
                                day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        fimMes = dtHoje.replace(month=dtHoje.month + 1, day=1,
                                hour=0, minute=0, second=0, microsecond=0)

    # Consulta filtrando registros do mês corrente
    nTtlMesCorrente = Security_Logs.objects.filter(
        DtHr_Atividade__range=(incioMes, fimMes)).count()

    # Início do ano corrente
    incioAno = dtHoje.replace(month=1, day=1, hour=0,
                              minute=0, second=0, microsecond=0)

    # Início do próximo ano
    fimAno = dtHoje.replace(year=dtHoje.year + 1, month=1,
                            day=1, hour=0, minute=0, second=0, microsecond=0)

    # Consulta filtrando registros do ano corrente
    nTtlAnoCorrente = Security_Logs.objects.filter(
        DtHr_Atividade__range=(incioAno, fimAno)).count()

    if filtro == 'hoje':

        data_inicio = make_aware(datetime.combine(hoje, datetime.min.time())).replace(
            microsecond=0).astimezone(None).replace(tzinfo=None)
        data_fim = make_aware(datetime.combine(hoje, datetime.max.time())).replace(
            microsecond=0).astimezone(None).replace(tzinfo=None)

        info_Periodo = hoje
        info_PrxPrdo = make_aware(datetime(hoje.year, hoje.month, hoje.day+1))

        # Considerando que a data de hoje é 30 de Setembro de 2025
        # data_inicio = make_aware(datetime(2025, 9, 30, 0, 0, 0))
        # data_fim = make_aware(datetime(2025, 9, 30, 23, 59, 59))

        nTtlRgstrsMaxAtvddes = 25

    elif filtro == 'mes':
        # Início do mês
        data_inicio = make_aware(datetime.combine(datetime(hoje.year, hoje.month, 1), datetime.min.time())).replace(
            microsecond=0).astimezone(None).replace(tzinfo=None)

        # Último dia do mês
        if hoje.month == 12:
            proximo_mes = date(hoje.year + 1, 1, 1)
        else:
            proximo_mes = date(hoje.year, hoje.month + 1, 1)

        ultimo_dia_mes = proximo_mes - timedelta(days=1)
        data_fim_teorica = make_aware(datetime.combine(ultimo_dia_mes, datetime.max.time())).replace(
            microsecond=0).astimezone(None).replace(tzinfo=None)

        # Data atual (agora)
        agora = datetime.now().replace(microsecond=0)

        # Garante que data_fim não ultrapasse hoje
        data_fim = min(data_fim_teorica, agora)

        # obtém o nome do mês por extenso e o ano
        mes_extenso = hoje.strftime('%B').capitalize()  # exemplo: 'Setembro'
        info_Periodo = f"Mês: {mes_extenso}/{hoje.year}"

        mes_extenso = proximo_mes.strftime(
            '%B').capitalize()  # exemplo: 'Setembro'
        info_PrxPrdo = f"{mes_extenso}/{hoje.year}"

        nTtlRgstrsMaxAtvddes = 250

    elif filtro == 'ano':
        data_inicio = make_aware(datetime(hoje.year, 1, 1))
        data_fim = make_aware(datetime(hoje.year, 12, 31, 23, 59, 59))

        data_inicio = make_aware(datetime.combine(data_inicio, datetime.min.time())).replace(
            microsecond=0).astimezone(None).replace(tzinfo=None)
        data_fim = make_aware(datetime.combine(data_fim, datetime.max.time())).replace(
            microsecond=0).astimezone(None).replace(tzinfo=None)

        # obtém o ano
        info_Periodo = f"Ano: {hoje.year}"
        info_PrxPrdo = f"{hoje.year+1}"

        nTtlRgstrsMaxAtvddes = 750
    else:
        # padrão fallback
        data_inicio = data_fim = make_aware(datetime(2025, 9, 30))

    # Seleciona todos os registros de acordo com o periodo
    slct_Rgstrs = Security_Logs.objects.filter(
        DtHr_Atividade__range=(data_inicio, data_fim))

    # Define intervalo de hoje (00:00 até 23:59)
    agora = datetime.now()
    inicio = agora.replace(hour=0, minute=0, second=0, microsecond=0)
    fim = inicio + timedelta(days=1)

    inicio_naive = inicio.replace(tzinfo=None)
    fim_naive = fim.replace(tzinfo=None)

    # Consulta registros
    slct_Rgstrs = Security_Logs.objects.filter(
        DtHr_Atividade__range=(inicio_naive, fim_naive))

    # Seleção das Atividades por cidades. Usado no Gráfico tipo 'radar'.
    slct_Cidades = (
        Security_Logs.objects.filter(
            DtHr_Atividade__range=(data_inicio, data_fim))
        # Retorna só os nomes das cidades
        .values_list('Cidade', flat=True)
        .distinct()                        # Remove duplicadas
        # Ordena alfabeticamente
        .order_by('Cidade')
    )

    slct_Atividades = (
        Security_Logs.objects
        .filter(DtHr_Atividade__range=(data_inicio, data_fim))
        .values('Atividade')         # Agrupa por atividade
        .annotate(total=Count('id'))  # Conta quantos registros por atividade
        .order_by('Atividade')       # Ordena por nome (opcional)
    )

    # Filtra pelo período desejado
    dados = (
        Security_Logs.objects
        .filter(DtHr_Atividade__range=(data_inicio, data_fim))
        .values('Cidade', 'Atividade')
        .annotate(total=Count('id'))
    )

    dt_Incio_Radar = make_aware(datetime(hoje.year, hoje.month, 1))
    # último dia do mês
    if hoje.month == 12:
        proximo_mes = date(hoje.year + 1, 1, 1)
    else:
        proximo_mes = date(hoje.year, hoje.month + 1, 1)
    dt_fim_Radar = make_aware(datetime.combine(
        proximo_mes - timedelta(days=1), datetime.max.time())
    )

    dadosRadar = (
        Security_Logs.objects
        .filter(DtHr_Atividade__range=(dt_Incio_Radar, dt_fim_Radar))
        .values('Cidade', 'Atividade')
        .annotate(total=Count('id'))
    )

    # Cria listas
    atividades = sorted(set(d['Atividade'] for d in dados))
    cidades = sorted(set(d['Cidade'] for d in dados))

    # Calcula o valor máximo de cada atividade
    max_por_atividade = defaultdict(int)
    for d in dados:
        if d['total'] > max_por_atividade[d['Atividade']]:
            max_por_atividade[d['Atividade']] = d['total']

    # 🔹 Combina atividade + máximo em uma lista de dicionários
    atividades_info = [
        {'nome': atividade, 'max': max_por_atividade[atividade]}
        for atividade in atividades
    ]

    # - Estrutura para o gráfico

    # A partir das variáveis: incioHoje e data_fim, definimos início e fim do dia atual, com um exemplo de dados fictícios para 24 horas

    # Inicializa listas com 24 posições
    acessos = [0] * 25
    usuarios = [0] * 25
    cliente = [0] * 25
    medico = [0] * 25
    atendente = [0] * 25
    gerente = [0] * 25
    estagiario = [0] * 25

    hoje = datetime.now()
    data_fim = data_inicio + timedelta(days=1)

    # Acessos por hora
    acessos_por_hora = (
        Security_Logs.objects
        .filter(DtHr_Atividade__range=(data_inicio, data_fim))
        .annotate(hora=TruncHour('DtHr_Atividade'))
        .values('hora')
        .annotate(total=Count('id'))
    )

    for item in acessos_por_hora:
        if item['hora'] is not None:
            hora = item['hora'].hour
            acessos[hora] = item['total']

    # Acessos por hora
    cliente_por_hora = (
        Security_Logs.objects
        .filter(DtHr_Atividade__range=(data_inicio, data_fim), Perfil_User='Cliente')
        .annotate(hora=TruncHour('DtHr_Atividade', output_field=DateTimeField(), tzinfo=None))
        .values('hora')
        .annotate(total=Count('id'))
    )

    for item in cliente_por_hora:
        if item['hora'] is not None:
            hora = item['hora'].hour
            cliente[hora] = item['total']

    # Exemplo: filtrando por tipo de atividade
    usuarios_por_hora = (
        Security_Logs.objects
        .filter(DtHr_Atividade__range=(data_inicio, data_fim), Perfil_User='Atendente')
        .annotate(hora=TruncHour('DtHr_Atividade'))
        .values('hora')
        .annotate(total=Count('id'))
    )
    for item in usuarios_por_hora:
        hora = item['hora'].hour
        usuarios[hora] = item['total']

    medico_por_hora = (
        Security_Logs.objects
        .filter(DtHr_Atividade__range=(data_inicio, data_fim), Perfil_User='Médico')
        .annotate(hora=TruncHour('DtHr_Atividade'))
        .values('hora')
        .annotate(total=Count('id'))
    )
    for item in medico_por_hora:
        hora = item['hora'].hour
        medico[hora] = item['total']

    estagiario_por_hora = (
        Security_Logs.objects
        .filter(DtHr_Atividade__range=(data_inicio, data_fim), Perfil_User='Estagiário')
        .annotate(hora=TruncHour('DtHr_Atividade'))
        .values('hora')
        .annotate(total=Count('id'))
    )
    for item in estagiario_por_hora:
        hora = item['hora'].hour
        estagiario[hora] = item['total']

    gerente_por_hora = (
        Security_Logs.objects
        .filter(DtHr_Atividade__range=(data_inicio, data_fim), Perfil_User='Gerente')
        .annotate(hora=TruncHour('DtHr_Atividade', output_field=DateTimeField(), tzinfo=None))
        .values('hora')
        .annotate(total=Count('id'))
    )

    for item in gerente_por_hora:
        hora = item['hora'].hour
        gerente[hora] = item['total']

    atendente_por_hora = (
        Security_Logs.objects
        .filter(DtHr_Atividade__range=(data_inicio, data_fim), Perfil_User='Atendente')
        .annotate(hora=TruncHour('DtHr_Atividade'))
        .values('hora')
        .annotate(total=Count('id'))
    )
    for item in atendente_por_hora:
        hora = item['hora'].hour
        atendente[hora] = item['total']

    # ----------------------------------------------------

    # Monta estrutura para o gráfico radar
    series_data = []
    for cidade in cidades:
        valores = []
        for atividade in atividades:
            registro = next(
                (r for r in dados if r['Cidade'] == cidade and r['Atividade'] == atividade), None)
            valores.append(registro['total'] if registro else 0)
        series_data.append({'value': valores, 'name': cidade})

    # Monta estrutura para o gráfico pizza
    sries_dta_Atvddes = []
    for atividade in atividades:
        registro = next(
            (r for r in dados if r['Atividade'] == atividade), None)
        vlres_atvdde = registro['total'] if registro else 0
        sries_dta_Atvddes.append(
            {'atvddeValor': vlres_atvdde * 100, 'atvddeNome': atividade})

    # Envia ao template
    context = {
        'Rgstrs_Atvddes': sries_dta_Atvddes,
        'Rgstrs_Series': series_data,
        'Rgstrs_MaxAtvddes': [max_por_atividade[a] for a in atividades],
        'cGrp_Usuario': Get_cGrp_Usuario(request.user),
        'Rgstrs_Cddes': slct_Cidades,
        'Rgstrs_Logs': slct_Rgstrs,
        'diaAnoCorrente': hoje,

        'nTtldiaCorrente': nTtlHjeCorrente,
        'nTtlMesCorrente': nTtlMesCorrente,
        'nTtlAnoCorrente': nTtlAnoCorrente,


        'mesAnoCorrente': mesAnoCrrnte,
        'anoCorrente': anoCrrnte,

        # 'Rgstrs_MaxAtvddes': [max_por_atividade[a] for a in atividades],
        'Rgstrs_MaxAtvddes': nTtlRgstrsMaxAtvddes,

        'slct_Filtro': filtro,
        'slct_Periodo': info_Periodo,
        'slct_PrxPrdo': info_PrxPrdo,

        'slct_Acessos': acessos,
        'slct_Cliente': cliente,
        'slct_Medico': medico,
        'slct_Atendente': atendente,
        'slct_Gerente': gerente,
        'slct_Estagiario': estagiario,
        'Slct5UltmosRgstrosDeHoje': n5UltmosRgstrosDeHoje,
    }
    return render(request, 'dashboard.html', context)
# =======================================================================================================


# =======================================================================================================
@csrf_exempt  # ou use @require_POST com CSRF token
def relatorio_ajax(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        filtro = data.get('filtro')

        # lógica para tratar "Hoje", "Mes", "Ano"
        resultado = f"Você escolheu: {filtro}"


# =======================================================================================================


@login_required(login_url='/usuarios/login/')
def fnct_My_Profile(request):

    return render(request, 'My_Profile.html', {'cGrp_Usuario': Get_cGrp_Usuario(request.user)})


def fnct_scrty_sobre(request):

    return render(request, 'sobre.html', {'cGrp_Usuario': Get_cGrp_Usuario(request.user)})


def fnct_scrty_acessos(request):

    filtro = request.GET.get('filtro', 'hoje')  # padrão "hoje"
    hoje = datetime.now().date()

    mes_extenso = hoje.strftime('%B').capitalize()  # exemplo: 'Setembro'
    mesAnoCrrnte = f"{mes_extenso} {hoje.year}"

    anoCrrnte = f"{hoje.year}"

    # Define o início e o fim do dia atual
    incioHoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    data_fim = incioHoje + timedelta(days=1)

    # Conta o total de registros de hoje
    nTtlHjeCorrente = Security_Logs.objects.filter(
        DtHr_Atividade__range=(incioHoje, data_fim)).count()

    # Conta o Total de Usuários que realizaram acesso no mês atual
    # Início do mês corrente
    dtHoje = datetime.now()
    incioMes = dtHoje.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Retorna os últimos 5 registros de hoje
    incioDia = make_aware(datetime.combine(hoje, datetime.min.time()))
    fimDia = make_aware(datetime.combine(hoje, datetime.max.time()))

    agora = datetime.now()
    inicio = agora.replace(hour=0, minute=0, second=0, microsecond=0)
    fim = inicio + timedelta(days=1)

    incioDia = inicio.replace(tzinfo=None)
    fimDia = fim.replace(tzinfo=None)

    n5UltmosRgstrosDeHoje = (Security_Logs.objects.filter(DtHr_Atividade__range=(incioDia, fimDia), DtHr_Atividade__lt=now())
                             .order_by('-DtHr_Atividade')[:6]
                             )

    # Início do próximo mês
    if dtHoje.month == 12:
        fimMes = dtHoje.replace(year=dtHoje.year + 1, month=1,
                                day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        fimMes = dtHoje.replace(month=dtHoje.month + 1, day=1,
                                hour=0, minute=0, second=0, microsecond=0)

    # Consulta filtrando registros do mês corrente
    nTtlMesCorrente = Security_Logs.objects.filter(
        DtHr_Atividade__range=(incioMes, fimMes)).count()

    # Início do ano corrente
    incioAno = dtHoje.replace(month=1, day=1, hour=0,
                              minute=0, second=0, microsecond=0)

    # Início do próximo ano
    fimAno = dtHoje.replace(year=dtHoje.year + 1, month=1,
                            day=1, hour=0, minute=0, second=0, microsecond=0)

    # Consulta filtrando registros do ano corrente
    nTtlAnoCorrente = Security_Logs.objects.filter(
        DtHr_Atividade__range=(incioAno, fimAno)).count()

    if filtro == 'hoje':

        data_inicio = make_aware(datetime.combine(hoje, datetime.min.time())).replace(
            microsecond=0).astimezone(None).replace(tzinfo=None)
        data_fim = make_aware(datetime.combine(hoje, datetime.max.time())).replace(
            microsecond=0).astimezone(None).replace(tzinfo=None)

        info_Periodo = hoje
        info_AntPrdo = make_aware(datetime(hoje.year, hoje.month, 1-1))
        info_PrxPrdo = make_aware(datetime(hoje.year, hoje.month, 1+1))

        # Considerando que a data de hoje é 30 de Setembro de 2025
        # data_inicio = make_aware(datetime(2025, 9, 30, 0, 0, 0))
        # data_fim = make_aware(datetime(2025, 9, 30, 23, 59, 59))

        nTtlRgstrsMaxAtvddes = 25

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
        info_Periodo = f"Mês: {mes_extenso}/{hoje.year}"

        nTtlRgstrsMaxAtvddes = 250

    elif filtro == 'ano':
        data_inicio = make_aware(datetime(hoje.year, 1, 1))
        data_fim = make_aware(datetime(hoje.year, 12, 31, 23, 59, 59))

        # obtém o ano
        info_Periodo = f"Ano: {hoje.year}"

        nTtlRgstrsMaxAtvddes = 750
    else:
        # padrão fallback
        data_inicio = data_fim = make_aware(datetime(2025, 9, 30))

    # Seleciona todos os registros de acordo com o periodo
    slct_Rgstrs = Security_Logs.objects.filter(
        DtHr_Atividade__range=(data_inicio, data_fim))

    # Define intervalo de hoje (00:00 até 23:59)
    agora = datetime.now()
    inicio = agora.replace(hour=0, minute=0, second=0, microsecond=0)
    fim = inicio + timedelta(days=1)

    inicio_naive = inicio.replace(tzinfo=None)
    fim_naive = fim.replace(tzinfo=None)

    # Consulta registros
    slct_Rgstrs = Security_Logs.objects.filter(
        DtHr_Atividade__range=(inicio_naive, fim_naive))

    # Seleção das Atividades por cidades. Usado no Gráfico tipo 'radar'.
    slct_Cidades = (
        Security_Logs.objects.filter(
            DtHr_Atividade__range=(data_inicio, data_fim))
        # Retorna só os nomes das cidades
        .values_list('Cidade', flat=True)
        .distinct()                        # Remove duplicadas
        # Ordena alfabeticamente
        .order_by('Cidade')
    )

    slct_Atividades = (
        Security_Logs.objects
        .filter(DtHr_Atividade__range=(data_inicio, data_fim))
        .values('Atividade')         # Agrupa por atividade
        .annotate(total=Count('id'))  # Conta quantos registros por atividade
        .order_by('Atividade')       # Ordena por nome (opcional)
    )

    # Filtra pelo período desejado
    dados = (
        Security_Logs.objects
        .filter(DtHr_Atividade__range=(data_inicio, data_fim))
        .values('Cidade', 'Atividade')
        .annotate(total=Count('id'))
    )

    dt_Incio_Radar = make_aware(datetime(hoje.year, hoje.month, 1))
    # último dia do mês
    if hoje.month == 12:
        proximo_mes = date(hoje.year + 1, 1, 1)
    else:
        proximo_mes = date(hoje.year, hoje.month + 1, 1)
    dt_fim_Radar = make_aware(datetime.combine(
        proximo_mes - timedelta(days=1), datetime.max.time())
    )

    dadosRadar = (
        Security_Logs.objects
        .filter(DtHr_Atividade__range=(dt_Incio_Radar, dt_fim_Radar))
        .values('Cidade', 'Atividade')
        .annotate(total=Count('id'))
    )

    # Cria listas
    atividades = sorted(set(d['Atividade'] for d in dados))
    cidades = sorted(set(d['Cidade'] for d in dados))

    # Calcula o valor máximo de cada atividade
    max_por_atividade = defaultdict(int)
    for d in dados:
        if d['total'] > max_por_atividade[d['Atividade']]:
            max_por_atividade[d['Atividade']] = d['total']

    # 🔹 Combina atividade + máximo em uma lista de dicionários
    atividades_info = [
        {'nome': atividade, 'max': max_por_atividade[atividade]}
        for atividade in atividades
    ]

    # - Estrutura para o gráfico

    # A partir das variáveis: incioHoje e data_fim, definimos início e fim do dia atual, com um exemplo de dados fictícios para 24 horas

    # Inicializa listas com 24 posições
    acessos = [0] * 25
    usuarios = [0] * 25
    cliente = [0] * 25
    medico = [0] * 25
    atendente = [0] * 25
    gerente = [0] * 25
    estagiario = [0] * 25

    hoje = datetime.now()
    data_fim = data_inicio + timedelta(days=1)

    # Acessos por hora
    acessos_por_hora = (
        Security_Logs.objects
        .filter(DtHr_Atividade__range=(data_inicio, data_fim))
        .annotate(hora=TruncHour('DtHr_Atividade'))
        .values('hora')
        .annotate(total=Count('id'))
    )

    for item in acessos_por_hora:
        if item['hora'] is not None:
            hora = item['hora'].hour
            acessos[hora] = item['total']

    # Acessos por hora
    cliente_por_hora = (
        Security_Logs.objects
        .filter(DtHr_Atividade__range=(data_inicio, data_fim), Perfil_User='Cliente')
        .annotate(hora=TruncHour('DtHr_Atividade', output_field=DateTimeField(), tzinfo=None))
        .values('hora')
        .annotate(total=Count('id'))
    )

    for item in cliente_por_hora:
        if item['hora'] is not None:
            hora = item['hora'].hour
            cliente[hora] = item['total']

    # Exemplo: filtrando por tipo de atividade
    usuarios_por_hora = (
        Security_Logs.objects
        .filter(DtHr_Atividade__range=(data_inicio, data_fim), Perfil_User='Atendente')
        .annotate(hora=TruncHour('DtHr_Atividade'))
        .values('hora')
        .annotate(total=Count('id'))
    )
    for item in usuarios_por_hora:
        hora = item['hora'].hour
        usuarios[hora] = item['total']

    medico_por_hora = (
        Security_Logs.objects
        .filter(DtHr_Atividade__range=(data_inicio, data_fim), Perfil_User='Médico')
        .annotate(hora=TruncHour('DtHr_Atividade'))
        .values('hora')
        .annotate(total=Count('id'))
    )
    for item in medico_por_hora:
        hora = item['hora'].hour
        medico[hora] = item['total']

    estagiario_por_hora = (
        Security_Logs.objects
        .filter(DtHr_Atividade__range=(data_inicio, data_fim), Perfil_User='Estagiário')
        .annotate(hora=TruncHour('DtHr_Atividade'))
        .values('hora')
        .annotate(total=Count('id'))
    )
    for item in estagiario_por_hora:
        hora = item['hora'].hour
        estagiario[hora] = item['total']

    gerente_por_hora = (
        Security_Logs.objects
        .filter(DtHr_Atividade__range=(data_inicio, data_fim), Perfil_User='Gerente')
        .annotate(hora=TruncHour('DtHr_Atividade', output_field=DateTimeField(), tzinfo=None))
        .values('hora')
        .annotate(total=Count('id'))
    )

    for item in gerente_por_hora:
        hora = item['hora'].hour
        gerente[hora] = item['total']

    atendente_por_hora = (
        Security_Logs.objects
        .filter(DtHr_Atividade__range=(data_inicio, data_fim), Perfil_User='Atendente')
        .annotate(hora=TruncHour('DtHr_Atividade'))
        .values('hora')
        .annotate(total=Count('id'))
    )
    for item in atendente_por_hora:
        hora = item['hora'].hour
        atendente[hora] = item['total']

    # ----------------------------------------------------

    # Monta estrutura para o gráfico radar
    series_data = []
    for cidade in cidades:
        valores = []
        for atividade in atividades:
            registro = next(
                (r for r in dados if r['Cidade'] == cidade and r['Atividade'] == atividade), None)
            valores.append(registro['total'] if registro else 0)
        series_data.append({'value': valores, 'name': cidade})

    # Monta estrutura para o gráfico pizza
    sries_dta_Atvddes = []
    for atividade in atividades:
        registro = next(
            (r for r in dados if r['Atividade'] == atividade), None)
        vlres_atvdde = registro['total'] if registro else 0
        sries_dta_Atvddes.append(
            {'atvddeValor': vlres_atvdde * 100, 'atvddeNome': atividade})

    # Envia ao template
    context = {
        'Rgstrs_Atvddes': sries_dta_Atvddes,
        'Rgstrs_Series': series_data,
        'Rgstrs_MaxAtvddes': [max_por_atividade[a] for a in atividades],
        'cGrp_Usuario': Get_cGrp_Usuario(request.user),
        'Rgstrs_Cddes': slct_Cidades,
        'Rgstrs_Logs': slct_Rgstrs,
        'diaAnoCorrente': hoje,

        'nTtldiaCorrente': nTtlHjeCorrente,
        'nTtlMesCorrente': nTtlMesCorrente,
        'nTtlAnoCorrente': nTtlAnoCorrente,


        'mesAnoCorrente': mesAnoCrrnte,
        'anoCorrente': anoCrrnte,

        # 'Rgstrs_MaxAtvddes': [max_por_atividade[a] for a in atividades],
        'Rgstrs_MaxAtvddes': nTtlRgstrsMaxAtvddes,

        'slct_Filtro': filtro,
        'slct_Periodo': info_Periodo,
        'slct_AntPrdo': info_AntPrdo,
        'slct_PrxPrdo': info_PrxPrdo,

        'slct_Acessos': acessos,
        'slct_Cliente': cliente,
        'slct_Medico': medico,
        'slct_Atendente': atendente,
        'slct_Gerente': gerente,
        'slct_Estagiario': estagiario,
        'Slct5UltmosRgstrosDeHoje': n5UltmosRgstrosDeHoje,


    }
    return render(request, 'acessos.html', context)


# =======================================================================================================
# *******************************************************************************************************
# =======================================================================================================
# Atualiza o gráfico de Relatórios
def gerar_dados(request):
    if request.method == "GET":
        filtro = request.GET.get('filtro', 'hoje').lower()
    elif request.method == "POST":
        filtro = request.POST.get('filtro', 'hoje').lower()
    else:
        filtro = 'hoje'

    slct_dt = datetime.now().date()
    if request.method == "GET":
        slct_dt_D = request.GET.get('dt_De', slct_dt)
        slct_dt_A = request.GET.get('dt_A', 'hoje')
    elif request.method == "POST":
        slct_dt_D = request.POST.get('dt_De', slct_dt)
        slct_dt_A = request.POST.get('dt_A', 'hoje')

    hoje = slct_dt_D

    mes_extenso = hoje.strftime('%B').capitalize()  # exemplo: 'Setembro'
    mesAnoCrrnte = f"{mes_extenso}"

    anoCrrnte = f"{hoje.year}"

    # Define o início e o fim do dia atual
    incioHoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    data_fim = incioHoje + timedelta(days=1)

    # Conta o total de registros de hoje
    nTtlHjeCorrente = Security_Logs.objects.filter(
        DtHr_Atividade__range=(incioHoje, data_fim)).count()

    # Conta o Total de Usuários que realizaram acesso no mês atual
    # Início do mês corrente
    dtHoje = datetime.now()
    incioMes = dtHoje.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Retorna os últimos 5 registros de hoje
    incioDia = make_aware(datetime.combine(hoje, datetime.min.time()))
    fimDia = make_aware(datetime.combine(hoje, datetime.max.time()))

    agora = datetime.now()
    inicio = agora.replace(hour=0, minute=0, second=0, microsecond=0)
    fim = inicio + timedelta(days=1)

    incioDia = inicio.replace(tzinfo=None)
    fimDia = fim.replace(tzinfo=None)

    n5UltmosRgstrosDeHoje = (Security_Logs.objects.filter(DtHr_Atividade__range=(incioDia, fimDia), DtHr_Atividade__lt=now())
                             .order_by('-DtHr_Atividade')[:6]
                             )

    # Início do próximo mês
    if dtHoje.month == 12:
        fimMes = dtHoje.replace(year=dtHoje.year + 1, month=1,
                                day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        fimMes = dtHoje.replace(month=dtHoje.month + 1, day=1,
                                hour=0, minute=0, second=0, microsecond=0)

    # Consulta filtrando registros do mês corrente
    nTtlMesCorrente = Security_Logs.objects.filter(
        DtHr_Atividade__range=(incioMes, fimMes)).count()

    # Início do ano corrente
    incioAno = dtHoje.replace(month=1, day=1, hour=0,
                              minute=0, second=0, microsecond=0)

    # Início do próximo ano
    fimAno = dtHoje.replace(year=dtHoje.year + 1, month=1,
                            day=1, hour=0, minute=0, second=0, microsecond=0)

    # Consulta filtrando registros do ano corrente
    nTtlAnoCorrente = Security_Logs.objects.filter(
        DtHr_Atividade__range=(incioAno, fimAno)).count()

    if filtro == 'hoje':
        # Inicializa listas com 24 posições para horas
        acessos = [0] * 25
        usuarios = [0] * 25
        cliente = [0] * 25
        medico = [0] * 25
        atendente = [0] * 25
        gerente = [0] * 25
        estagiario = [0] * 25

        data_inicio = make_aware(datetime.combine(hoje, datetime.min.time())).replace(
            microsecond=0).astimezone(None).replace(tzinfo=None)
        data_fim = make_aware(datetime.combine(hoje, datetime.max.time())).replace(
            microsecond=0).astimezone(None).replace(tzinfo=None)

        info_Periodo = hoje
        info_PrxPrdo = make_aware(datetime(hoje.year, hoje.month, hoje.day+1))

        # Considerando que a data de hoje é 30 de Setembro de 2025
        # data_inicio = make_aware(datetime(2025, 9, 30, 0, 0, 0))
        # data_fim = make_aware(datetime(2025, 9, 30, 23, 59, 59))

        nTtlRgstrsMaxAtvddes = 25

    elif filtro == 'mes':
        # Inicializa listas com 31 posições no total de 31 dias no máximo no mês.
        acessos = [0] * nTtlMesCorrente
        usuarios = [0] * nTtlMesCorrente
        cliente = [0] * nTtlMesCorrente
        medico = [0] * nTtlMesCorrente
        atendente = [0] * nTtlMesCorrente
        gerente = [0] * nTtlMesCorrente
        estagiario = [0] * nTtlMesCorrente

        data_inicio = make_aware(datetime(hoje.year, hoje.month, 1))

        # último dia do mês
        if hoje.month == 12:
            proximo_mes = date(hoje.year + 1, 1, 1)
        else:
            proximo_mes = date(hoje.year, hoje.month + 1, 1)

        data_fim = make_aware(datetime.combine(
            proximo_mes - timedelta(days=1), datetime.max.time()))

        # Garante que não ultrapasse o momento atual
        agora = make_aware(datetime.now())
        if data_fim > agora:
            data_fim = agora

        data_inicio = make_aware(datetime.combine(data_inicio, datetime.min.time())).replace(
            microsecond=0).astimezone(None).replace(tzinfo=None)
        data_fim = make_aware(datetime.combine(data_fim, datetime.max.time())).replace(
            microsecond=0).astimezone(None).replace(tzinfo=None)

        # obtém o nome do mês por extenso e o ano
        mes_extenso = hoje.strftime('%B').capitalize()  # exemplo: 'Setembro'
        info_Periodo = f"Mês: {mes_extenso}/{hoje.year}"

        mes_extenso = proximo_mes.strftime(
            '%B').capitalize()  # exemplo: 'Setembro'
        info_PrxPrdo = f"{mes_extenso}/{hoje.year}"

        nTtlRgstrsMaxAtvddes = 250

    elif filtro == 'ano':
        acessos = [0] * 13
        usuarios = [0] * 13
        cliente = [0] * 13
        medico = [0] * 13
        atendente = [0] * 13
        gerente = [0] * 13
        estagiario = [0] * 13

        data_inicio = make_aware(datetime(hoje.year, 1, 1))
        data_fim = make_aware(datetime(hoje.year, 12, 31, 23, 59, 59))

        data_inicio = make_aware(datetime.combine(data_inicio, datetime.min.time())).replace(
            microsecond=0).astimezone(None).replace(tzinfo=None)
        data_fim = make_aware(datetime.combine(data_fim, datetime.max.time())).replace(
            microsecond=0).astimezone(None).replace(tzinfo=None)

        # obtém o ano
        info_Periodo = f"Ano: {hoje.year}"
        info_PrxPrdo = f"{hoje.year+1}"

        nTtlRgstrsMaxAtvddes = 450
    else:
        # padrão fallback
        data_inicio = data_fim = make_aware(datetime(2025, 9, 30))

    # Seleciona todos os registros de acordo com o periodo
    slct_Rgstrs = Security_Logs.objects.filter(
        DtHr_Atividade__range=(data_inicio, data_fim))

    # Define intervalo de hoje (00:00 até 23:59)
    agora = datetime.now()
    inicio = agora.replace(hour=0, minute=0, second=0, microsecond=0)
    fim = inicio + timedelta(days=1)

    inicio_naive = inicio.replace(tzinfo=None)
    fim_naive = fim.replace(tzinfo=None)

    # Consulta registros
    slct_Rgstrs = Security_Logs.objects.filter(
        DtHr_Atividade__range=(inicio_naive, fim_naive))

    # Seleção das Atividades por cidades. Usado no Gráfico tipo 'radar'.
    slct_Cidades = (
        Security_Logs.objects.filter(
            DtHr_Atividade__range=(data_inicio, data_fim))
        # Retorna só os nomes das cidades
        .values_list('Cidade', flat=True)
        .distinct()                        # Remove duplicadas
        # Ordena alfabeticamente
        .order_by('Cidade')
    )

    slct_Atividades = (
        Security_Logs.objects
        .filter(DtHr_Atividade__range=(data_inicio, data_fim))
        .values('Atividade')         # Agrupa por atividade
        .annotate(total=Count('id'))  # Conta quantos registros por atividade
        .order_by('Atividade')       # Ordena por nome (opcional)
    )

    # Filtra pelo período desejado
    dados = (
        Security_Logs.objects
        .filter(DtHr_Atividade__range=(data_inicio, data_fim))
        .values('Cidade', 'Atividade')
        .annotate(total=Count('id'))
    )

    dt_Incio_Radar = make_aware(datetime(hoje.year, hoje.month, 1))
    # último dia do mês
    if hoje.month == 12:
        proximo_mes = date(hoje.year + 1, 1, 1)
    else:
        proximo_mes = date(hoje.year, hoje.month + 1, 1)
    dt_fim_Radar = make_aware(datetime.combine(
        proximo_mes - timedelta(days=1), datetime.max.time())
    )

    dadosRadar = (
        Security_Logs.objects
        .filter(DtHr_Atividade__range=(dt_Incio_Radar, dt_fim_Radar))
        .values('Cidade', 'Atividade')
        .annotate(total=Count('id'))
    )

    # Cria listas
    atividades = sorted(set(d['Atividade'] for d in dados))
    cidades = sorted(set(d['Cidade'] for d in dados))

    # Calcula o valor máximo de cada atividade
    max_por_atividade = defaultdict(int)
    for d in dados:
        if d['total'] > max_por_atividade[d['Atividade']]:
            max_por_atividade[d['Atividade']] = d['total']

    # 🔹 Combina atividade + máximo em uma lista de dicionários
    atividades_info = [
        {'nome': atividade, 'max': max_por_atividade[atividade]}
        for atividade in atividades
    ]

    # - Estrutura para o gráfico

    # A partir das variáveis: incioHoje e data_fim, definimos início e fim do dia atual, com um exemplo de dados fictícios para 24 horas

    hoje = datetime.now()
    data_fim = data_inicio + timedelta(days=1)

    if filtro == 'hoje':
        # Acessos por hora
        acessos_por_hora = (
            Security_Logs.objects
            .filter(DtHr_Atividade__range=(data_inicio, data_fim))
            .annotate(hora=TruncHour('DtHr_Atividade'))
            .values('hora')
            .annotate(total=Count('id'))
        )
        for item in acessos_por_hora:
            if item['hora'] is not None:
                hora = item['hora'].hour
                acessos[hora] = item['total']

        # Acessos por hora
        cliente_por_hora = (
            Security_Logs.objects
            .filter(DtHr_Atividade__range=(data_inicio, data_fim), Perfil_User='Cliente')
            .annotate(hora=TruncHour('DtHr_Atividade', output_field=DateTimeField(), tzinfo=None))
            .values('hora')
            .annotate(total=Count('id'))
        )
        for item in cliente_por_hora:
            if item['hora'] is not None:
                hora = item['hora'].hour
                cliente[hora] = item['total']

        medico_por_hora = (
            Security_Logs.objects
            .filter(DtHr_Atividade__range=(data_inicio, data_fim), Perfil_User='Médico')
            .annotate(hora=TruncHour('DtHr_Atividade'))
            .values('hora')
            .annotate(total=Count('id'))
        )
        for item in medico_por_hora:
            hora = item['hora'].hour
            medico[hora] = item['total']

        atendente_por_hora = (
            Security_Logs.objects
            .filter(DtHr_Atividade__range=(data_inicio, data_fim), Perfil_User='Atendente')
            .annotate(hora=TruncHour('DtHr_Atividade'))
            .values('hora')
            .annotate(total=Count('id'))
        )
        for item in atendente_por_hora:
            hora = item['hora'].hour
            atendente[hora] = item['total']

        gerente_por_hora = (
            Security_Logs.objects
            .filter(DtHr_Atividade__range=(data_inicio, data_fim), Perfil_User='Gerente')
            .annotate(hora=TruncHour('DtHr_Atividade', output_field=DateTimeField(), tzinfo=None))
            .values('hora')
            .annotate(total=Count('id'))
        )
        for item in gerente_por_hora:
            hora = item['hora'].hour
            gerente[hora] = item['total']

        estagiario_por_hora = (
            Security_Logs.objects
            .filter(DtHr_Atividade__range=(data_inicio, data_fim), Perfil_User='Estagiário')
            .annotate(hora=TruncHour('DtHr_Atividade'))
            .values('hora')
            .annotate(total=Count('id'))
        )
        for item in estagiario_por_hora:
            hora = item['hora'].hour
            estagiario[hora] = item['total']

    # ----------------------------------------------------------------------------------------------Finaliza Dia
    # Se filtro for igual "Mês"--------------------------------------------------------------------------------
    if filtro == 'mes':
        # Para MÊS: acessos por dia
        acessos_por_dia = (
            Security_Logs.objects
            .filter(DtHr_Atividade__range=(data_inicio, data_fim))
            .annotate(dia=TruncDay('DtHr_Atividade'))
            .values('dia')
            .annotate(total=Count('id'))
        )
        for item in acessos_por_dia:
            if item['dia'] is not None:
                # ou item['dia'].strftime('%d') para string
                dia = item['dia'].day
                acessos[dia - 1] = item['total']  # índice começa em 0

        # Para perfis específicos (Cliente, Médico etc.)
        cliente_por_dia = (
            Security_Logs.objects
            .filter(DtHr_Atividade__range=(data_inicio, data_fim), Perfil_User='Cliente')
            .annotate(dia=TruncDay('DtHr_Atividade'))
            .values('dia')
            .annotate(total=Count('id'))
        )
        for item in cliente_por_dia:
            dia = item['dia'].day
            cliente[dia - 1] = item['total']

        medico_por_dia = (
            Security_Logs.objects
            .filter(DtHr_Atividade__range=(data_inicio, data_fim), Perfil_User='Médico')
            .annotate(dia=TruncDay('DtHr_Atividade'))
            .values('dia')
            .annotate(total=Count('id'))
        )
        for item in medico_por_dia:
            dia = item['dia'].day
            medico[dia] = item['total']

        atendente_por_dia = (
            Security_Logs.objects
            .filter(DtHr_Atividade__range=(data_inicio, data_fim), Perfil_User='Atendente')
            .annotate(dia=TruncDay('DtHr_Atividade'))
            .values('dia')
            .annotate(total=Count('id'))
        )
        for item in atendente_por_dia:
            dia = item['dia'].day
            atendente[dia] = item['total']

        gerente_por_dia = (
            Security_Logs.objects
            .filter(DtHr_Atividade__range=(data_inicio, data_fim), Perfil_User='Gerente')
            .annotate(dia=TruncDay('DtHr_Atividade', output_field=DateTimeField(), tzinfo=None))
            .values('dia')
            .annotate(total=Count('id'))
        )
        for item in gerente_por_dia:
            dia = item['dia'].day
            gerente[dia] = item['total']

        estagiario_por_dia = (
            Security_Logs.objects
            .filter(DtHr_Atividade__range=(data_inicio, data_fim), Perfil_User='Estagiário')
            .annotate(dia=TruncDay('DtHr_Atividade'))
            .values('dia')
            .annotate(total=Count('id'))
        )
        for item in estagiario_por_dia:
            dia = item['dia'].day
            estagiario[dia] = item['total']

    # ----------------------------------------------------------------------------------------------Finaliza Mes
    # Se filtro for igual "Anoa"--------------------------------------------------------------------------------
    if filtro == 'ano':
        acessos_por_mes = (
            Security_Logs.objects
            .filter(DtHr_Atividade__range=(data_inicio, data_fim))
            .annotate(mes=TruncMonth('DtHr_Atividade'))
            .values('mes')
            .annotate(total=Count('id'))
        )

        for item in acessos_por_mes:
            if item['mes'] is not None:
                mes = item['mes'].month
                acessos[mes - 1] = item['total']

    # Exemplo: filtrando por tipo de atividade
    usuarios_por_hora = (
        Security_Logs.objects
        .filter(DtHr_Atividade__range=(data_inicio, data_fim), Perfil_User='Atendente')
        .annotate(hora=TruncHour('DtHr_Atividade'))
        .values('hora')
        .annotate(total=Count('id'))
    )
    for item in usuarios_por_hora:
        hora = item['hora'].hour
        usuarios[hora] = item['total']

    # ----------------------------------------------------

    # Monta estrutura para o gráfico radar
    series_data = []
    for cidade in cidades:
        valores = []
        for atividade in atividades:
            registro = next(
                (r for r in dados if r['Cidade'] == cidade and r['Atividade'] == atividade), None)
            valores.append(registro['total'] if registro else 0)
        series_data.append({'value': valores, 'name': cidade})

    # Monta estrutura para o gráfico pizza
    sries_dta_Atvddes = []
    for atividade in atividades:
        registro = next(
            (r for r in dados if r['Atividade'] == atividade), None)
        vlres_atvdde = registro['total'] if registro else 0
        sries_dta_Atvddes.append(
            {'atvddeValor': vlres_atvdde * 100, 'atvddeNome': atividade})

    # Envia ao template
    context = {
        'Rgstrs_Atvddes': sries_dta_Atvddes,
        'Rgstrs_Series': series_data,
        'Rgstrs_MaxAtvddes': [max_por_atividade[a] for a in atividades],
        'cGrp_Usuario': Get_cGrp_Usuario(request.user),
        'Rgstrs_Cddes': slct_Cidades,
        'Rgstrs_Logs': slct_Rgstrs,
        'diaAnoCorrente': hoje,

        'nTtldiaCorrente': nTtlHjeCorrente,
        'nTtlMesCorrente': nTtlMesCorrente,
        'nTtlAnoCorrente': nTtlAnoCorrente,


        'mesAnoCorrente': mesAnoCrrnte,
        'anoCorrente': anoCrrnte,

        # 'Rgstrs_MaxAtvddes': [max_por_atividade[a] for a in atividades],
        'Rgstrs_MaxAtvddes': nTtlRgstrsMaxAtvddes,

        'slct_Periodo': info_Periodo,
        'slct_PrxPrdo': info_PrxPrdo,

        'slct_Acessos': acessos,
        'slct_Cliente': cliente,
        'slct_Medico': medico,
        'slct_Atendente': atendente,
        'slct_Gerente': gerente,
        'slct_Estagiario': estagiario,
        'Slct5UltmosRgstrosDeHoje': n5UltmosRgstrosDeHoje,
    }

    # return {
    #    context

    return {
        'periodo': filtro,
        'acessos': acessos,
        'cliente': cliente,
        'medico': medico,
        'atendente': atendente,
        'gerente': gerente,
        'estagiario': estagiario,
        'Rgstrs_Series': series_data,
        # 'Rgstrs_MaxAtvddes': [max_por_atividade[a] for a in atividades],
        # 'cGrp_Usuario': Get_cGrp_Usuario(request.user),
        # 'Rgstrs_Cddes': slct_Cidades,
        # 'Rgstrs_Logs': slct_Rgstrs,
        #        'diaAnoCorrente': hoje,

        #        'nTtldiaCorrente': nTtlHjeCorrente,
        #        'nTtlMesCorrente': nTtlMesCorrente,
        #        'nTtlAnoCorrente': nTtlAnoCorrente,


        #        'mesAnoCorrente': mesAnoCrrnte,
        #        'anoCorrente': anoCrrnte,

        # 'Rgstrs_MaxAtvddes': [max_por_atividade[a] for a in atividades],
        #       'Rgstrs_MaxAtvddes': nTtlRgstrsMaxAtvddes,

        #        'slct_Periodo': info_Periodo,
        #        'slct_AntPrdo': info_AntPrdo,
        #        'slct_PrxPrdo': info_PrxPrdo,

        'slct_Acessos': acessos,
        'slct_Cliente': cliente,
        'slct_Medico': medico,
        'slct_Atendente': atendente,
        'slct_Gerente': gerente,
        'slct_Estagiario': estagiario,
        #        'Slct5UltmosRgstrosDeHoje': n5UltmosRgstrosDeHoje,

    }
# --------------------------------------------------------------------------------------------------------
# Finaliza: gerar_dados(request) atualiza o gráfico de Relatórios
# =======================================================================================================
# *******************************************************************************************************
# =======================================================================================================


def grafico_dados(request):
    hoje = datetime.now().date()
    if request.method == 'GET':
        periodo = request.GET.get('filtro', 'hoje').lower()

        # Captura dt_De
        dt_De_str = request.GET.get('dt_De')
        try:
            dt_De = datetime.strptime(
                dt_De_str, '%Y-%m-%d').date() if dt_De_str else hoje
        except ValueError:
            dt_De = hoje

        # Captura dt_A, ou define como dt_De + 1 dia
        dt_A_str = request.GET.get('dt_A')
        try:
            dt_A = datetime.strptime(
                dt_A_str, '%Y-%m-%d').date() if dt_A_str else dt_De + timedelta(days=1)
        except ValueError:
            dt_A = dt_De + timedelta(days=1)

    elif request.method == 'POST':
        # Captura dt_De
        dt_De_str = request.GET.get('dt_De')
        try:
            dt_De = datetime.strptime(
                dt_De_str, '%Y-%m-%d').date() if dt_De_str else hoje
        except ValueError:
            dt_De = hoje

        # Captura dt_A, ou define como dt_De + 1 dia
        dt_A_str = request.GET.get('dt_A')
        try:
            dt_A = datetime.strptime(
                dt_A_str, '%Y-%m-%d').date() if dt_A_str else dt_De + timedelta(days=1)
        except ValueError:
            dt_A = dt_De + timedelta(days=1)

        try:
            periodo = request.POST.get('filtro', 'hoje').lower()
        except Exception as e:
            print('erro')
            periodo = 'hoje'
    else:
        periodo = 'hoje'

    # Adiciona o parâmetro 'filtro' à request para que gerar_dados use
    request.GET = request.GET.copy()
    request.GET['filtro'] = periodo
    request.GET['dt_De'] = dt_De
    request.GET['dt_A'] = dt_A

    dados = gerar_dados(request)
    return JsonResponse(dados)
