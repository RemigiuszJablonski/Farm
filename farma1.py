import csv
import random
import tkinter as tk
from tkinter import ttk
import threading
import time
from PIL import Image, ImageTk
class Farm:
    def __init__(self):
        self.current_month = 0   # glowna klasa reprezentujaca farme
        self.money = 5000
        self.season = 1
        self.resources = {}
        self.total_resources_collected = {}  # Zmienne do sledzenia wartosci
        self.animals = {}
        self.max_animals = {}
        self.sickAnimals_count = {}
        self.crops = None
        self.total_medicines_used = 0

    def addAnimal(self, animal_type, quantity): # funkcja dodajaca zwierzeta
        if animal_type not in self.animals:
            self.animals[animal_type] = []
            resource_key = animal_type.__name__.lower() + "_resource"
            self.resources[resource_key] = 0
            self.total_resources_collected[resource_key] = 0  # wprowadzenie calkowitych zasobow
            self.max_animals[animal_type] = animal_type.default_capacity
            self.sickAnimals_count[animal_type] = 0

        for i in range(quantity):
            if len(self.animals[animal_type]) < self.max_animals[animal_type]:
                self.animals[animal_type].append(animal_type())

    def addCrops(self, crops):          # dodawanie upraw
        self.crops = crops

    def addSickCount(self, animal_type):              # dodawanie liczby chorych zwierzat
        self.sickAnimals_count[animal_type] += 1

    def decSickCount(self, animal_type):
        self.sickAnimals_count[animal_type] -= 1     # odejmowanie liczby chorych zwierzat

    def MonthlyEvents(self):          # wydarzenia miesieczne na farmie
        self.current_month += 1
        for animal_type, animals_list in self.animals.items():
            for animal in animals_list[:]:
                animal.age += 1
                farm.money -= animal.costOfLiving

                # CHOROBY
                if not animal.is_sick and random.random() < animal.chanceOfSickness:
                    animal.is_sick = True

                if animal.is_sick:
                    for other_animal in animals_list:
                        if not other_animal.is_sick and random.random() < animal.chanceOfInfection:
                            other_animal.is_sick = True
                            self.addSickCount(animal_type)

                # RODZENIE
                if animal.is_pregnant:
                    animal.pregnancyTime += 1
                    animal.check_pregnancy()
                    if animal.readyToBirth:
                        animal.is_pregnant = False
                        animal.pregnancyTime = 0
                        animal.readyToBirth = False
                        if len(self.animals[animal_type]) < self.max_animals[animal_type]:
                            self.addAnimal(animal_type, 1)
                        else:
                            newbornAnimal = animal_type()
                            self.money += newbornAnimal.prize

                elif random.random() < animal.chanceOfBirth and animal.is_sick == False:
                    animal.is_pregnant = True

                # JAJKA MLEKO WEŁNA
                if random.random() < animal.chanceOfResource:
                    resource_key = animal_type.__name__.lower() + "_resource"
                    self.resources[resource_key] += 1
                    self.total_resources_collected[resource_key] += 1  # Aktualizacja całkowitych zasobów

                # UMIERANIE
                animal.check_ageDebuff()
                DeathChance = animal.chanceOfDeath
                if random.random() < DeathChance:
                    if animal.is_sick == True:
                        self.decSickCount(animal_type)
                    self.animals[animal_type].remove(animal)

        # koszty utrzymania plonow
        if self.crops:
            self.money -= self.crops.monthly_maintenance
            self.crops.total_maintenance_cost += self.crops.monthly_maintenance
            if self.current_month % 12 == 6:
                self.crops.check_for_drought()
                self.money += self.crops.annual_profit
                self.crops.total_profit += self.crops.annual_profit

    # AUTOMATYCZNE POWIĘKSZANIE MIEJSC NA ZWIERZAKI
    def AutoUpgrade(self, upgrade_manager):
        total_living_cost = sum(self.calculate_total_living_cost(animal_type) for animal_type in self.animals.keys())
        affordable_upgrades = [animal_type for animal_type, cost in upgrade_manager.upgrade_costs.items() if
                               self.money >= cost + total_living_cost]
        if affordable_upgrades:
            best_upgrade = max(affordable_upgrades, key=lambda animal_type: animal_type.default_capacityCost)
            upgrade_manager.upgrade_capacity(best_upgrade)

    def AutoAnimalBuy(self, market):
        for animal_type in self.animals.keys():
            if len(self.animals[animal_type]) <= 0:
                if self.money >= 2 * animal_type().prize * 1.1:
                    market.buy_animal(self, animal_type, 2)


    # OBLICZANIE MIESIĘCZNEGO KOSZU UTRZYMANIA ZWIERZĄT
    def calculate_total_living_cost(self, animal_type):
        total_cost = 0
        for animal in self.animals.get(animal_type, []):
            total_cost += animal.costOfLiving
        return total_cost

    # WYŚWIETLANIE STATYSTYK
    def show_statistics(self):
        for animal_type, animals in self.animals.items():

            resource_key = animal_type.__name__.lower() + "_resource"
            print(f"{animal_type.__name__}:")
            print(f"  Number of animals: {len(animals)}")
            print(f"  Total number of resources produced: {self.total_resources_collected[resource_key]}")
            final_crops_profit = self.crops.total_profit - self.crops.total_maintenance_cost
            print(f"Total profit from crops: {round(final_crops_profit)}")
            print(f"Total medicines used: {self.total_medicines_used}")  # Display the total medicines used


