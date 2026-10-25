from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import JsonResponse, Http404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from apps.cerebro.models import Rotas, Checkin_Checkout, Aluno, Biometria, PosicaoVan
from apps.cerebro.palm_recognition import palm_recognition, MAO_PARA_LADO
import json

PRECISAO_MAXIMA_M = 200
TEMPO_BLOQUEIO_S = 30

MENSAGENS_ERRO_PALMA = {
    'DORSO_DETECTADO': 'Dorso da mão detectado. Por favor, mostre a PALMA da mão virada para a câmera.',
    'MAO_INCORRETA': 'Essa não é a mão solicitada. Troque de mão e tente novamente.',
}


@login_required
@user_passes_test(lambda u: hasattr(u, 'motorista'), login_url='dashboard')
def motorista(request):
    motorista_perfil = request.user.motorista
    rotas_ativas = Rotas.objects.filter(motorista=motorista_perfil, status='ATIVA')
    rotas_finalizadas = Rotas.objects.filter(motorista=motorista_perfil, status='FINALIZADA').order_by('-data_fim')[:10]

    context = {
        'rotas_ativas': rotas_ativas,
        'rotas_finalizadas': rotas_finalizadas,
        'total_ativas': rotas_ativas.count(),
    }
    return render(request, 'motorista.html', context)


@login_required
@user_passes_test(lambda u: hasattr(u, 'motorista'), login_url='dashboard')
def iniciar_rota(request):
    if request.method == 'POST':
        nome_rota = request.POST.get('nome_rota')
        tipo = request.POST.get('tipo')
        horario_previsto = request.POST.get('horario_previsto')

        if not horario_previsto:
            horario_previsto = None

        sessao = Rotas.objects.create(
            nome_rota=nome_rota,
            tipo=tipo,
            motorista=request.user.motorista,
            horario_previsto=horario_previsto,
            status='ATIVA'
        )

        messages.success(request, f'Rota "{nome_rota}" iniciada com sucesso!')
        return redirect('checkin_aluno', sessao_id=sessao.id)

    return render(request, 'iniciar_rota.html')


@login_required
@user_passes_test(lambda u: hasattr(u, 'motorista'), login_url='dashboard')
def checkin_aluno(request, sessao_id):
    sessao = get_object_or_404(Rotas, id=sessao_id, status='ATIVA')

    if request.method == 'POST':
        metodo = request.POST.get('metodo')
        aluno_id = request.POST.get('aluno_id')

        aluno = get_object_or_404(Aluno, id=aluno_id)

        registro, created = Checkin_Checkout.objects.get_or_create(
            rota=sessao,
            aluno=aluno,
            defaults={
                'checkin_realizado': True,
                'horario_checkin': timezone.now(),
                'metodo_checkin': metodo
            }
        )

        if not created and not registro.checkin_realizado:
            registro.checkin_realizado = True
            registro.horario_checkin = timezone.now()
            registro.metodo_checkin = metodo
            registro.save()

        messages.success(request, f'Check-in realizado: {aluno.nome}')
        return redirect('checkin_aluno', sessao_id=sessao_id)

    registros_queryset = sessao.registros.filter(checkin_realizado=True).order_by('horario_checkin')

    context = {
        'sessao': sessao,
        'registros': registros_queryset,
        'total_checkins': registros_queryset.count(),
        'alunos_disponiveis': Aluno.objects.all()
    }
    return render(request, 'checkin_aluno.html', context)


@login_required
@user_passes_test(lambda u: hasattr(u, 'motorista'), login_url='dashboard')
def checkout_escola(request, sessao_id):
    sessao = get_object_or_404(Rotas, id=sessao_id, status='ATIVA')

    if request.method == 'POST':
        aluno_id = request.POST.get('aluno_id')

        try:
            registro = sessao.registros.get(aluno_id=aluno_id, checkin_realizado=True)
            registro.checkout_realizado = True
            registro.horario_checkout = timezone.now()
            registro.save()

            messages.success(request, f'Check-out realizado: {registro.aluno.nome}')

            divergencia = sessao.get_divergencia()
            if divergencia > 0:
                messages.warning(request, f'ATENÇÃO: {divergencia} aluno(s) ainda não fizeram check-out!')

        except Checkin_Checkout.DoesNotExist:
            messages.error(request, 'Aluno não encontrado ou já fez check-out')

        return redirect('checkout_escola', sessao_id=sessao_id)

    registros_pendentes = sessao.registros.filter(checkin_realizado=True, checkout_realizado=False).order_by('horario_checkin')

    context = {
        'sessao': sessao,
        'registros': registros_pendentes,
        'total_checkins': sessao.get_total_checkins(),
        'total_checkouts': sessao.get_total_checkouts(),
        'divergencia': sessao.get_divergencia()
    }
    return render(request, 'checkout_escola.html', context)


