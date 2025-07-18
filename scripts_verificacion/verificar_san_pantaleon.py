import pandas as pd

df = pd.read_csv('datos/csv_procesado/agendas_consolidadas.csv')

print("=== EFECTORES PROCESADOS ===")
print(df['efector'].value_counts())

print("\n=== ¿CAPS San Pantaleón procesado? ===")
san_pantaleon = df[df['efector'].str.contains('San Pantale', case=False, na=False)]
print(f"Registros: {len(san_pantaleon)}")

if len(san_pantaleon) > 0:
    print("\nAgendas encontradas:")
    agendas = san_pantaleon[['nombre_original_agenda', 'efector']].drop_duplicates()
    for _, row in agendas.iterrows():
        print(f"  • {row['nombre_original_agenda']} ({row['efector']})")
else:
    print("❌ CAPS San Pantaleón NO fue procesado")
