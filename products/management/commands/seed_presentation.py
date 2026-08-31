"""
Backfills the storefront presentation fields on a handful of existing services
and products so the shop and services pages have real copy to render.

Only fills fields that are still empty, so anything edited in the admin is left
alone. Safe to re-run.

    python manage.py seed_presentation
    python manage.py seed_presentation --overwrite
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from products.models import Product
from services.models import Service

BLUSH = "var(--gradient-blush)"
SAGE = "var(--gradient-sage)"
LILAC = "var(--gradient-lilac)"

# Keyed by name so the seed does not depend on primary keys.
SERVICE_COPY = {
    "Manicure": {
        "tagline": "Shaped, buffed and cared for",
        "gradient": BLUSH,
        "includes": [
            "Nail shaping and filing",
            "Cuticle care",
            "Hand massage",
            "Polish of your choice",
        ],
    },
    "Pedicure": {
        "tagline": "A proper reset for tired feet",
        "gradient": SAGE,
        "includes": [
            "Warm soak and scrub",
            "Nail shaping and cuticle care",
            "Callus softening",
            "Foot massage and polish",
        ],
    },
    "Facial": {
        "tagline": "Deep cleanse, tuned to your skin",
        "gradient": LILAC,
        "includes": [
            "Skin consultation",
            "Cleanse and exfoliation",
            "Steam and extraction",
            "Mask, serum and moisturiser",
        ],
    },
    "Hair Spa": {
        "tagline": "Scalp-first conditioning ritual",
        "gradient": SAGE,
        "includes": [
            "Scalp analysis",
            "Oil massage",
            "Steam treatment",
            "Wash and blow dry",
        ],
    },
    "Hair Styling": {
        "tagline": "Blow-dry and finish for any occasion",
        "gradient": BLUSH,
        "includes": [
            "Consultation on the look",
            "Wash and prep",
            "Heat styling",
            "Finishing spray",
        ],
    },
}

PRODUCT_COPY = {
    "Face Wash": {
        "tagline": "Daily gentle cleanser",
        "concern": "Cleansing",
        "size": "150 ml",
        "gradient": LILAC,
        "bestseller": True,
        "ingredients": "Aqua, Glycerin, Coco-Glucoside, Panthenol, Citric Acid.",
        "details": [
            "Soap-free, non-drying formula",
            "Suits daily morning and evening use",
            "Rinses clean without residue",
        ],
    },
    "Moisturizer": {
        "tagline": "Lightweight everyday hydration",
        "concern": "Hydration",
        "size": "100 ml",
        "gradient": BLUSH,
        "ingredients": "Aqua, Glycerin, Shea Butter, Tocopherol, Dimethicone.",
        "details": [
            "Absorbs without a greasy finish",
            "Layers well under sunscreen",
            "Fragrance-light",
        ],
    },
    "Shampoo": {
        "tagline": "Everyday cleansing for soft hair",
        "concern": "Cleansing",
        "size": "250 ml",
        "gradient": SAGE,
        "bestseller": True,
        "ingredients": "Aqua, Sodium Laureth Sulfate, Cocamidopropyl Betaine, Panthenol.",
        "details": [
            "Balanced lather, easy to rinse",
            "Safe for colour-treated hair",
            "Pairs with the matching conditioner",
        ],
    },
    "Hair Serum": {
        "tagline": "Frizz control and shine",
        "concern": "Repair",
        "size": "100 ml",
        "gradient": BLUSH,
        "ingredients": "Cyclopentasiloxane, Dimethiconol, Argan Oil, Tocopherol.",
        "details": [
            "Smooths flyaways on damp or dry hair",
            "Adds shine without weighing hair down",
            "A few drops is enough",
        ],
    },
    "Sunscreen": {
        "tagline": "Broad-spectrum daily shield",
        "concern": "Protection",
        "size": "50 ml",
        "gradient": LILAC,
        "bestseller": True,
        "ingredients": "Aqua, Homosalate, Octocrylene, Zinc Oxide, Glycerin.",
        "details": [
            "No white cast on reapplication",
            "Sits well under makeup",
            "Reapply every few hours outdoors",
        ],
    },
}


class Command(BaseCommand):
    help = "Backfill storefront presentation fields on 5 services and 5 products."

    def add_arguments(self, parser):
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Replace values that are already set instead of only filling blanks.",
        )

    def handle(self, *args, **options):
        overwrite = options["overwrite"]

        with transaction.atomic():
            services = self._apply(Service, SERVICE_COPY, overwrite)
            products = self._apply(Product, PRODUCT_COPY, overwrite)

        self.stdout.write(
            self.style.SUCCESS(
                f"Updated {services} service(s) and {products} product(s)."
            )
        )

    def _apply(self, model, copy_by_name, overwrite):
        updated = 0

        for name, values in copy_by_name.items():
            obj = model.objects.filter(name=name).first()
            if obj is None:
                self.stdout.write(
                    self.style.WARNING(f"  skipped: no {model.__name__} named {name!r}")
                )
                continue

            changed = []
            for field, value in values.items():
                current = getattr(obj, field)
                # Empty string, empty list and False all count as "not set yet".
                if not overwrite and current not in ("", [], False, None):
                    continue
                if current == value:
                    continue
                setattr(obj, field, value)
                changed.append(field)

            if changed:
                obj.save(update_fields=[*changed, "updated_at"])
                updated += 1
                self.stdout.write(f"  {model.__name__} {name}: {', '.join(changed)}")

        return updated
