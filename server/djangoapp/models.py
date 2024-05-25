from django.db import models
from django.utils.timezone import now


# Create your models here.

class CarMake(models.Model):
    name = models.CharField(null=False, max_length=50)
    description = models.CharField(null=True, max_length=500)

    def __str__(self):
        return self.name

# <HINT> Create a Car Model model `class CarModel(models.Model):`:

class CarModel(models.Model):
    # make = models.ForeignKey(CarMake, null=True, on_delete = models.CASCADE)
    car_make = models.ForeignKey(CarMake, null=True, on_delete=models.CASCADE)
    dealer_id = models.IntegerField()
    name = models.CharField(max_length=255)
    SEDAN = "Sedan"
    SUV = "SUV"
    WAGON = "WAGON"
    TYPE_CHOICES = (
        (SEDAN, "Sedan"),
        (SUV, "SUV"),
        (WAGON, "Wagon"),
    )
    model_type  = models.CharField(max_length=10, choices=TYPE_CHOICES)
    year = models.DateField()

    def __str__(self):
        return f"{self.car_make} {self.name} ({self.year})"

        
# <HINT> Create a plain Python class `CarDealer` to hold dealer data

# All fields are from dealerships document in cloudant
class CarDealer:

    def __init__(self, address, city, full_name, id, lat, long, short_name, st, zip):
        # Dealer address
        self.address = address
        # Dealer city
        self.city = city
        # Dealer Full Name
        self.full_name = full_name
        # Dealer id
        self.id = id
        # Location lat
        self.lat = lat
        # Location long
        self.long = long
        # Dealer short name
        self.short_name = short_name
        # Dealer state
        self.st = st
        # Dealer zip
        self.zip = zip

    def __str__(self):
        return "Dealer name: " + self.full_name


# <HINT> Create a plain Python class `DealerReview` to hold review data.

# All fields are from review documet in cloudant.
class DealerReview:

    def __init__(self, id, name, dealership, review, purchase, purchase_date, car_make, car_model, car_year, sentiment='neutral'):
        self.id = id
        self.name = name  # reviewer name
        self.dealership = dealership
        self.review = review  # reveiw text
        self.purchase = purchase  # Did the reviewer purchase the car? bool
        self.purchase_date = purchase_date
        self.car_make = car_make
        self.car_model = car_model
        self.car_year = car_year
        self.sentiment = sentiment  # Watson NLU sentiment analysis of review

        def __str__(self):
            return 'Reviewer: ' + self.name + ' Review: ' + self.review
