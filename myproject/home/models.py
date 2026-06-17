from django.contrib.auth.models import User
from django.db import models

# Category Model
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# Menu Item Model
class MenuItem(models.Model):


    FOOD_TYPE = [
        ('Veg', 'Veg'),
        ('Non-Veg', 'Non-Veg'),
    ]

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='items'
    )


    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)

    food_type = models.CharField(
        max_length=10,
        choices=FOOD_TYPE,
         default='Veg'
    )

    image = models.ImageField(upload_to='menu_images/')
    available = models.BooleanField(default=True)

class Cart(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    item = models.ForeignKey(
        MenuItem,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(default=1)
    
    def total_price(self):
        return self.item.price * self.quantity
    
    def __str__(self):
        return self.item.name

class OTP(models.Model):
    mobile = models.CharField(max_length=15)
    otp = models.CharField(max_length=6)

    def __str__(self):
        return self.mobile
    
class UserProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    phone = models.CharField(max_length=15)

    address = models.CharField(max_length=100, default="")

    dining_option = models.CharField(
        max_length=20,
        default=""
    )

    payment_status = models.CharField(
        max_length=20,
        default="Pending"
    )

    def __str__(self):
        return self.user.username
    
class Reservation(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    seat_number = models.CharField(
        max_length=20
    )

    reservation_date = models.DateField(
        null=True,
        blank=True
    )

    reservation_time = models.TimeField(
        null=True,
        blank=True
    )

    guests = models.IntegerField(
        default=1
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ('Occupied', 'Occupied'),
            ('Available', 'Available')
        ],
        default='Occupied'
    )

    
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            self.user.username +
            " - " +
            self.seat_number
        )

class Order(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_status = models.CharField(
        max_length=30
    )
    status = models.CharField(
        max_length=20,
        default="Active"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.user.username
    

class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )

    item_name = models.CharField(
        max_length=100
    )

    quantity = models.IntegerField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    def __str__(self):
        return self.item_name
    
class OTP(models.Model):

    email = models.EmailField()

    otp = models.CharField(
        max_length=6
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return self.email