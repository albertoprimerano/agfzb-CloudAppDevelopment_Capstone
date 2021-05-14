from django.db import models

# Internal Data Stored
class StoreRelevantDate(models.Model):
    review_id = models.IntegerField(default=10)



# Car Make
class CarMake(models.Model):
    name = models.CharField(null=False, max_length=30)
    description = models.CharField(null=False, max_length=500)

    def __str__(self):
        return self.name + " " + self.description


# Car Model
class CarModel(models.Model):
    SEDAN = 'Sedan'
    SUW = 'SUW'
    WAGON = 'Station Wagon'
    COUPE = 'Coupe'
    CONVERTIBLE = 'Convertible'
    MINIVAN = 'Minivan'
    CAR_TYPE_CHOICE = [
        (SEDAN, 'Sedan'),
        (SUW, 'SUW'),
        (WAGON, 'Station Wagon'),
        (COUPE, 'Coupe'),
        (CONVERTIBLE, 'Convertible'),
        (MINIVAN, 'Minivan'),
    ]
    name = models.CharField(null=False, max_length=30)
    dealer_id = models.IntegerField()
    type = models.CharField(
        null=False,
        max_length=20,
        choices=CAR_TYPE_CHOICE,
        default=SEDAN
    )
    year = models.DateField(null=True)
    car_make = models.ForeignKey(CarMake, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name + " " + self.type + " " + str(self.year)


# Car Dealer
class CarDealer:
    POSITIVE = 'positive'
    NEGATIVE = 'negative'
    NEUTRAL = 'neutral'
    SENTIMENT_CHOICE = [(POSITIVE, 'positive'), (NEGATIVE, 'negative'), (NEUTRAL, 'neutral')]
    address = models.CharField(max_length=256)
    sentiment = models.CharField(null=False, max_length=20, choices=SENTIMENT_CHOICE, default=NEUTRAL)

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


# Car Review
class CarReview:

    def __init__(self, dealership, name, purchase, review, purchase_date, car_make, car_model, car_year, sentiment, id):
        self.dealership = dealership
        self.name = name
        self.purchase = purchase
        self.id = id
        self.review = review
        self.purchase_date = purchase_date
        self.car_make = car_make
        self.car_model = car_model
        self.car_year = car_year
        self.sentiment = sentiment

    def __str__(self):
        return "Review : " + self.id + " " + self.purchase
