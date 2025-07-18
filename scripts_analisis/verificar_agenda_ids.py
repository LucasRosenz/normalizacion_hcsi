import pandas as pd

def verificar_agenda_ids():
    """
    Verifica que las agendas duplicadas ahora se cuenten correctamente
    usando el nuevo campo agenda_id
    """
    print("🔍 VERIFICACIÓN DE AGENDA_IDs")
    print("=" * 60)
    
    try:
        # Leer la base procesada
        df = pd.read_csv('datos/csv_procesado/agendas_consolidadas.csv')
        
        # Verificar que existe la columna agenda_id
        if 'agenda_id' not in df.columns:
            print("❌ La columna 'agenda_id' no existe en el CSV")
            print("Columnas disponibles:", list(df.columns))
            return
        
        print("✅ La columna 'agenda_id' existe en el CSV")
        
        # Análisis general
        total_registros = len(df)
        agendas_unicas_por_id = df['agenda_id'].nunique()
        agendas_unicas_por_nombre = df['nombre_original_agenda'].nunique()
        
        print(f"\n📊 RESUMEN GENERAL:")
        print(f"   • Total registros: {total_registros}")
        print(f"   • Agendas únicas por ID: {agendas_unicas_por_id}")
        print(f"   • Agendas únicas por nombre: {agendas_unicas_por_nombre}")
        print(f"   • Diferencia (IDs vs nombres): {agendas_unicas_por_id - agendas_unicas_por_nombre}")
        
        # Análisis específico de CAPS San Isidro Labrador
        caps_si = df[df['efector'] == 'CAPS San Isidro Labrador']
        
        if len(caps_si) > 0:
            caps_registros = len(caps_si)
            caps_agendas_por_id = caps_si['agenda_id'].nunique()
            caps_agendas_por_nombre = caps_si['nombre_original_agenda'].nunique()
            
            print(f"\n🎯 CAPS SAN ISIDRO LABRADOR:")
            print(f"   • Total registros: {caps_registros}")
            print(f"   • Agendas únicas por ID: {caps_agendas_por_id}")
            print(f"   • Agendas únicas por nombre: {caps_agendas_por_nombre}")
            print(f"   • Diferencia: {caps_agendas_por_id - caps_agendas_por_nombre}")
            
            # Verificar si ahora tenemos 66 agendas
            if caps_agendas_por_id == 66:
                print(f"   ✅ ¡CORRECTO! Ahora tenemos 66 agendas únicas")
            else:
                print(f"   ⚠️  Esperábamos 66, pero tenemos {caps_agendas_por_id}")
            
            # Mostrar las agendas duplicadas
            contador_nombres = caps_si['nombre_original_agenda'].value_counts()
            duplicados = contador_nombres[contador_nombres > 1]
            
            if len(duplicados) > 0:
                print(f"\n📋 AGENDAS CON MISMO NOMBRE:")
                for nombre, cantidad in duplicados.items():
                    agenda_ids = caps_si[caps_si['nombre_original_agenda'] == nombre]['agenda_id'].unique()
                    print(f"   • '{nombre}': {cantidad} registros")
                    print(f"     └─ IDs únicos: {len(agenda_ids)} ({', '.join(sorted(agenda_ids))})")
        
        # Verificar todos los centros
        print(f"\n📊 CONTEO POR CENTRO:")
        resumen_por_centro = df.groupby('efector').agg({
            'agenda_id': 'nunique',
            'nombre_original_agenda': 'nunique'
        }).reset_index()
        resumen_por_centro['diferencia'] = resumen_por_centro['agenda_id'] - resumen_por_centro['nombre_original_agenda']
        
        for _, row in resumen_por_centro.iterrows():
            efector = row['efector']
            ids_unicos = row['agenda_id']
            nombres_unicos = row['nombre_original_agenda']
            diferencia = row['diferencia']
            
            if diferencia > 0:
                print(f"   • {efector}: {ids_unicos} IDs, {nombres_unicos} nombres (+{diferencia} duplicados)")
            else:
                print(f"   • {efector}: {ids_unicos} agendas únicas")
        
        # Totales finales
        total_agenda_ids = resumen_por_centro['agenda_id'].sum()
        total_nombres = resumen_por_centro['nombre_original_agenda'].sum()
        diferencia_total = total_agenda_ids - total_nombres
        
        print(f"\n🎯 TOTALES FINALES:")
        print(f"   • Total agendas por ID: {total_agenda_ids}")
        print(f"   • Total agendas por nombre: {total_nombres}")
        print(f"   • Duplicados detectados: {diferencia_total}")
        
        if total_agenda_ids == 612:
            print(f"   ✅ ¡PERFECTO! Ahora tenemos exactamente 612 agendas únicas")
        else:
            print(f"   ⚠️  Esperábamos 612, pero tenemos {total_agenda_ids}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    verificar_agenda_ids()
