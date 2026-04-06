# 🏗️ UNIBIM Uniclass Classifier

**Clasificación automática de modelos BIM (IFC) según Uniclass 2015**

Desarrollado por el equipo **UNIBIM** · Zigurat Institute · 2026

---

## ¿Qué hace esta herramienta?

Esta aplicación lee archivos de modelo BIM en formato **IFC** y asigna automáticamente códigos de clasificación **Uniclass 2015** a cada elemento constructivo. El resultado es un reporte en Excel con los códigos EF, Ss y Pr de cada elemento, junto con un indicador de confianza.

### ¿Qué es Uniclass 2015?

Es el sistema de clasificación de la construcción más usado en proyectos BIM. Organiza los elementos en tres categorías:

| Código | Nombre | Ejemplo |
|--------|--------|---------|
| **EF** | Entity Facets — tipo de entidad | Elemento estructural, instalación, cerramiento |
| **Ss** | Systems — sistema o subsistema | Sistema de climatización, estructura de hormigón |
| **Pr** | Products — producto específico | Viga de acero, tubería PVC, luminaria LED |

---

## ¿Cómo funciona el motor de clasificación?

El motor analiza cada grupo de elementos del modelo IFC en tres pasos:

1. **Lee y agrupa los elementos** del archivo IFC por tipo, material y nombre.
2. **Aplica reglas deterministas** — conjuntos de reglas basadas en el tipo IFC y la disciplina del modelo (estructural, HVAC, eléctrico, etc.). Si una regla coincide, la confianza es del 95%.
3. **Si ninguna regla aplica**, usa inteligencia semántica: convierte el elemento en una frase descriptiva, la compara con los 2 712 códigos Ss y 8 441 códigos Pr oficiales de Uniclass usando similitud semántica, y elige el más parecido.

El **nivel de confianza** final es el mínimo entre la confianza del código Ss y el código Pr. Si es menor al 75%, el elemento se marca como **⚠️ Revisar** para revisión manual.

---

## Instalación paso a paso

> **Requisitos previos:** tener Python instalado en tu computador.  
> Si no lo tienes, descárgalo desde [python.org](https://www.python.org/downloads/) — marca la opción **"Add Python to PATH"** al instalar.

### Paso 1 — Descargar el código

Haz clic en el botón verde **Code → Download ZIP** en esta página y extrae la carpeta en tu computador.

O si usas Git:
```
git clone https://github.com/<usuario>/HybridSemanticBIMClassification.git
```

### Paso 2 — Descargar el modelo de inteligencia artificial

El modelo de lenguaje especializado en construcción se distribuye por separado por su tamaño.

1. Ve a la sección **[Releases](../../releases)** de este repositorio.
2. Descarga el archivo `model_package.zip` del release **"Modelo Embedding V01"**.
3. Extrae el ZIP **dentro de la carpeta del proyecto** — mantén la estructura de carpetas tal como viene.

Después de extraer, deberías ver estas carpetas:
```
HybridSemanticBIMClassification/
├── models/
│   └── construction_embedding_model/   ← del ZIP
├── data/
│   └── processed/                      ← del ZIP
└── ...
```

### Paso 3 — Instalar dependencias

En Windows, haz doble clic en el archivo **`setup.bat`**.

Espera a que termine — verás el mensaje "Setup completado correctamente".

### Paso 4 — (Opcional) Agregar tablas Uniclass

Para que el reporte muestre las descripciones completas de los códigos, coloca los archivos Excel oficiales de Uniclass 2015 dentro de la carpeta `data/uniclass/`:

```
data/uniclass/
├── Uniclass2015_EF_v1_16.xlsx
├── Uniclass2015_Ss_v1_40.xlsx
└── Uniclass2015_Pr_v1_40.xlsx
```

Puedes descargarlos gratis desde [uniclass.thenbs.com](https://uniclass.thenbs.com).  
> Sin estos archivos la herramienta igualmente clasifica y asigna los códigos — solo no mostrará las descripciones de texto.

---

## Cómo usar la aplicación

### Paso 1 — Abrir la aplicación

Haz doble clic en **`run.bat`**. Se abrirá una ventana negra y unos segundos después se abrirá la aplicación en tu navegador.

> Mantén la ventana negra abierta mientras usas la aplicación. Si la cierras, la aplicación se detiene.

### Paso 2 — Subir los modelos IFC

En el panel lateral izquierdo, haz clic en **"Modelos IFC"** y selecciona uno o más archivos `.ifc`. La herramienta detecta automáticamente la disciplina desde el nombre del archivo:

| Nombre del archivo contiene | Disciplina detectada |
|-----------------------------|----------------------|
| `IFC-EST-...` | Estructural |
| `IFC-HVAC-...` | Climatización |
| `IFC-ELE-...` | Eléctrico |
| `IFC-SAN-...` | Sanitario |
| `IFC-PCI-...` | Protección contra incendio |
| `IFC-ARQ-...` | Arquitectura |

### Paso 3 — Clasificar

Haz clic en el botón **▶ Clasificar** en el panel lateral. El proceso puede tardar unos minutos dependiendo del tamaño del modelo.

### Paso 4 — Revisar resultados

Una vez clasificado verás:

- **Métricas** — número de grupos clasificados, porcentaje OK / Revisar, confianza promedio.
- **Pestaña Resumen** — gráficas por estado y dominio, confianza por modelo, códigos Ss más frecuentes.
- **Pestaña Detalle** — tabla completa con todos los grupos y sus códigos EF, Ss y Pr.
- **Pestaña Metodología** — explicación de cómo funciona el motor.

### Paso 5 — Descargar el reporte

Haz clic en **⬇️ Descargar** para obtener un archivo Excel formateado con:
- Portada con nombre del proyecto y autores
- Colores por estado (verde = OK, ámbar = Revisar)
- Encabezados claros y columnas ajustadas
- Filtros automáticos

---

## Estructura del proyecto

```
├── app.py                           # Aplicación web (Streamlit)
├── setup.bat                        # Instalador de dependencias (Windows)
├── run.bat                          # Lanzador de la aplicación (Windows)
├── requirements.txt                 # Lista de dependencias Python
│
├── engine/                          # Motor de clasificación
│   ├── rules/                       # Reglas deterministas (EF, Ss, Pr)
│   └── semantic/                    # Clasificador por similitud semántica
│
├── data/
│   ├── processed/                   # Índices de vectores pre-construidos (del ZIP)
│   └── uniclass/                    # Tablas Excel Uniclass (el usuario debe aportar)
│
└── models/
    └── construction_embedding_model/ # Modelo de lenguaje fine-tuned (del ZIP)
```

---

## Autores

**Equipo UNIBIM · Zigurat Institute · 2026**

| Rol | Nombre |
|-----|--------|
| Integrante | Alejandro Martínez |
| Integrante | Camilo Torres |
| Integrante | Gissela Chicaiza |
| Integrante | Maite Castiñeira |
| Integrante | Pablo Pinuer |
| Integrante | Santiago Martínez Chabbert |
| Tutor | Evelio Sanchez |

© 2026 UNIBIM. Todos los derechos reservados.