import psycopg2
from dotenv import load_dotenv
import pandas as pd
import os

from login import acesso_turma

load_dotenv()

caminho_csv = './file.csv'  # A partir do diretório atual


def conectar_banco():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('PG_DB'),
            user=os.getenv('PG_USER'),
            password=os.getenv('PG_PASSWORD'),
            host=os.getenv('PG_HOST'),
            port=os.getenv('PG_PORT')
        )
        conn.autocommit = True       
        if conn.status:
            print("Conectado com sucesso!") 
            return conn
    except Exception as e:
        print(f"Erro ao criar banco de dados: {e}")    


def criar_tabelas():

    try:
        conn = conectar_banco()
        
        # Criação de cursor
        cur = conn.cursor()

        # Criação das tabelas
        cur.execute('''
            CREATE TABLE IF NOT EXISTS alunos (
                nome_aluno VARCHAR(100),
                ra VARCHAR(20),
                digito_ra VARCHAR(5),
                data_nascimento DATE,
                PRIMARY KEY (ra, digito_ra)
            );
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS emails (
                email_google VARCHAR(100),
                email_microsoft VARCHAR(100),
                ra VARCHAR(20),
                digito_ra VARCHAR(5),
                PRIMARY KEY (ra, digito_ra),
                FOREIGN KEY (ra, digito_ra) REFERENCES alunos (ra, digito_ra)
            );
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS turma (
                turma VARCHAR(50),
                ra VARCHAR(20),
                digito_ra VARCHAR(5),
                situacao_aluno VARCHAR(50),
                PRIMARY KEY (ra, digito_ra),
                FOREIGN KEY (ra, digito_ra) REFERENCES alunos (ra, digito_ra)
            );
        ''')

        # Commitar as alterações
        conn.commit()

        # Fechar a conexão
        cur.close()
        conn.close()

        print("Tabelas criadas com sucesso! ")

    except Exception as e:
        print(f"Erro ao criar tabelas: {e}")

# Função para carregar o CSV e inserir os dados no banco de dados
def inserir_dados_no_banco():
    df = pd.read_csv(caminho_csv)
    
    # Verificar se as colunas esperadas estão no CSV
    colunas_esperadas = ['RA', 'Dig. RA', 'Nome do Aluno', 'Data de Nascimento', 'Email Microsoft', 'Email Google', 'Situação do Aluno', 'Turma']
    
    if not all(coluna in df.columns for coluna in colunas_esperadas):
        raise ValueError(f"O arquivo CSV deve conter as seguintes colunas: {colunas_esperadas}")
    
    # Garantir que a coluna de data esteja no formato correto
    df['Data de Nascimento'] = pd.to_datetime(df['Data de Nascimento'], errors='coerce')
    
    return df


def popular_tabelas():
    df = inserir_dados_no_banco()
    conn = conectar_banco()
        
    # Criação de cursor
    cur = conn.cursor()

    # Inserir dados na tabela 'alunos', 'emails' e 'turma'
    for index, row in df.iterrows():
        # Inserir na tabela 'alunos'
        cur.execute('''
            INSERT INTO alunos (ra, digito_ra, nome_aluno, data_nascimento)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (ra, digito_ra) DO NOTHING;
        ''', (row['RA'], row['Dig. RA'], row['Nome do Aluno'], row['Data de Nascimento']))
        
        # Inserir na tabela 'emails'
        cur.execute('''
            INSERT INTO emails (ra, digito_ra, email_microsoft, email_google)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (ra, digito_ra) DO NOTHING;
        ''', (row['RA'], row['Dig. RA'], row['Email Microsoft'], row['Email Google']))
        
        # Inserir na tabela 'turma'
        cur.execute('''
            INSERT INTO turma (ra, digito_ra, situacao_aluno, turma)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (ra, digito_ra) DO NOTHING;
        ''', (row['RA'], row['Dig. RA'], row['Situação do Aluno'], row['Turma']))

    # Commitar as mudanças no banco
    conn.commit()
    print('Tabelas populadas com sucesso!')
    # Fechar o cursor e a conexão
    cur.close()
    conn.close()
    

if __name__ == '__main__':
    
    criar_tabelas()
    acesso_turma()
    popular_tabelas()
    # verificar_db()


