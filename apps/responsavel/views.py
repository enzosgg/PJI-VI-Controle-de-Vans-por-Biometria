import json
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import F, Max, Q
from django.http import JsonResponse, Http404
from django.middleware.csrf import get_token
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST, require_GET

from apps.cerebro.models import (
    Aluno, Biometria, Escola, Checkin_Checkout, Rotas, AVATARES, AVATAR_EMOJI
)
from apps.cerebro.palm_recognition import MAO_PARA_LADO

CAMPO_POR_MAO = {'direita': 'template_direita', 'esquerda': 'template_esquerda'}


def _eh_responsavel(user):
    return hasattr(user, 'responsavel')

def _rota_do_aluno(aluno):

    sessao = _sessao_ativa_do_aluno(aluno)
    if sessao:
        return sessao, True
    return None, False


@login_required
@user_passes_test(_eh_responsavel, login_url='dashboard')
def responsavel(request):
    alunos = list(request.user.responsavel.alunos.select_related('rota', 'biometria', 'escola'))
    for aluno in alunos:
        aluno.rota_info, aluno.rota_ativa = _rota_do_aluno(aluno)

    avatares = [{'chave': c, 'emoji': e, 'nome': n} for c, e, n in AVATARES]

    return render(request, 'responsavel.html', {
        'alunos': alunos,
        'avatares': avatares,
    })

@login_required
@user_passes_test(_eh_responsavel, login_url='dashboard')
def cadastrar_biometria(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id, responsavel=request.user.responsavel)
    biometria = Biometria.objects.filter(aluno=aluno).first()

    return render(request, 'cadastrar_biometria.html', {
        'aluno': aluno,
        'tem_direita': bool(biometria and biometria.template_direita),
        'tem_esquerda': bool(biometria and biometria.template_esquerda),
    })


@login_required
@require_POST
def api_salvar_biometria(request):
    try:
        dados = json.loads(request.body)
        aluno_id = dados.get('aluno_id')
        template = dados.get('template')
        mao = dados.get('mao')

        if not aluno_id or not template or mao not in CAMPO_POR_MAO:
            return JsonResponse({'success': False, 'error': 'Dados incompletos.'})

        if not isinstance(template, str):
            template = json.dumps(template)

        try:
            lado = json.loads(template).get('lado_da_mao')
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Template inválido.'})
        if lado != MAO_PARA_LADO[mao]:
            return JsonResponse({'success': False,
                                 'error': 'O template não corresponde à mão informada.'})

        aluno = get_object_or_404(Aluno, id=aluno_id, responsavel=request.user.responsavel)

        biometria, _ = Biometria.objects.get_or_create(aluno=aluno)
        setattr(biometria, CAMPO_POR_MAO[mao], template)
        biometria.save()

        return JsonResponse({'success': True, 'completa': biometria.completa})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_POST
def api_salvar_avatar(request):
    try:
        dados = json.loads(request.body)
        avatar = dados.get('avatar')

        if avatar not in AVATAR_EMOJI:
            return JsonResponse({'success': False, 'error': 'Avatar inválido.'}, status=400)

        aluno = get_object_or_404(Aluno, id=dados.get('aluno_id'), responsavel__user=request.user)
        aluno.avatar = avatar
        aluno.save(update_fields=['avatar'])

        return JsonResponse({'success': True, 'avatar': avatar, 'emoji': AVATAR_EMOJI[avatar]})
    except Http404:
        return JsonResponse({'success': False, 'error': 'Aluno não encontrado.'}, status=404)
    except (ValueError, TypeError):
        return JsonResponse({'success': False, 'error': 'Dados inválidos.'}, status=400)

def _sessao_ativa_do_aluno(aluno):

    filtro = Q(registros__aluno=aluno)
    if aluno.rota_id:
        filtro |= Q(pk=aluno.rota_id) | Q(nome_rota=aluno.rota.nome_rota)

    return (
        Rotas.objects
        .filter(status='ATIVA')
        .filter(filtro)
        .annotate(ultima_posicao=Max('posicoes__registrado_em'))
        .order_by(F('ultima_posicao').desc(nulls_last=True), '-data_inicio')
        .first()
    )


