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

## ¿Cómo funciona?

El motor analiza cada grupo de elementos del modelo IFC en tres pasos:

1. **Lee y agrupa los elementos** del archivo IFC por tipo, material y nombre.
2. **Aplica reglas deterministas** basadas en el tipo IFC y la disciplina del modelo. Si una regla coincide, la confianza es del 95%.
3. **Si ninguna regla aplica**, usa inteligencia semántica: compara el elemento con los 2 712 códigos Ss y 8 441 códigos Pr oficiales de Uniclass y elige el más parecido.

El **nivel de confianza** final es el mínimo entre la confianza del código Ss y el código Pr. Si es menor al 75%, el elemento se marca como **⚠️ Revisar** para revisión manual.

---

## Instalación — solo la primera vez

### Requisito previo: instalar Python

Si no tienes Python instalado:

1. Ve a [python.org/downloads](https://www.python.org/downloads/) y descarga la versión más reciente.
2. Ejecuta el instalador.
3. **Importante:** marca la casilla **"Add Python to PATH"** antes de hacer clic en Install.

---

### Paso 1 — Descargar el código

En esta página haz clic en el botón verde **Code → Download ZIP** y extrae la carpeta en tu computador (por ejemplo en el Escritorio).

---

### Paso 2 — Descargar el modelo de IA

El modelo de lenguaje especializado en construcción se distribuye por separado por su tamaño (~105 MB).

1. En esta página busca la sección **Releases** en el panel derecho y haz clic en ella.
2. Abre el release **"Modelo Embedding V01"** y descarga `model_package.zip`.
3. Abre el ZIP — verás dos carpetas adentro: `models/` y `data/`.
4. Copia **el contenido** de esas dos carpetas dentro de la carpeta del proyecto que descargaste en el Paso 1.

> ⚠️ **Importante:** no copies la carpeta `model_package` completa — copia lo que hay **dentro** de ella (`models/` y `data/`). Si Windows pregunta si deseas fusionar carpetas, haz clic en **Sí**.

Al terminar, la carpeta del proyecto debe verse así:

```
UNIBIMUniclassClassifier/
├── models/
│   └── construction_embedding_model/   ← vino del ZIP
├── data/
│   └── processed/                      ← vino del ZIP
├── app.py
├── setup.bat
├── run.bat
└── ...
```

---

### Paso 3 — Instalar dependencias

Abre la carpeta del proyecto y haz doble clic en **`setup.bat`**.

Se abrirá una ventana negra que instalará todo automáticamente. Espera a que termine y ciérrala.

---

### Paso 4 — (Opcional) Agregar tablas Uniclass

Para que el reporte muestre las descripciones completas de los códigos, coloca los archivos Excel oficiales de Uniclass 2015 dentro de la carpeta `data/uniclass/`:

```
data/uniclass/
├── Uniclass2015_EF_v1_16.xlsx
├── Uniclass2015_Ss_v1_40.xlsx
└── Uniclass2015_Pr_v1_40.xlsx
```

Descárgalos gratis desde [uniclass.thenbs.com](https://uniclass.thenbs.com).

> Sin estos archivos la herramienta igualmente clasifica y asigna los códigos — solo no mostrará las descripciones de texto.

---

## Cómo usar la aplicación

### Paso 1 — Abrir la aplicación

Haz doble clic en **`run.bat`**.

Se abrirá una ventana negra y unos segundos después el navegador se abrirá automáticamente en `http://localhost:8501`.

> Mantén la ventana negra abierta mientras usas la aplicación. Si la cierras, la aplicación se detiene.

---

### Paso 2 — Subir los modelos IFC

En el panel lateral izquierdo haz clic en **"Modelos IFC"** y selecciona uno o más archivos `.ifc`.

La herramienta detecta automáticamente la disciplina desde el nombre del archivo:

| El nombre del archivo contiene | Disciplina detectada |
|-------------------------------|----------------------|
| `IFC-EST-...` | Estructural |
| `IFC-HVAC-...` | Climatización |
| `IFC-ELE-...` | Eléctrico |
| `IFC-SAN-...` | Sanitario |
| `IFC-PCI-...` | Protección contra incendio |
| `IFC-ARQ-...` | Arquitectura |

---

### Paso 3 — Clasificar

Haz clic en **▶ Clasificar** en el panel lateral y espera. El tiempo depende del tamaño del modelo.

---

### Paso 4 — Revisar resultados

Al terminar verás:

- **Métricas** — grupos clasificados, porcentaje OK / Revisar, confianza promedio.
- **Pestaña Resumen** — gráficas por estado y dominio.
- **Pestaña Detalle** — tabla completa con códigos EF, Ss y Pr por elemento.
- **Pestaña Metodología** — explicación de cómo funciona el motor.

---

### Paso 5 — Descargar el reporte

Haz clic en **⬇️ Descargar** para obtener un Excel formateado con colores, encabezados y filtros automáticos.

---

## Estructura del proyecto

```
├── app.py                           # Aplicación web (Streamlit)
├── setup.bat                        # Instalador de dependencias (Windows)
├── run.bat                          # Lanzador de la aplicación (Windows)
├── requirements.txt                 # Lista de dependencias Python
├── engine/                          # Motor de clasificación
├── data/
│   ├── processed/                   # Índices de vectores (del ZIP del modelo)
│   └── uniclass/                    # Tablas Excel Uniclass (el usuario debe aportar)
└── models/
    └── construction_embedding_model/ # Modelo de lenguaje (del ZIP del modelo)
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