@login_required
@user_passes_test(lambda u: hasattr(u, 'motorista'), login_url='dashboard')
def finalizar_rota(request, sessao_id):
    sessao = get_object_or_404(Rotas, id=sessao_id)

    if request.method == 'POST':
        divergencia = sessao.get_divergencia()
        motivo = request.POST.get('motivo')

        if divergencia > 0 and not motivo:
            mensagem = f"ALERTA GRAVE: Rota {sessao.nome_rota} finalizada com {divergencia} aluno(s) sem check-out!"
            messages.error(request, mensagem)
            return render(request, 'alerta_esquecimento.html', {
                'sessao': sessao,
                'divergencia': divergencia
            })

        sessao.status = 'FINALIZADA'
        sessao.data_fim = timezone.now()
        sessao.save()

        messages.success(request, f'Rota "{sessao.nome_rota}" finalizada com sucesso!')
        return redirect('motorista')

    context = {
        'sessao': sessao,
        'total_checkins': sessao.get_total_checkins(),
        'total_checkouts': sessao.get_total_checkouts(),
        'divergencia': sessao.get_divergencia()
    }
    return render(request, 'finalizar_rota.html', context)


@login_required
@user_passes_test(lambda u: hasattr(u, 'motorista'), login_url='dashboard')
@require_POST
def api_enviar_posicao(request):

    try:
        dados = json.loads(request.body)

        sessao = get_object_or_404(
            Rotas,
            id=dados.get('sessao_id'),
            motorista=request.user.motorista,
            status='ATIVA'
        )

        latitude = float(dados.get('latitude'))
        longitude = float(dados.get('longitude'))
        if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
            return JsonResponse({'success': False, 'error': 'Coordenadas inválidas.'}, status=400)

        direcao = dados.get('direcao')
        direcao = float(direcao) % 360 if direcao is not None else None

        velocidade = dados.get('velocidade')
        velocidade = max(0.0, float(velocidade)) if velocidade is not None else None

        precisao = dados.get('precisao')
        precisao = max(0.0, float(precisao)) if precisao is not None else None
        if precisao is not None and precisao > PRECISAO_MAXIMA_M:
            return JsonResponse({
                'success': False,
                'codigo': 'PRECISAO_BAIXA',
                'error': f'Precisão do GPS muito baixa (±{round(precisao)} m).'
            }, status=422)

        dispositivo = str(dados.get('dispositivo') or '')[:64]
        assumir = bool(dados.get('assumir'))

        ultima = sessao.posicoes.order_by('-registrado_em').first()
        if (ultima and dispositivo and ultima.dispositivo
                and ultima.dispositivo != dispositivo and not assumir):
            segundos = (timezone.now() - ultima.registrado_em).total_seconds()
            if segundos < TEMPO_BLOQUEIO_S:
                return JsonResponse({
                    'success': False,
                    'codigo': 'OUTRO_APARELHO',
                    'error': 'Outro aparelho já está compartilhando a localização desta rota.'
                }, status=409)

        PosicaoVan.objects.create(
            rota=sessao,
            latitude=latitude,
            longitude=longitude,
            direcao=direcao,
            velocidade=velocidade,
            precisao=precisao,
            dispositivo=dispositivo,
        )
        return JsonResponse({'success': True})

    except Http404:
        return JsonResponse({'success': False, 'error': 'Rota não encontrada ou já finalizada.'}, status=404)
    except (ValueError, TypeError, ValidationError):
        return JsonResponse({'success': False, 'error': 'Dados inválidos.'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@login_required
def api_ler_biometria(request):

    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)

    try:
        dados = json.loads(request.body)
        template_atual = dados.get('template')
        sessao_id = dados.get('sessao_id')

        if not template_atual or not sessao_id:
            return JsonResponse({'success': False, 'error': 'Dados incompletos.'})

        get_object_or_404(Rotas, id=sessao_id)

        biometrias = (
            Biometria.objects
            .select_related('aluno')
            .exclude(template_direita='', template_esquerda='')
        )

        biometria, score, ranking = palm_recognition.identificar_aluno(template_atual, biometrias)

        if settings.DEBUG:

            print('[palma] ranking:', [(nome, round(s, 3)) for nome, s in ranking[:5]], flush=True)

        if biometria is None:
            if ranking:
                return JsonResponse({
                    'success': False,
                    'error': 'Não foi possível identificar com segurança (resultado parecido '
                             'com mais de um aluno). Tente de novo com a mão bem aberta.'
                })
            return JsonResponse({'success': False, 'error': 'Aluno não reconhecido.'})

        aluno = biometria.aluno
        return JsonResponse({
            'success': True,
            'aluno_id': aluno.id,
            'nome_aluno': aluno.nome
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@login_required
def api_capturar_palma(request):

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método não permitido'})

    try:
        dados = json.loads(request.body)
        imagem_base64 = dados.get('imagem')
        mao = dados.get('mao')  # opcional

        if not imagem_base64:
            return JsonResponse({'success': False, 'error': 'Imagem não enviada.'})

        if mao is not None and mao not in MAO_PARA_LADO:
            return JsonResponse({'success': False, 'error': 'Mão inválida.'})

        template_json = palm_recognition.imagem_infos(imagem_base64, mao_esperada=mao)

        if not template_json:
            return JsonResponse({'success': False, 'error': 'Mão não detectada'})

        template_dict = json.loads(template_json)
        erro = template_dict.get('error')
        if erro:
            return JsonResponse({
                'success': False,
                'error': MENSAGENS_ERRO_PALMA.get(erro, erro)
            })

        return JsonResponse({'success': True, 'template': template_json})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
def api_sensor_status(request):
    return JsonResponse({
        'ativo': True,
        'tipo': 'palma',
        'mensagem': 'Sensor em desenvolvimento',
        'versao_api': '1.0.0'
    })