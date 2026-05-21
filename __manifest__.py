{
    'name': 'Dynamic Competitor Pricing',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Dynamic pricing based on competitor scraping',
    'description': """
        Dynamic Competitor Pricing Module
        - Scrapes competitor prices
        - Updates product list price based on defined rules and margins
    """,
    'author': 'Alberto Ortiz',
    'depends': ['product', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'data/cron_data.xml',
        'views/product_template_views.xml',
        'views/dynamic_price_log_views.xml',
        'views/import_competitor_url_views.xml',
        'views/dynamic_pricing_dashboard_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
