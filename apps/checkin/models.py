from django .db import models 
from django .utils import timezone 
import uuid 

class SessaoRota (models .Model ):
    """Sessão de uma rota (ida ou volta)"""
    STATUS_CHOICES =(
    ('ATIVA','Ativa'),
    ('FINALIZADA','Finalizada'),
    ('CANCELADA','Cancelada'),
    )

    TIPO_CHOICES =(
    ('IDA','Ida para Escola'),
    ('VOLTA','Volta para Casa'),
    )

    id =models .UUIDField (primary_key =True ,default =uuid .uuid4 ,editable =False )
    nome_rota =models .CharField (max_length =100 ,help_text ="Ex: Rota Manhã - Bairro A")
    tipo =models .CharField (max_length =5 ,choices =TIPO_CHOICES )
    data_inicio =models .DateTimeField (auto_now_add =True )
    data_fim =models .DateTimeField (null =True ,blank =True )
    status =models .CharField (max_length =10 ,choices =STATUS_CHOICES ,default ='ATIVA')


    motorista =models .CharField (max_length =100 ,blank =True ,default ='')
    horario_previsto =models .TimeField (null =True ,blank =True )

    def __str__ (self ):
        return f"{self .nome_rota } - {self .get_tipo_display ()} - {self .data_inicio .strftime ('%d/%m/%Y %H:%M')}"

    def get_total_checkins (self ):
        return self .registros .filter (checkin_realizado =True ).count ()

    def get_total_checkouts (self ):
        return self .registros .filter (checkout_realizado =True ).count ()

    def get_divergencia (self ):
        """Retorna a diferença entre checkins e checkouts"""
        return self .get_total_checkins ()-self .get_total_checkouts ()

class RegistroAluno (models .Model ):
    """Registro temporário do aluno durante uma rota"""
    id =models .UUIDField (primary_key =True ,default =uuid .uuid4 ,editable =False )
    sessao_rota =models .ForeignKey (SessaoRota ,on_delete =models .CASCADE ,related_name ='registros')


    aluno_id_temporario =models .CharField (max_length =50 )
    nome_aluno =models .CharField (max_length =200 ,blank =True )
    responsavel =models .CharField (max_length =200 ,blank =True )
    telefone_responsavel =models .CharField (max_length =20 ,blank =True )


    palm_template =models .TextField (blank =True )


    qrcode_data =models .CharField (max_length =200 ,blank =True )


    checkin_realizado =models .BooleanField (default =False )
    checkout_realizado =models .BooleanField (default =False )
    horario_checkin =models .DateTimeField (null =True ,blank =True )
    horario_checkout =models .DateTimeField (null =True ,blank =True )
    metodo_checkin =models .CharField (max_length =20 ,blank =True )


    observacao =models .TextField (blank =True )

    class Meta :
        unique_together =['sessao_rota','aluno_id_temporario']

    def __str__ (self ):
        return f"{self .aluno_id_temporario } - {self .sessao_rota .nome_rota }"