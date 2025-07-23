import pandas as pd

df = pd.read_csv('datos/csv_procesado/agendas_consolidadas.csv')

print('=== REPORTE ESTADÍSTICO COMPLETO ===')
print(f'Total de registros: {len(df):,}')
print(f'Total de efectores únicos: {df["efector"].nunique()}')
print(f'Total de áreas médicas únicas: {df["area"].nunique()}')
print(f'Total de doctores únicos: {df["doctor"].nunique()}')
print(f'Total de agendas únicas: {df["agenda_id"].nunique()}')
print()

print('=== DISTRIBUCIÓN POR EFECTOR ===')
for efector, count in df['efector'].value_counts().items():
    pct = count/len(df)*100
    print(f'{efector}: {count:,} registros ({pct:.1f}%)')
print()

print('=== DISTRIBUCIÓN POR DÍA ===')
for dia, count in df['dia'].value_counts().items():
    pct = count/len(df)*100
    print(f'{dia}: {count:,} registros ({pct:.1f}%)')
print()

print('=== VERIFICACIÓN DE NORMALIZACIÓN DE DÍAS ===')
sab_count = len(df[df['dia'].str.contains('Sáb', na=False)])
sabado_count = len(df[df['dia'] == 'Sábado'])
print(f'Entradas con "Sáb": {sab_count}')
print(f'Entradas con "Sábado": {sabado_count}')
print()

print('=== TOP 10 ÁREAS MÉDICAS ===')
for area, count in df['area'].value_counts().head(10).items():
    print(f'{area}: {count:,} registros')
print()

print('=== DATOS DE HCSI ===')
hcsi = df[df['efector'] == 'HCSI']
print(f'Registros HCSI: {len(hcsi):,}')
print(f'Áreas en HCSI: {hcsi["area"].nunique()}')
print(f'Doctores en HCSI: {hcsi["doctor"].nunique()}')
print()

print('=== TIPOS DE TURNO ===')
for tipo, count in df['tipo_turno'].value_counts().items():
    print(f'{tipo}: {count:,} registros')
print()

print('=== RANGOS DE HORARIOS ===')
horas_inicio_validas = df["hora_inicio"].dropna()
horas_fin_validas = df["hora_fin"].dropna()
if len(horas_inicio_validas) > 0:
    print(f'Hora inicio más temprana: {horas_inicio_validas.min()}')
if len(horas_fin_validas) > 0:
    print(f'Hora fin más tardía: {horas_fin_validas.max()}')
print()

print('=== VERIFICACIÓN DE CALIDAD DE DATOS ===')
print(f'Registros con doctor nulo: {df["doctor"].isnull().sum()}')
print(f'Registros con área nula: {df["area"].isnull().sum()}')
print(f'Registros con efector nulo: {df["efector"].isnull().sum()}')
print(f'Registros con hora_inicio nula: {df["hora_inicio"].isnull().sum()}')
print(f'Registros con hora_fin nula: {df["hora_fin"].isnull().sum()}')
