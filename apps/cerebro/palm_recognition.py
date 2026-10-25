import base64
import json
import math
import re
import time

import cv2
import mediapipe as mp
import numpy as np

MAO_PARA_LADO = {'direita': 'Right', 'esquerda': 'Left'}

ESPELHAR_IMAGEM = True

LIMIAR_DIFERENCA = 0.25

MARGEM_MINIMA = 0.02


class PalmRecognition:
    def __init__(self):
        self.available = True
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=True,
            max_num_hands=1,
            min_detection_confidence=0.5,
        )

    def conversor(self, conversor_base64):
        """Converte a imagem de base64 para imagem OpenCV."""
        try:
            if not conversor_base64:
                return None
            if ',' in conversor_base64:
                conversor_base64 = conversor_base64.split(',')[1]

            conversor_base64 = re.sub(r'[^a-zA-Z0-9+/]', '', conversor_base64)
            conversor_base64 += "=" * ((4 - len(conversor_base64) % 4) % 4)
            imagem_data = base64.b64decode(conversor_base64)
            np_array = np.frombuffer(imagem_data, np.uint8)
            imagem = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

            if imagem is None or imagem.size == 0:
                return None
            return imagem
        except Exception:
            return None

    def imagem_infos(self, image_data, mao_esperada=None):

        imagem = self.conversor(image_data)
        if imagem is None:
            return None

        if len(imagem.shape) != 3 or imagem.shape[0] < 50 or imagem.shape[1] < 50:
            return None

        if ESPELHAR_IMAGEM:
            imagem = cv2.flip(imagem, 1)

        imagem_rgb = cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB)
        imagem_rgb = np.ascontiguousarray(imagem_rgb)
        imagem_rgb.flags.writeable = False

        try:
            resultados = self.hands.process(imagem_rgb)
        except Exception:
            return None
        finally:
            imagem_rgb.flags.writeable = True

        if not resultados or not resultados.multi_hand_landmarks:
            return None

        lado_da_mao = resultados.multi_handedness[0].classification[0].label
        referencias_da_palma = resultados.multi_hand_landmarks[0]

        if mao_esperada and lado_da_mao != MAO_PARA_LADO.get(mao_esperada):
            return json.dumps({"error": "MAO_INCORRETA", "lado_detectado": lado_da_mao})

        referencias_lista = [
            {'x': r.x, 'y': r.y, 'z': r.z} for r in referencias_da_palma.landmark
        ]

        # Detecção de dorso (costas da mão)
        p0, p5, p17 = referencias_lista[0], referencias_lista[5], referencias_lista[17]
        v1_x, v1_y = p5['x'] - p0['x'], p5['y'] - p0['y']
        v2_x, v2_y = p17['x'] - p0['x'], p17['y'] - p0['y']
        cross_z = (v1_x * v2_y) - (v1_y * v2_x)

        costas_da_mao = (
            (lado_da_mao == 'Right' and cross_z < 0)
            or (lado_da_mao == 'Left' and cross_z > 0)
        )
        if costas_da_mao:
            return json.dumps({"error": "DORSO_DETECTADO"})

        p9 = referencias_lista[9]
        escala_base = math.sqrt((p9['x'] - p0['x']) ** 2 + (p9['y'] - p0['y']) ** 2)

        assinatura_geometrica = []
        pontos_chave = [4, 8, 12, 16, 20]

        if escala_base > 0:
            for idx in pontos_chave:
                ponto = referencias_lista[idx]
                dist = math.sqrt((ponto['x'] - p0['x']) ** 2 + (ponto['y'] - p0['y']) ** 2)
                assinatura_geometrica.append(dist / escala_base)

            for i in range(len(pontos_chave) - 1):
                a = referencias_lista[pontos_chave[i]]
                b = referencias_lista[pontos_chave[i + 1]]
                dist = math.sqrt((a['x'] - b['x']) ** 2 + (a['y'] - b['y']) ** 2)
                assinatura_geometrica.append(dist / escala_base)

        template = {
            'simulated': False,
            'timestamp': time.time(),
            'lado_da_mao': lado_da_mao,
            'assinatura': assinatura_geometrica,
        }
        return json.dumps(template)

    def comparador_de_palmas(self, template1, template2, threshold=LIMIAR_DIFERENCA):
        if not template1 or not template2:
            return False, 0

        try:
            t1 = json.loads(template1)
            t2 = json.loads(template2)

            if "error" in t1 or "error" in t2:
                return False, 0

            if t1.get('lado_da_mao') and t2.get('lado_da_mao'):
                if t1['lado_da_mao'] != t2['lado_da_mao']:
                    return False, 0

            l1 = t1.get('assinatura', [])
            l2 = t2.get('assinatura', [])
            if not l1 or not l2 or len(l1) != len(l2):
                return False, 0

            diferencas = [abs(v1 - v2) for v1, v2 in zip(l1, l2)]
            media_distancia = sum(diferencas) / len(diferencas)

            return media_distancia < threshold, max(0, 1.0 - media_distancia)
        except Exception:
            return False, 0

    def comparar_com_biometria(self, template_capturado, biometria, threshold=LIMIAR_DIFERENCA):

        if not template_capturado or biometria is None:
            return False, 0
        try:
            lado = json.loads(template_capturado).get('lado_da_mao')
        except Exception:
            return False, 0
        if lado not in ('Right', 'Left'):
            return False, 0

        template_cadastrado = biometria.template_do_lado(lado)
        return self.comparador_de_palmas(template_capturado, template_cadastrado, threshold)

    def identificar_aluno(self, template_capturado, biometrias,
                          threshold=LIMIAR_DIFERENCA, margem=MARGEM_MINIMA):

        candidatos = []
        for biometria in biometrias:
            match, score = self.comparar_com_biometria(template_capturado, biometria, threshold)
            if match:
                candidatos.append((score, biometria))

        candidatos.sort(key=lambda c: c[0], reverse=True)
        ranking = [(b.aluno.nome, s) for s, b in candidatos]

        if not candidatos:
            return None, 0, []

        if len(candidatos) > 1 and (candidatos[0][0] - candidatos[1][0]) < margem:
            return None, 0, ranking

        return candidatos[0][1], candidatos[0][0], ranking


palm_recognition = PalmRecognition()