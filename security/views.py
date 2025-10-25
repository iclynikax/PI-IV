from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from usuarios.models import Get_cGrp_Usuario


@login_required(login_url='/usuarios/login/')
def fnct_security(request):

    return render(request, 'dashboard.html', {'cGrp_Usuario': Get_cGrp_Usuario(request.user)})


@login_required(login_url='/usuarios/login/')
def fnct_My_Profile(request):

    return render(request, 'My_Profile.html', {'cGrp_Usuario': Get_cGrp_Usuario(request.user)})


def fnct_scrty_sobre(request):

    return render(request, 'sobre.html', {'cGrp_Usuario': Get_cGrp_Usuario(request.user)})
