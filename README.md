# Dynamic Competitor Pricing para Odoo

**Dynamic Competitor Pricing** es un módulo avanzado para Odoo (v17, 18 y 19) diseñado para automatizar y optimizar la estrategia de precios de tu e-commerce o inventario mediante el scraping de precios de la competencia.

## 🚀 Características Principales

*   **Scraping Automatizado:** Extracción periódica de los precios de la competencia (ej. Amazon, Google Shopping, entre otros).
*   **Reglas de Precio Inteligentes:** Posibilidad de ajustar automáticamente el precio de tu producto para igualar a la competencia, ser un porcentaje más barato, o reducir el precio por un importe fijo.
*   **Protección de Margen (Safety Net):** Nunca venderás a pérdida. El sistema frena la bajada de precios si el cálculo sugiere un precio inferior al Coste (`standard_price`) + el Margen Mínimo Configurado.
*   **Histórico y Auditoría:** Gráficos integrados en el dashboard del producto y registro auditable de todos los cambios de precios (Cuándo, cuánto, y por qué).
*   **Evitación de Bloqueos (Throttling & Proxies):** Rotación automática de User-Agents, retrasos aleatorios (throttling) entre peticiones y soporte para añadir Proxies mediante parámetros del sistema.

## ⚙️ Configuración y Uso

### 1. Activar precios dinámicos por producto
Ve a Ventas > Productos y abre cualquier producto (Template). Verás una nueva pestaña llamada **"Dynamic Competitor Pricing"**.
- Activa el interruptor **Enable Dynamic Pricing**.
- Establece tu **Minimum Margin (%)** (Margen Mínimo sobre coste).
- Selecciona tu **Adjustment Rule** (Regla de Ajuste: e.g. `Lowest competitor - X%`).

### 2. Añadir a la Competencia
En la misma pestaña, añade las URLs de la competencia en la sección **Competitor URLs**. Selecciona la plataforma y pega la URL de su ficha de producto.

### 3. Automatización (CRON)
El módulo instala automáticamente una acción planificada (CRON) llamada `Dynamic Pricing: Update Dynamic Prices`. Por defecto, se ejecuta una vez al día de madrugada, extrayendo los precios y ajustando el `list_price` de todo el catálogo activo.

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

## 📊 Visualización de Resultados
Cada producto tiene un nuevo botón inteligente (Smart Button) en la parte superior derecha **"Price Fluctuation"**. Al hacer clic, se abrirá un gráfico histórico con todos los saltos de precio aplicados por el sistema a ese producto.

---

**Autor:** Alberto Ortiz  
**Licencia:** LGPL-3  
**Categoría:** Sales / E-commerce
