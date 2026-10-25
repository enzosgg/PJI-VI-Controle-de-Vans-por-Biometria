from django.db import models
from django.contrib.auth.models import User
import uuid

AVATARES = [
    ('raposa', '🦊', 'Raposa'),
    ('panda', '🐼', 'Panda'),
    ('tigre', '🐯', 'Tigre'),
    ('leao', '🦁', 'Leão'),
    ('sapo', '🐸', 'Sapo'),
    ('macaco', '🐵', 'Macaco'),
    ('coelho', '🐰', 'Coelho'),
    ('cachorro', '🐶', 'Cachorro'),
    ('gato', '🐱', 'Gato'),
    ('unicornio', '🦄', 'Unicórnio'),
    ('polvo', '🐙', 'Polvo'),
    ('pinguim', '🐧', 'Pinguim'),
    ('dinossauro', '🦖', 'Dinossauro'),
    ('foguete', '🚀', 'Foguete'),
    ('bola', '⚽', 'Bola'),
    ('arco_iris', '🌈', 'Arco-íris'),
]
AVATAR_EMOJI = {chave: emoji for chave, emoji, _ in AVATARES}


class Motorista(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='motorista', null=True, blank=True)
    nome = models.CharField(max_length=100, default='Sem nome')


class Responsavel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='responsavel', null=True, blank=True)
    nome = models.CharField(max_length=100, default='Sem nome')
    telefone = models.CharField(max_length=20, blank=True)


class Rotas(models.Model):
    STATUS_CHOICES = (
        ('ATIVA', 'Ativa'),
        ('FINALIZADA', 'Finalizada'),
        ('CANCELADA', 'Cancelada'),
    )

    TIPO_CHOICES = (
        ('IDA', 'Ida para Escola'),
        ('VOLTA', 'Volta para Casa'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome_rota = models.CharField(max_length=100, help_text="Ex: Rota Manhã - Bairro A")
    tipo = models.CharField(max_length=5, choices=TIPO_CHOICES)
    data_inicio = models.DateTimeField(auto_now_add=True)
    data_fim = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ATIVA')
    horario_previsto = models.TimeField(null=True, blank=True)
    motorista = models.ForeignKey(Motorista, on_delete=models.CASCADE, related_name='rotas_realizadas', null=True)

    def __str__(self):
        return f"{self.nome_rota} - {self.get_tipo_display()} - {self.data_inicio.strftime('%d/%m/%Y %H:%M')}"

    def get_total_checkins(self):
        return self.registros.filter(checkin_realizado=True).count()

    def get_total_checkouts(self):
        return self.registros.filter(checkout_realizado=True).count()

    def get_divergencia(self):
        return self.get_total_checkins() - self.get_total_checkouts()


class Escola(models.Model):
    nome = models.CharField(max_length=150)
    endereco = models.CharField(max_length=255, blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.nome


class Aluno(models.Model):
    nome = models.CharField(max_length=100)
    responsavel = models.ForeignKey(Responsavel, on_delete=models.CASCADE, related_name='alunos')
    rota = models.ForeignKey(Rotas, on_delete=models.SET_NULL, null=True, blank=True, related_name='alunos')
    escola = models.ForeignKey(Escola, on_delete=models.SET_NULL, null=True, blank=True, related_name='alunos')
    endereco = models.CharField(max_length=255, blank=True)
    casa_latitude = models.FloatField(null=True, blank=True)
    casa_longitude = models.FloatField(null=True, blank=True)
    avatar = models.CharField(max_length=20, default='raposa')

    @property
    def avatar_emoji(self):
        return AVATAR_EMOJI.get(self.avatar, '🙂')

    @property
    def casa_definida(self):
        return self.casa_latitude is not None and self.casa_longitude is not None


class Checkin_Checkout(models.Model):
    rota = models.ForeignKey(Rotas, on_delete=models.CASCADE, related_name='registros', null=True)
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='historico_viagens', null=True)

    checkin_realizado = models.BooleanField(default=False)
    checkout_realizado = models.BooleanField(default=False)
    horario_checkin = models.DateTimeField(null=True, blank=True)
    horario_checkout = models.DateTimeField(null=True, blank=True)
    metodo_checkin = models.CharField(max_length=20, blank=True)
    observacao = models.TextField(blank=True)


class PosicaoVan(models.Model):
    rota = models.ForeignKey(Rotas, on_delete=models.CASCADE, related_name='posicoes')
    latitude = models.FloatField()
    longitude = models.FloatField()
    direcao = models.FloatField(null=True, blank=True)
    velocidade = models.FloatField(null=True, blank=True)
    precisao = models.FloatField(null=True, blank=True)
    dispositivo = models.CharField(max_length=64, blank=True)
    registrado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['rota', '-registrado_em'])]


class Biometria(models.Model):
    aluno = models.OneToOneField(Aluno, on_delete=models.CASCADE, related_name='biometria')
    template_direita = models.TextField(blank=True, default='')
    template_esquerda = models.TextField(blank=True, default='')

    @property
    def completa(self):
        return bool(self.template_direita and self.template_esquerda)

    def template_do_lado(self, lado):
        return self.template_direita if lado == 'Right' else self.template_esquerda


class Ocorrencia(models.Model):
    TIPOS = (
        ('ESQUECIMENTO_VAN', 'Possível Esquecimento dentro da Van'),
        ('ESQUECIMENTO_ESCOLA', 'Possível Esquecimento na Escola'),
        ('ALERTA_GERAL', 'Alerta Geral'),
        ('ATRASO', 'Atraso na Rota'),
        ('PROBLEMA_VAN', 'Problema com o Veículo'),
        ('OUTRO', 'Outro'),
    )

    data_hora = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    rota = models.ForeignKey(Rotas, on_delete=models.CASCADE, related_name='ocorrencias', null=True, blank=True)
    mensagem = models.TextField()
    telefone_destino = models.CharField(max_length=20)
    enviado = models.BooleanField(default=False)
    data_envio = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.data_hora.strftime('%d/%m/%Y %H:%M')} - {self.get_tipo_display()}"