from django .contrib import admin 
from apps .cerebro .models import Motorista ,Responsavel ,Aluno ,Biometria 

admin .site .register (Motorista )
admin .site .register (Responsavel )
admin .site .register (Aluno )
admin .site .register (Biometria )