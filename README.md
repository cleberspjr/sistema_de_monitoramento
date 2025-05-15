# sistema-monitoramento
Protótipo de software leve e customizável para monitoramento térmico e consumo de CPU, com visualização via Dashboard interativo 
Este protótipo de sistema coleta dados térmicos e de uso da CPU, armazena em um banco de dados MariaDB e os apresenta em um painel web com gráficos interativos.

🚀 Funcionalidades
• Coleta contínua de temperaturas por zona térmica.
• Monitoramento de consumo de múltiplos núcleos de CPU.

•Dashboard responsivo e interativo com seleção por:

    •Zona térmica
    •Data e intervalo de horário
    •Múltiplos CPUs

•Visualizações comparativas:

    •Temperaturas por zona
    •Consumo da CPU original e múltiplos CPUs

🧰 Tecnologias utilizadas
•Python 3
•Dash (Plotly)
•Dash Bootstrap Components
•Pandas
•MariaDB
•Plotly Graph Objects

🖥️ Requisitos

Antes de rodar o projeto, instale os seguintes pacotes no ambiente Python:
pip install dash dash-bootstrap-components pandas mariadb plotly

Além disso, é necessário ter:

Python 3.8 ou superior
MariaDB instalado e configurado localmente


⚙️ Como Executar (Ubuntu / VS Code)

1. Clone o repositório:
    git clone https://github.com/seu-usuario/seu-repositorio.git

2. Instale as dependências:
    pip install dash dash-bootstrap-components pandas mariadb plotly

3. Execute uma das opções abaixo:
   ▶️ Opção 1 - Coleta de dados térmicos
   python3 main.py 1

   ▶️ Opção 2 - Executar o Dashboard
   python3 main.py 2

   Inicia o dashboard interativo em: http://127.0.0.1:8050

## Observação importante
O banco de dados incluído neste projeto contém dados apenas do dia 29-05-2024.
Ao acessar o dashboard, altere o campo de data para 2024-05-29 para visualizar os gráficos corretamente.