class UpgradeManager:              # klasa zajmujaca sie ulepszeniami
    def __init__(self, farm):
        self.farm = farm
        self.upgrade_costs = {}

    # USTAWIANIE KOSZTU POWIĘKSZENIA MIEJSC
    def set_upgrade_cost(self, animal_type):
        self.upgrade_costs[animal_type] = animal_type.default_capacityCost

    # POWIĘKSZENIE MIEJSC NA ZWIERZĄT
    def upgrade_capacity(self, animal_type):
        if self.farm.money >= self.upgrade_costs[animal_type]:
            self.farm.money -= self.upgrade_costs[animal_type]
            self.farm.max_animals[animal_type] += animal_type.capacity_increase
            self.upgrade_costs[animal_type] = int(self.upgrade_costs[animal_type] * 1.20)

class Market:                #klasa zajmujaca sie marketem
    def __init__(self):
        self.prices = {}
        self.medicine_price = 500

    # USTAWIANIE CEN ZASOBÓW DLA DANEGO ZWIERZĘCIA
    def set_price(self, animal_type):
        resource_key = animal_type.__name__.lower() + "_resource"
        self.prices[resource_key] = animal_type.resource_value

    # SPRZEDAWANIE WSZYSTKICH ZASOBÓW
    def sell_resources(self, farm):
        for resource_key, amount in farm.resources.items():
            if resource_key in self.prices:
                farm.money += amount * self.prices[resource_key]
        farm.resources = {key: 0 for key in farm.resources}

    # KUPOWANIE PODANEJ ILOSCI ZWIERZĄT
    def buy_animal(self, farm, animal_type, quantity):
        animals_price = int(animal_type().prize * 1.25)
        if len(farm.animals[animal_type]) + quantity < farm.max_animals[animal_type]:
            totalCost = animals_price * quantity
            if farm.money >= totalCost:
                farm.money -= totalCost
                farm.addAnimal(animal_type, quantity)

    # SPRZEDAWANIE WYBRANEGO ZWIERZĘCIA
    def sell_animal(self, farm, animal_type, index):
        animal = farm.animals[animal_type][index]
        animal_price = int(animal.prize)
        del farm.animals[animal_type][index]
        farm.money += animal_price

    # ULECZENIE WSZYSTKICH CHORYCH ZWIERZĄT
    def buy_medicine(self, farm):
        for animal_type, count in farm.sickAnimals_count.items():
            if count >= 1:
                if farm.money >= self.medicine_price:
                    farm.money -= self.medicine_price
                    farm.sickAnimals_count[animal_type] = 0
                    for animal in farm.animals[animal_type]:
                        animal.set_SickStatusFalse()
                        farm.total_medicines_used += 1
