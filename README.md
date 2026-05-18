# Dynamic Competitor Pricing para Odoo

**Dynamic Competitor Pricing** es un módulo avanzado para Odoo (v17, 18 y 19) diseñado para automatizar y optimizar la estrategia de precios de tu e-commerce o inventario mediante el scraping de precios de la competencia.

## 🚀 Características Principales

*   **Scraping Automatizado:** Extracción periódica de los precios de la competencia (ej. Amazon, Google Shopping, entre otros).
*   **Reglas de Precio Inteligentes:** Posibilidad de ajustar automáticamente el precio de tu producto para igualar a la competencia, ser un porcentaje más barato, o reducir el precio por un importe fijo.
*   **Protección de Margen (Safety Net):** Nunca venderás a pérdida. El sistema frena la bajada de precios si el cálculo sugiere un precio inferior al Coste (`standard_price`) + el Margen Mínimo Configurado.
*   **Alertas de Fluctuación Crítica:** Genera avisos y **actividades To-Do** de Odoo automáticamente si un competidor cambia su precio por encima de un umbral establecido (ej. 15%).
*   **ROI de Estrategia de Ventas:** Panel analítico integrado que compara ventas y facturación en el período activo vs. el mismo período anterior sin la regla activa.
*   **Gestión Masiva (CSV):** Asistente integrado para importar miles de URLs de competidores y listado centralizado para exportación directa a Excel.
*   **Histórico y Auditoría:** Gráficos integrados en el dashboard del producto y registro auditable de todos los cambios de precios (Cuándo, cuánto, y por qué).
*   **Evitación de Bloqueos (Throttling & Proxies):** Rotación automática de User-Agents, retrasos aleatorios (throttling) entre peticiones y soporte para añadir Proxies mediante parámetros del sistema.

## ⚙️ Configuración y Uso

### 1. Activar precios dinámicos por producto
Ve a Ventas > Productos y abre cualquier producto (Template). Verás una nueva pestaña llamada **"Dynamic Competitor Pricing"**.
- Activa el interruptor **Enable Dynamic Pricing**.
- Establece tu **Minimum Margin (%)** (Margen Mínimo sobre coste).
- Selecciona tu **Adjustment Rule** (Regla de Ajuste: e.g. `Lowest competitor - X%`).
- Establece el **Alert Threshold (%)** (Umbral de Alerta, por defecto al `15.0%`).

### 2. Añadir a la Competencia
En la misma pestaña, añade las URLs de la competencia en la sección **Competitor URLs**. Selecciona la plataforma y pega la URL de su ficha de producto.

### 3. Automatización (CRON)
El módulo instala automáticamente una acción planificada (CRON) llamada `Dynamic Pricing: Update Dynamic Prices`. Por defecto, se ejecuta una vez al día de madrugada, extrayendo los precios y ajustando el `list_price` de todo el catálogo activo.

## 📊 Visualización de Resultados y Análisis ROI
Cada producto con precios dinámicos activos dispone de herramientas analíticas de última generación:
1. **Historial de Precios:** Un botón inteligente (Smart Button) **"Price Fluctuation"** en la parte superior derecha abre un gráfico histórico con todos los saltos de precio aplicados por el sistema.
2. **Impacto en Ventas (ROI):** En la pestaña "Dynamic Competitor Pricing" se despliega un panel de rendimiento de ventas que cruza datos en tiempo real con el módulo de `sale`, informándote de las unidades vendidas, ingresos acumulados e incremento porcentual frente al periodo equivalente anterior.

## 📥 Gestión Masiva de Catálogos (CSV/Excel)
Para inicializar de forma instantánea catálogos de gran envergadura:
1. Dirígete a **Ventas > Productos > Import Competitor URLs**.
2. Sube un archivo CSV con las columnas `sku` (referencia interna), `platform` y `url`. El asistente se encargará del resto de forma inteligente.
3. Ve a **Ventas > Productos > Competitor URLs** para ver el catálogo consolidado de enlaces de competidores y usar la herramienta de exportación nativa de Odoo para obtener plantillas o informes detallados.

## 🔔 Alertas Activas de Competidores
Si un competidor rompe los precios o los sube por encima del porcentaje configurado en **Alert Threshold (%)**:
* Se registra un log destacado de advertencia en el **chatter del producto**.
* Se crea automáticamente una **actividad de Odoo (To-Do)** asignada al administrador responsable del producto para que pueda tomar decisiones estratégicas de inmediato.

## 🛠 Configuración Avanzada Técnica
Para evitar bloqueos de IP (Error 403 / Captchas) y renderizar webs modernas (SPAs):
1. Activa el modo desarrollador en Odoo.
2. Ve a Ajustes > Técnico > **Parámetros del Sistema**.
3. Añade cualquiera de los siguientes parámetros según tus necesidades:
   - `dynamic_pricing.proxy_url`: Tu servidor Proxy (ej. `http://usuario:contraseña@ip_proxy:puerto`).
   - `dynamic_pricing.api_provider`: `scrapingbee` o `zenrows` para delegar el scraping.
   - `dynamic_pricing.api_key`: Tu clave de API privada para el proveedor elegido.
   - `dynamic_pricing.render_js`: Escribe `True` si necesitas que el proveedor renderice el JavaScript (ideal para SPAs y webs React/Vue).

> **Eficiencia Multi-hilo:** El CRON está optimizado con **Multi-Threading** (`ThreadPoolExecutor`). Extrae múltiples URLs de un mismo producto en paralelo, acelerando radicalmente la ejecución en catálogos inmensos.

---

**Autor:** Alberto Ortiz  
**Licencia:** LGPL-3  
**Categoría:** Sales / E-commerce
