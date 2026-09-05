DjangoShopeCRUDS

A professional Django Product CMS built with Django and PostgreSQL.

The project provides a complete product management system with an administrative interface, inventory tracking, hierarchical product categories, tags, PostgreSQL full-text search, and a public product catalog.

Features

Product Management

- Create, update, and delete products through Django Admin.
- Product name, SKU, description, price, stock quantity, and status.
- Category and tag management.
- Automatic product updates reflected on the public catalog.

Inventory Management

- Stock In.
- Stock Out.
- Opening balance.
- Stock adjustment.
- Automatic stock quantity updates.
- Insufficient-stock protection.
- Low-stock detection.
- Bulk inventory update screen.
- Inventory transaction history.

Categories

- Hierarchical/nested categories.
- Parent-child relationships.
- Hierarchical category URLs.
- Category ordering.
- Drag-and-drop category ordering in the admin interface.

Tags

- Product tagging system.
- Tag-based product organization.
- Tags included in full-text search.

Advanced Search

The project uses PostgreSQL Full-Text Search instead of Elasticsearch.

Search covers:

- Product names
- SKU
- Product descriptions
- Category names
- Tags

A PostgreSQL "SearchVectorField" with a GIN index is used to provide fast search performance.

Public Catalog

- Product listing.
- Product detail pages.
- Category pages.
- Nested category URLs.
- Search.
- Pagination.
- Breadcrumb navigation.
- Active/inactive product filtering.

Testing

The project includes automated Django tests covering:

- Models
- Inventory services
- Public views
- Admin inventory views
- Search functionality
- Category functionality

Current test suite:

39 tests — all passing

The project achieved approximately 97% code coverage during development.

Performance

The public product search was tested against 5,000 products.

Measured result:

- Average response time: 61.81 ms
- Maximum measured response time: 89.04 ms

This is well below the project's target of 300 ms.

Demo Data

The project includes a reproducible Django management command for generating demo data:

python manage.py seed_demo

The command creates:

- 5,000 products
- Hierarchical categories
- Product tags
- Search vectors

Technology Stack

- Python
- Django
- PostgreSQL
- psycopg
- Django ORM
- PostgreSQL Full-Text Search
- HTML
- CSS
- JavaScript
- Django Admin
- Git

Installation

Clone the repository:

git clone <YOUR_GITHUB_REPOSITORY_URL>
cd DjangoShopeCRUDS

Create a virtual environment:

python -m venv .venv

Activate it:

source .venv/bin/activate

Install dependencies:

pip install -r requirements.txt

Configure the PostgreSQL database and environment variables.

Run migrations:

python manage.py migrate

Create demo data:

python manage.py seed_demo

Create an administrator:

python manage.py createsuperuser

Run the development server:

python manage.py runserver

Testing

Run the complete test suite:

python manage.py test apps.products.tests

Run coverage:

coverage run --source='apps' manage.py test apps.products.tests
coverage report -m

Project Structure

DjangoShopeCRUDS/
├── apps/
│   └── products/
│       ├── migrations/
│       ├── management/
│       ├── services/
│       ├── tests/
│       ├── admin.py
│       ├── admin_views.py
│       ├── apps.py
│       ├── forms.py
│       ├── models.py
│       ├── signals.py
│       ├── urls.py
│       └── views.py
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── manage.py
├── requirements.txt
└── README.md

License

This project is provided for educational and professional demonstration purposes.
