import pandas as pd
import re

# Nome do arquivo gerado no passo anterior
input_file = "pokemon_dual_type_competitivos.csv"

def extrair_bst(valor):
    match = re.search(r'\((\d+)\)', str(valor))
    return int(match.group(1)) if match else 0

try:
    # 1. Carregar os dados (sem cabeçalho)
    df = pd.read_csv(input_file, header=None)
    
    # Adicionar coluna de BST para ordenação
    df['bst_int'] = df[5].apply(extrair_bst)
    
    # 2. Identificar todos os tipos únicos presentes (nas colunas de índice 2 e 3)
    tipos_col1 = df[2].unique()
    tipos_col2 = df[3].unique()
    todos_tipos = sorted(list(set(tipos_col1) | set(tipos_col2)))

    # Criar o arquivo de saída
    with open("tabelas_por_tipo.md", "w", encoding="utf-8") as f:
        f.write("# Pokémon Clover - Dual Types por Tipo (480-600 BST)\n\n")

        # 3. Gerar uma tabela para cada tipo
        for tipo in todos_tipos:
            # Filtra Pokémon que tenham o tipo atual na coluna 2 OU na coluna 3
            mask = (df[2] == tipo) | (df[3] == tipo)
            df_tipo = df[mask].copy()
            
            # Ordenar decrescentemente pelo BST
            df_tipo = df_tipo.sort_values(by='bst_int', ascending=False)

            # Escrever o cabeçalho do tipo no arquivo
            f.write(f"## Tipo: {tipo.upper()}\n")
            f.write("| ID | Nome | Tipo 1 | Tipo 2 | Stats (BST) |\n")
            f.write("|---|---|---|---|---|\n")

            # Inserir as linhas dos Pokémon
            for _, row in df_tipo.iterrows():
                # row[0]=ID, row[1]=Nome, row[2]=Tipo1, row[3]=Tipo2, row[5]=Stats string
                f.write(f"| {row[0]} | **{row[1]}** | {row[2]} | {row[3]} | {row[5]} |\n")
            
            f.write("\n---\n\n")

    print(f"Sucesso! O arquivo 'tabelas_por_tipo.md' foi criado com as tabelas organizadas.")

except FileNotFoundError:
    print("Erro: O arquivo 'pokemon_dual_type_competitivos.csv' não foi encontrado.")
except Exception as e:
    print(f"Ocorreu um erro: {e}")