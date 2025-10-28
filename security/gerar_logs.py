import random
from datetime import datetime, timedelta

# Configurações
nomes = [
    "Carlos Henrique", "Fernanda Souza", "Marcos Paulo", "Juliana Almeida",
    "Rodrigo Santos", "Patrícia Lima", "Gustavo Ribeiro", "Camila Fernandes",
    "Eduardo Martins", "Tatiane Pereira", "Mariana Maria Macedo", "Helena Joaquina"
]

cidades = [
    {"nome": "Adamantina", "url": "https://maps.google.com/?q=-21.6821,-51.0737"},
    {"nome": "Lucélia", "url": "https://maps.google.com/?q=-21.7193,-51.0213"}
]

atividades = [
    "Login no sistema",
    "Consulta de Pets",
    "Atualização de cadastro",
    "Cadastro de novo PETs",
    "Visualização de relatórios",
    "Edição de perfil",
    "Agendamento de consulta",
    "Exclusão de registro",
    "Upload de documento",
    "Logout do sistema"
]

# Datas de início e fim
inicio = datetime(2025, 10, 1)
fim = datetime(2025, 12, 31)

# Parâmetros fixos
country = "Brasil"
perfils = ["Atendente", "Gerente", "Cliente", "Médico", "Estagiário"]
uf_id = 25   # São Paulo
user_id = 1  # Ajuste conforme seu banco de dados

# Início do SQL
sql_output = """INSERT INTO `security_security_logs`
                (`Usuario`, `CEP`, `Endereco`, `Numero`, `Bairro`, `urlGgleMaps`,
                 `Cidade`, `Country`, `IP`, `Perfil_User`, `Atividade`, `DtHr_Atividade`,
                 `UF_id`, `user_id`) VALUES
"""

# Loop por dia
current_date = inicio
values = []

while current_date <= fim:
    num_logs = random.randint(22, 25)
    for _ in range(num_logs):
        nome = random.choice(nomes)
        cidade = random.choice(cidades)
        atividade = random.choice(atividades)
        hora = random.randint(22, 23)
        minuto = random.randint(0, 59)
        segundo = random.randint(0, 59)
        dt = current_date.replace(hour=hora, minute=minuto, second=segundo)

        # CEPs de Adamantina/Lucélia
        cep = random.choice(["17800-000", "17780-000"])
        endereco = random.choice(
            ["Rua Brasil", "Av. Rio Branco", "Rua das Flores", "Rua São João"])
        numero = str(random.randint(10, 999))
        bairro = random.choice(
            ["Centro", "Jardim Bela Vista", "Vila Industrial", "Jardim das Palmeiras"])
        ip = f"187.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"
        perfil = random.choice(perfils)

        values.append(
            f"('{nome}', '{cep}', '{endereco}', '{numero}', '{bairro}', '{cidade['url']}', "
            f"'{cidade['nome']}', '{country}', '{ip}', '{perfil}', '{atividade}', "
            f"'{dt.strftime('%Y-%m-%d %H:%M:%S')}', {uf_id}, {user_id})"
        )

    current_date += timedelta(days=1)

# Junta tudo em uma única instrução SQL
sql_output += ",\n".join(values) + ";"

# Salva em arquivo
with open("inserts_security_logs.sql", "w", encoding="utf-8") as f:
    f.write(sql_output)

print("Arquivo 'inserts_security_logs.sql' gerado com sucesso!")
