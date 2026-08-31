from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from accounts.models import RoleChoices
from appointments.models import Appointment, AppointmentStatus
from categories.models import Category
from customers.models import CustomerProfile
from orders.models import Order, OrderStatus
from payments.models import Payment, PaymentStatus
from products.models import Product
from services.models import Service, ServiceCategory
from staff.models import StaffProfile, StaffStatus

User = get_user_model()


class Command(BaseCommand):
    help = "Seed the database with sample salon data."

    def handle(self, *args, **options):
        self.stdout.write("Seeding database...")

        self.create_users()
        self.create_categories()
        self.create_services()
        self.create_products()
        self.create_sample_order()
        self.create_sample_appointment()

        self.stdout.write(self.style.SUCCESS("Database seeded successfully."))

    def create_users(self):
        if not User.objects.filter(role=RoleChoices.ADMIN).exists():
            User.objects.create_superuser(
                username="admin", email="admin@salon.com", password="admin12345", role=RoleChoices.ADMIN
            )
            self.stdout.write("  - Admin created (admin@salon.com / admin12345)")

        staff_list = [
            ("Priya", "Sharma", "priya@salon.com", "Nails", "Manicure, Pedicure, Nail Art"),
            ("Anjali", "Verma", "anjali@salon.com", "Facial", "Facial, Cleanup, Beauty Treatments"),
            ("Neha", "Singh", "neha@salon.com", "Hair", "Hair Spa, Hair Styling"),
            ("Sara", "Khan", "sara@salon.com", "Waxing", "Waxing"),
            ("Aisha", "Patel", "aisha@salon.com", "Makeup", "Makeup, Bridal Makeup, Party Makeup"),
        ]
        for first, last, email, dept, skills in staff_list:
            if not User.objects.filter(email=email).exists():
                user = User.objects.create_user(
                    username=email, email=email, password="staff12345",
                    first_name=first, last_name=last, role=RoleChoices.STAFF,
                )
                StaffProfile.objects.create(user=user, department=dept, skills=skills,
                                            experience_years=3, status=StaffStatus.AVAILABLE)
                self.stdout.write(f"  - Staff created ({email} / staff12345)")

        if not User.objects.filter(email="customer@salon.com").exists():
            user = User.objects.create_user(
                username="customer@salon.com", email="customer@salon.com",
                password="customer12345", first_name="Rohit", last_name="Kumar",
                role=RoleChoices.CUSTOMER, phone="9876543210",
            )
            CustomerProfile.objects.create(
                user=user, address="123 MG Road", city="Mumbai", state="Maharashtra",
                postal_code="400001",
            )
            self.stdout.write("  - Customer created (customer@salon.com / customer12345)")

    def create_categories(self):
        categories = [
            ("Skin Care", "Products for healthy skin"),
            ("Hair Care", "Shampoos, conditioners and hair products"),
            ("Nail Care", "Nail polish and nail care products"),
            ("Body Care", "Body lotions and creams"),
            ("Beauty Accessories", "Brushes, tools and accessories"),
        ]
        for name, desc in categories:
            Category.objects.get_or_create(name=name, defaults={"description": desc})
        self.stdout.write(f"  - {Category.objects.count()} product categories")

    def create_services(self):
        service_cats = [
            ("Nails", "Nail care services"),
            ("Facial", "Facial and skin services"),
            ("Hair", "Hair styling and treatment"),
            ("Waxing", "Waxing services"),
            ("Spa", "Spa and relaxation"),
            ("Beauty Care", "General beauty treatments"),
            ("Makeup", "Makeup and glam services"),
        ]
        for name, desc in service_cats:
            ServiceCategory.objects.get_or_create(name=name, defaults={"description": desc})

        services = [
            ("Manicure", "Nails", 45, 499, "Classic manicure"),
            ("Pedicure", "Nails", 60, 699, "Classic pedicure"),
            ("Manicure + Pedicure", "Nails", 90, 999, "Complete nail care"),
            ("Nail Art", "Nails", 60, 799, "Custom nail art designs"),
            ("Facial", "Facial", 60, 1299, "Glow facial treatment"),
            ("Cleanup", "Facial", 45, 899, "Basic facial cleanup"),
            ("Hair Spa", "Hair", 75, 1499, "Deep conditioning hair spa"),
            ("Hair Styling", "Hair", 60, 1099, "Blow dry and styling"),
            ("Waxing", "Waxing", 45, 899, "Full arm waxing"),
            ("Beauty Treatment", "Beauty Care", 90, 1999, "Premium beauty treatment"),
            ("Makeup", "Makeup", 75, 1799, "Soft glam and party makeup"),
        ]
        for name, cat, duration, price, desc in services:
            category = ServiceCategory.objects.get(name=cat)
            Service.objects.get_or_create(
                name=name,
                defaults={
                    "category": category, "duration_minutes": duration,
                    "price": price, "description": desc,
                },
            )
        self.stdout.write(f"  - {Service.objects.count()} services")

    def create_products(self):
        products = [
            ("Face Wash", "Skin Care", "FACEWASH-001", "Nivea", 199, 50),
            ("Moisturizer", "Skin Care", "MOIST-001", "Nivea", 299, 40),
            ("Shampoo", "Hair Care", "SHAMPOO-001", "Loreal", 399, 30),
            ("Conditioner", "Hair Care", "COND-001", "Loreal", 349, 30),
            ("Hair Serum", "Hair Care", "SERUM-001", "Loreal", 499, 20),
            ("Nail Polish", "Nail Care", "NAILPOL-001", "Mavala", 249, 60),
            ("Nail File Set", "Nail Care", "NAILSET-001", "Mavala", 149, 25),
            ("Body Lotion", "Body Care", "LOTION-001", "Vaseline", 229, 45),
            ("Sunscreen", "Skin Care", "SUNSC-001", "Lakme", 349, 35),
            ("Beauty Cream", "Skin Care", "CREAM-001", "Lakme", 399, 28),
        ]
        for name, cat, sku, brand, price, stock in products:
            category = Category.objects.get(name=cat)
            Product.objects.get_or_create(
                sku=sku,
                defaults={
                    "name": name, "category": category, "brand": brand,
                    "price": price, "stock_quantity": stock, "gst_tax": 5,
                },
            )
        self.stdout.write(f"  - {Product.objects.count()} products")

    def create_sample_order(self):
        customer = User.objects.get(email="customer@salon.com")
        if Order.objects.filter(customer=customer).exists():
            return

        product = Product.objects.first()
        order = Order.objects.create(
            order_number="ORD-SEED0001", customer=customer,
            shipping_address=customer.customer_profile.address,
            billing_address=customer.customer_profile.address,
            subtotal=product.final_price,
            tax_amount=product.final_price * product.gst_tax / 100,
            total_amount=product.final_price * (1 + product.gst_tax / 100),
            status=OrderStatus.PENDING, payment_status=PaymentStatus.PENDING,
        )
        from orders.models import OrderItem
        OrderItem.objects.create(
            order=order, product=product, product_name=product.name, quantity=1,
            unit_price=product.final_price,
            total_price=product.final_price * (1 + product.gst_tax / 100),
        )
        Payment.objects.create(user=customer, order=order, amount=order.total_amount,
                               status=PaymentStatus.PENDING)
        self.stdout.write("  - Sample order created")

    def create_sample_appointment(self):
        customer = User.objects.get(email="customer@salon.com")
        if Appointment.objects.filter(customer=customer).exists():
            return

        service = Service.objects.get(name="Manicure")
        from datetime import date, datetime
        from django.utils import timezone

        today = timezone.localdate()
        start = datetime.combine(today, datetime.strptime("10:00", "%H:%M").time())
        from datetime import timedelta
        end = start + timedelta(minutes=service.duration_minutes)

        Appointment.objects.create(
            appointment_number="APT-SEED0001",
            customer=customer,
            service=service,
            appointment_date=today,
            start_time=start.time(),
            end_time=end.time(),
            duration_minutes=service.duration_minutes,
            status=AppointmentStatus.PENDING,
        )
        self.stdout.write("  - Sample appointment created")
