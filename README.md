# Aixpointpro – Cálculo Lógico de Participaciones en Startups

Aplicación desarrollada en Streamlit para calcular de forma lógica, transparente y visual las participaciones societarias en proyectos emprendedores. Incluye una estimación de reparto por bloques (idea, gestión, inversión...) y un módulo para inversores con cálculo automático de participación en función de la valoración de la empresa.

## Características principales

- Reparto por bloques ponderados:
  - Concepto e IP Fundacional
  - Inversión Económica Inicial
  - Operaciones y Gestión
  - Estrategia y Marketing

- % blindado configurable por socio
- Visualización interactiva en gráfico circular
- Módulo de cálculo de participación para inversores
- Exportación de resultados a CSV

##  Tecnologías

- Python
- Streamlit
- Pandas
- Matplotlib

##  Requisitos

Asegúrate de tener las siguientes dependencias (usadas en `requirements.txt`):

```
streamlit
pandas
matplotlib
```

##  Cómo ejecutar localmente

```bash
# Clona el repo
git clone https://github.com/jmarti-ops/Aixpointpro.git
cd Aixpointpro

# Instala dependencias
pip install -r requirements.txt

# Lanza la app
streamlit run app_reparto_full.py
```

## 🌐 Despliegue en Streamlit Cloud

Puedes desplegar fácilmente esta app en [streamlit.io](https://share.streamlit.io) conectando este repositorio y especificando como archivo principal `app_reparto_full.py`.

---

Desarrollado con  por Jordi Martí.
