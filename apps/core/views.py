from django .shortcuts import redirect 
from django .contrib .auth .decorators import login_required 

@login_required 
def dashboard (request ):
    """Redireciona para o dashboard apropriado baseado no tipo de usuário"""
    if request .user .tipo =='ADMIN'or request .user .is_superuser :
        return redirect ('admin_dashboard')
    elif request .user .tipo =='MOTORISTA':
        return redirect ('motorista_dashboard')
    elif request .user .tipo =='RESPONSAVEL':
        return redirect ('responsavel_dashboard')
    else :
        return redirect ('admin_dashboard')