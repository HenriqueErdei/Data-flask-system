import os
from datetime import datetime

def registrar_log(mensagem, usuario=None, log_path='data/logs/system.log'):
    data_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_msg = f'[{data_hora}]'
    if usuario:
        log_msg += f' [Usuário: {usuario}]'
    log_msg += f' {mensagem}\n'
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(log_msg)
    # Log por usuário (opcional)
    if usuario:
        user_log_dir = 'data/logs/actions/'
        os.makedirs(user_log_dir, exist_ok=True)
        user_log_file = os.path.join(user_log_dir, f'{usuario}.log')
        with open(user_log_file, 'a', encoding='utf-8') as f:
            f.write(log_msg)
