import pandas as pd

# Caminho do arquivo dentro do contêiner
file_path = "municipios.xlsx"

try:
    # Lê o arquivo Excel
    df = pd.read_excel(file_path)
    
    # Mostra os nomes das colunas
    print("Colunas encontradas:", df.columns.tolist())
except FileNotFoundError:
    print(f"Erro: Arquivo não encontrado em {file_path}")
except Exception as e:
    print(f"Erro ao ler a planilha: {e}")
