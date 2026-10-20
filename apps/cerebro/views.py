from django .shortcuts import redirect 
from django .contrib .auth .decorators import login_required 

@login_required 
def dashboard (request ):

    if request .user .is_superuser :
        return redirect ('admin:index')
    elif hasattr (request .user ,'motorista'):
        return redirect ('motorista')
    elif hasattr (request .user ,'responsavel'):
        return redirect ('responsavel')
    else :
        return redirect ('admin:index')