@login_required
@user_passes_test(_eh_responsavel, login_url='dashboard')
def mapa_aluno(request, aluno_id):
    aluno = get_object_or_404(
        Aluno.objects.select_related('escola'),
        id=aluno_id,
        responsavel=request.user.responsavel
    )

    casa = None
    if aluno.casa_definida:
        casa = {
            'lat': aluno.casa_latitude,
            'lng': aluno.casa_longitude,
            'endereco': aluno.endereco,
        }

    escola = None
    if aluno.escola_id:
        escola = {
            'nome': aluno.escola.nome,
            'lat': aluno.escola.latitude,
            'lng': aluno.escola.longitude,
            'endereco': aluno.escola.endereco,
        }

    config = {
        'alunoId': aluno.id,
        'alunoNome': aluno.nome,
        'avatar': aluno.avatar_emoji,
        'csrf': get_token(request),
        'casa': casa,
        'escola': escola,
        'urls': {
            'posicao': reverse('api_posicao_van', args=[aluno.id]),
            'salvarLocal': reverse('api_salvar_local'),
        },
    }

    return render(request, 'mapa_aluno.html', {
        'aluno': aluno,
        'config': config,
        'abrir_painel': not (casa and escola),
    })


@login_required
@require_GET
def api_posicao_van(request, aluno_id):

    aluno = get_object_or_404(
        Aluno.objects.select_related('escola', 'rota'),
        id=aluno_id,
        responsavel__user=request.user
    )

    sessao = _sessao_ativa_do_aluno(aluno)
    if not sessao:
        return JsonResponse({'success': True, 'ativa': False})

    registro = Checkin_Checkout.objects.filter(rota=sessao, aluno=aluno).first()
    embarcado = bool(registro and registro.checkin_realizado and not registro.checkout_realizado)
    desembarcou = bool(registro and registro.checkout_realizado)

    casa = None
    if aluno.casa_definida:
        casa = {'tipo': 'casa', 'nome': 'Casa', 'lat': aluno.casa_latitude, 'lng': aluno.casa_longitude}

    escola = None
    if aluno.escola_id:
        escola = {'tipo': 'escola', 'nome': aluno.escola.nome,
                  'lat': aluno.escola.latitude, 'lng': aluno.escola.longitude}

    if desembarcou:
        destino = None
    elif (sessao.tipo == 'IDA') == embarcado:
        destino = escola
    else:
        destino = casa

    ultimas = list(sessao.posicoes.order_by('-registrado_em')[:120])
    posicao = None
    trilha = []
    if ultimas:
        ultima = ultimas[0]
        direcao = next((p.direcao for p in ultimas if p.direcao is not None), None)
        posicao = {
            'lat': ultima.latitude,
            'lng': ultima.longitude,
            'direcao': direcao,
            'velocidade': ultima.velocidade,
            'precisao': ultima.precisao,
            'segundos': max(0, int((timezone.now() - ultima.registrado_em).total_seconds())),
        }
        trilha = [[p.latitude, p.longitude] for p in reversed(ultimas)]

    return JsonResponse({
        'success': True,
        'ativa': True,
        'rota': {'nome': sessao.nome_rota, 'tipo': sessao.tipo},
        'embarcado': embarcado,
        'desembarcou': desembarcou,
        'destino': destino,
        'posicao': posicao,
        'trilha': trilha,
    })


@login_required
@require_POST
def api_salvar_local(request):

    try:
        dados = json.loads(request.body)
        aluno = get_object_or_404(Aluno, id=dados.get('aluno_id'), responsavel__user=request.user)

        tipo = dados.get('tipo')
        latitude = round(float(dados.get('latitude')), 6)
        longitude = round(float(dados.get('longitude')), 6)
        if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
            return JsonResponse({'success': False, 'error': 'Coordenadas inválidas.'}, status=400)

        endereco = (dados.get('endereco') or '').strip()[:255]

        if tipo == 'casa':
            aluno.endereco = endereco
            aluno.casa_latitude = latitude
            aluno.casa_longitude = longitude
            aluno.save(update_fields=['endereco', 'casa_latitude', 'casa_longitude'])

        elif tipo == 'escola':
            nome = (dados.get('nome') or '').strip()[:150]
            if not nome:
                return JsonResponse({'success': False, 'error': 'Informe o nome da escola.'}, status=400)

            escola, _ = Escola.objects.get_or_create(
                nome=nome,
                latitude=latitude,
                longitude=longitude,
                defaults={'endereco': endereco},
            )
            aluno.escola = escola
            aluno.save(update_fields=['escola'])

        else:
            return JsonResponse({'success': False, 'error': 'Tipo de local inválido.'}, status=400)

        return JsonResponse({'success': True})

    except Http404:
        return JsonResponse({'success': False, 'error': 'Aluno não encontrado.'}, status=404)
    except (ValueError, TypeError):
        return JsonResponse({'success': False, 'error': 'Dados inválidos.'}, status=400)