class Crops:                # klasa odpowiedzialna za plony
    def __init__(self, monthly_maintenance, annual_profit):
        self.monthly_maintenance = monthly_maintenance
        self.annual_profit = annual_profit
        self.upgrade_cost = 1000
        self.profit_increase = 2000
        self.total_maintenance_cost = 0
        self.total_profit = 0
        self.drought_penalty = 0.20  # Penalty percentage for drought
    def upgrade(self):
        self.annual_profit += self.profit_increase


    def check_for_drought(self):           # sprawdzanie szansy na susze
        if random.random() < 0.20:
            self.annual_profit = self.annual_profit *(1 - self.drought_penalty)

class Animal:                # klasa odpowiedzialna za zwierzeta na farmie
    default_capacity = 0
    capacity_increase = 0
    default_capacityCost = 0
    resource_value = 0
    costOfLiving = 0
    chanceOfSickness = 0.0001
    chanceOfInfection = 0.005

    def __init__(self):
        self.is_sick = False
        self.is_pregnant = False
        self.readyToBirth = False
        self.pregnancyTime = 0
        self.chanceOfResource = 0
        self.chanceOfBirth = 0
        self.chanceOfDeath = 0
        self.age = 0
        self.ageDebuff = 0
        self.prize = 0
        self.set_prize()

    def __str__(self):
        return (f"Type: {self.__class__.__name__}\n"
                f"Is Sick: {self.is_sick}\n"
                f"Is Pregnant: {self.is_pregnant}\n"
                f"Ready to Birth: {self.readyToBirth}\n"
                f"Pregnancy Time: {self.pregnancyTime}\n"
                f"Chance of Resource: {self.chanceOfResource}\n"
                f"Chance of Birth: {self.chanceOfBirth}\n"
                f"Chance of Death: {self.chanceOfDeath}\n"
                f"Age in months: {self.age}")

    # SPRAWDZANIE CZY ZWIERZE JEST W CIĄŻY
    def check_pregnancy(self):
        pass

    # OBLICZANIE MNOŻNIKA NA NEGATYWNE EFEKTY ZE WZGL. NA WIEK
    def check_ageDebuff(self):
        pass

    # USTAWIANIE CENY ZE WZGLĘDU NA WIEK
    def set_prize(self):
        pass

    def set_SickStatusFalse(self):
        self.is_sick = False

class Cow(Animal):                     # klasa dziedziczaca z klasy animal
    default_capacity = 5
    capacity_increase = 5
    default_capacityCost = 1200
    resource_value = 100
    costOfLiving = 50
    chanceOfSickness = 0.002
    chanceOfInfection = 0.01

    def __init__(self):
        super().__init__()
        self.chanceOfResource = 0.35
        self.chanceOfBirth = 0.05

    def check_pregnancy(self):                # sprawdzanie ciazy zwierzat
        if self.pregnancyTime == 9:
            self.readyToBirth = True

    def check_ageDebuff(self):             # zwiekszanie szansy na smierc zwierzat
        if self.age <= 12:
            self.ageDebuff = 0
        elif self.age > 12 and self.age <= 72:
            self.ageDebuff = 1
        elif self.age > 72 and self.age < 120:
            self.ageDebuff = 2
        else:
            self.ageDebuff = 10
        if self.is_sick:
            self.chanceOfDeath = 0.015 * self.ageDebuff * 2
        else:
            self.chanceOfDeath = 0.015 * self.ageDebuff

    def set_prize(self):
        if self.age <= 24:
            self.prize = 2000
        elif self.age > 24 and self.age < 120:
            self.prize = 5000
        else:
            self.prize = 500

