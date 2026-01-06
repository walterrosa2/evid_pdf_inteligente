
import pandas as pd
import sys

with open('headers_log.txt', 'w', encoding='utf-8') as f:
    try:
        f.write("Reading mapeamento...\n")
        df1 = pd.read_excel('evidencias_extraidas_mapeamento.xlsx')
        f.write(f"MAP Headers: {list(df1.columns)}\n")
    except Exception as e:
        f.write(f"Error reading mapeamento: {e}\n")

    try:
        f.write("Reading catalogador...\n")
        df2 = pd.read_excel('evidencias_extraidas_catalogador.xlsx')
        f.write(f"CAT Headers: {list(df2.columns)}\n")
    except Exception as e:
        f.write(f"Error reading catalogador: {e}\n")

print("Done writing to headers_log.txt")
