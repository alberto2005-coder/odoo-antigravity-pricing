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
Si tu servidor se enfrenta a bloqueos de IP (Error 403 / Captchas) de Amazon o Google:
1. Activa el modo desarrollador.
2. Ve a Ajustes > Técnico > **Parámetros del Sistema**.
3. Añade una nueva clave llamada `dynamic_pricing.proxy_url` y asigna como valor tu servidor Proxy o servicio como ScrapingBee (ej. `http://usuario:contraseña@ip_proxy:puerto`).

## 📊 Visualización de Resultados
Cada producto tiene un nuevo botón inteligente (Smart Button) en la parte superior derecha **"Price Fluctuation"**. Al hacer clic, se abrirá un gráfico histórico con todos los saltos de precio aplicados por el sistema a ese producto.

---

**Autor:** Alberto Ortiz  
**Licencia:** LGPL-3  
**Categoría:** Sales / E-commerce