class Chicken(Animal):           # klasa dziedziczaca
    default_capacity = 15
    capacity_increase = 25
    default_capacityCost = 900
    resource_value = 20
    costOfLiving = 10
    chanceOfSickness = 0.002
    chanceOfInfection = 0.01

    def __init__(self):
        super().__init__()
        self.chanceOfResource = 0.5
        self.chanceOfBirth = 0.06

    def check_pregnancy(self):
        if self.pregnancyTime == 1:
            self.readyToBirth = True

    def check_ageDebuff(self):
        if self.age <= 2:
            self.ageDebuff = 0
        elif self.age > 2 and self.age <= 16:
            self.ageDebuff = 1
        elif self.age > 16 and self.age < 48:
            self.ageDebuff = 2
        else:
            self.ageDebuff = 10
        if self.is_sick:
            self.chanceOfDeath = 0.015 * self.ageDebuff * 2
        else:
            self.chanceOfDeath = 0.015 * self.ageDebuff

    def set_prize(self):
        if self.age <= 2:
            self.prize = 100
        elif self.age > 2 and self.age <= 16:
            self.prize = 250
        else:
            self.prize = 50

class Sheep(Animal):
    default_capacity = 5
    capacity_increase = 5
    default_capacityCost = 1300
    resource_value = 500
    costOfLiving = 50
    chanceOfSickness = 0.002
    chanceOfInfection = 0.01

    def __init__(self):
        super().__init__()
        self.chanceOfResource = 0.15
        self.chanceOfBirth = 0.05

    def check_pregnancy(self):
        if self.pregnancyTime == 5:
            self.readyToBirth = True

    def check_ageDebuff(self):
        if self.age <= 12:
            self.ageDebuff = 0
        elif self.age > 12 and self.age <= 60:
            self.ageDebuff = 1
        elif self.age > 60 and self.age < 96:
            self.ageDebuff = 2
        else:
            self.ageDebuff = 10
        if self.is_sick:
            self.chanceOfDeath = 0.015 * self.ageDebuff * 2
        else:
            self.chanceOfDeath = 0.015 * self.ageDebuff

    def set_prize(self):
        if self.age <= 12:
            self.prize = 2000
        elif self.age > 12 and self.age <= 60:
            self.prize = 6000
        else:
            self.prize = 1100

farm = Farm()
farm.addCrops(Crops(monthly_maintenance=200, annual_profit=7000))




# rozpoczęcie gui
class FarmGameApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1200x600")
        self.root.title("Farm")
        self.farm = Farm()
        self.upgrade_manager = UpgradeManager(self.farm)
        self.market = Market()

        # Dodaj zwierzęta na farmę
        self.farm.addAnimal(Cow, 2)
        self.farm.addAnimal(Chicken, 2)
        self.farm.addAnimal(Sheep, 2)
        self.farm.addCrops(Crops(monthly_maintenance=200, annual_profit=7000))


        # Ustaw ceny ulepszeń i zasobów
        self.upgrade_manager.set_upgrade_cost(Cow)
        self.upgrade_manager.set_upgrade_cost(Chicken)
        self.upgrade_manager.set_upgrade_cost(Sheep)
        self.market.set_price(Cow)
        self.market.set_price(Chicken)
        self.market.set_price(Sheep)

        self.bg_image = Image.open("photo.jpg")
        self.bg_image = self.bg_image.resize((1200, 600), Image.ANTIALIAS)
        self.bg_image = ImageTk.PhotoImage(self.bg_image)

        # Utwórz GUI
        self.create_widgets()

    def create_widgets(self):
        # Informacje o grze
        bg_label = tk.Label(self.root, image=self.bg_image)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.info_frame = ttk.LabelFrame(self.root, text="Information")
        self.info_frame.grid(row=4, column=0, padx=10, pady=15)

        self.month_label = ttk.Label(self.info_frame, text="Month: 0")
        self.month_label.grid(row=4, column=0, padx=10, pady=5)

        self.money_label = ttk.Label(self.info_frame, text="Money: 5000")
        self.money_label.grid(row=6, column=0, padx=10, pady=5)

        # Przycisk następnego miesiąca
        self.next_month_button = ttk.Button(self.root, text="Next month", command=self.next_month)
        self.next_month_button.grid(row=2, column=0, padx=10, pady=10)

        # Przycisk wczytywania pliku
        self.load_button = ttk.Button(self.root, text="load from file", command=self.load_from_file)
        self.load_button.grid(row=1, column=0, padx=10, pady=10)

        # Przyciski symulacji
        self.start_simulation_button = ttk.Button(self.root, text="Start Simulation", command=self.start_simulation)
        self.start_simulation_button.grid(row=0, column=0, padx=10, pady=10)

        self.stop_simulation_button = ttk.Button(self.root, text="Stop Simulation", command=self.stop_simulation)
        self.stop_simulation_button.grid(row=3, column=0, padx=10, pady=10)

        # Pole tekstowe do wyświetlania statystyk
        self.text_output = tk.Text(self.root, wrap="word", width=60, height=20)
        self.text_output.grid(row=2, column=1, rowspan=6, padx=(10, 0))

    def next_month(self):
        self.farm.MonthlyEvents()
        self.market.sell_resources(self.farm)
        self.farm.AutoAnimalBuy(self.market)
        self.farm.AutoUpgrade(self.upgrade_manager)
        self.market.buy_medicine(self.farm)
        self.update_labels()
        self.show_statistics()  # Aktualizuj statystyki

    def update_labels(self):
        self.month_label.config(text=f"Miesiąc: {self.farm.current_month}")
        self.money_label.config(text=f"Pieniądze: {round(self.farm.money)}")

    def load_from_file(self):
        with open("text.csv", newline='', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file, delimiter=";")
            for line in reader:
                self.farm.current_month = int(line['miesiac'])
                self.farm.money = int(line['pieniadze'])
                self.farm.animals[Cow] = [Cow() for _ in range(int(line['krowy']))]
                self.farm.animals[Chicken] = [Chicken() for _ in range(int(line['kury']))]
                self.farm.animals[Sheep] = [Sheep() for _ in range(int(line['owce']))]
                self.update_labels()

    def start_simulation(self):
        self.simulation_thread = threading.Thread(target=self.run_simulation)
        self.simulation_thread.start()

    def run_simulation(self):
      self.running = True
      while self.running and self.farm.current_month < 2000:
        self.farm.MonthlyEvents()
        self.market.sell_resources(self.farm)
        self.farm.AutoAnimalBuy(self.market)
        self.farm.AutoUpgrade(self.upgrade_manager)
        self.market.buy_medicine(self.farm)
        self.update_labels()
        self.root.after(100, self.show_statistics)  # Wywołaj show_statistics co 0.1 sekundy
        time.sleep(0.05)
    def stop_simulation(self):
        self.running = False
        if hasattr(self, 'simulation_thread'):
            self.simulation_thread.join()

    def show_statistics(self):
        self.text_output.delete(1.0, tk.END)  # Wyczyść pole tekstowe przed wyświetleniem statystyk

        for animal_type, animals in self.farm.animals.items():
            resource_key = animal_type.__name__.lower() + "_resource"

            stats = (f"{animal_type.__name__}:\n"
                     f"  Number of animals: {len(animals)}\n"
                     f"  Total number of resources produced: {self.farm.total_resources_collected[resource_key]}\n")

            self.text_output.insert(tk.END, stats)

        if self.farm.crops:
            final_crops_profit = self.farm.crops.total_profit - self.farm.crops.total_maintenance_cost
        crops_stats = (f"Total profit from crops: {round(final_crops_profit)}\n"
                       f"Total medicines used: {self.farm.total_medicines_used}\n")

        self.text_output.insert(tk.END, crops_stats)

# Tworzenie okna aplikacji
root = tk.Tk()
app = FarmGameApp(root)
root.mainloop()