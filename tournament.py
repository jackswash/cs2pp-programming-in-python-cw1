import json
import csv
import math
import random

class Tournament:
    def __init__(self, config_path):
        """Initialises tournament by loading the JSON file stored in ./data/.

        Parameters:
        config_path (str): Directory path to the JSON config.

        Returns:
        TypeError: If number of teams is not an integer.
        AssertionError: If number of teams is not positive and non-zero.
        """
        
        # Load JSON file.
        with open(config_path, 'r') as f:
            config = json.load(f)

        # Read values stored within JSON file.
        self.path = config['path']
        self.name = config['name']
        nteams = config.get('nteams', 16)
        self.default_low = config['default_low']
        self.default_high = config['default_high']
        self.default_incr = config['default_incr']

        # Load CSV file.
        with open(self.path, 'r', newline='') as file:
            reader = csv.reader(file)
            self.headers = next(reader)
            self.data = list(reader)

        # Check if number of teams is not an int and raise error if not.
        if not isinstance(nteams, int):
            raise TypeError("The number of teams must be an integer.")

        # Assert that number of teams is positive and non-zero.
        assert nteams > 0, "The number of teams must be positive and non-zero."

        # Check if number of teams is a power of 2, and if not, adjust
        # number of teams.
        if not math.log2(nteams).is_integer():
            nteams = 2 ** math.ceil(math.log2(nteams))
            print(f"The number of teams has been adjusted to {nteams}.")

        self.nteams = nteams
        self.sponsors = []
        self.budget = []
        self.teams = []

    def __repr__(self):
        """Return a string representation of Tournament.
        
        Returns:
        str: Information about tournament such as name and number of teams.
        """
        
        return f"Tournament(name='{self.name}', nteams={self.nteams})"

    def __str__(self):
        """Return a regular string representation of Tournament.

        Returns:
        str: Information about tournament such as name and number of teams
        """
        
        return f"{self.name} Tournament with {self.nteams} teams"

    def generate_sponsors(self, sponsor_list=None, low=None, high=None, incr=None, fixed_budget=None):
        """Function for generating sponsors for teams, and allocates a budget
        to them also.

        Parameters:
        sponsor_list (list, optional): Sponsors that get assigned to teams.
        low (int, optional): Lowest budget value, default value in config.
        high (int, optional): Highest budget value, default value in config.
        incr (int, optional): Increment value of budget, default value in config.
        """
        
        # Set default values as set in config if none specified.
        low = low if low is not None else self.default_low
        high = high if high is not None else self.default_high
        incr = incr if incr is not None else self.default_incr
        
        if sponsor_list is None:
            sponsor_list = []
        
        self.sponsors = []
        self.budget = []
        self.tournament_record = {}

        # Get available sponsors by reading the 'Make' header.
        make_index = self.headers.index('Make')
        available_sponsors = []
        for car in self.data:
            make = car[make_index]
            if make not in available_sponsors:
                available_sponsors.append(make)

        # Assign sponsors from sponsor_list or randomly.
        for i in range(self.nteams):
            if i < len(sponsor_list):
                sponsor = sponsor_list[i]
            else:
                # Go through and find sponsors that have yet to be assigned.
                unassigned_sponsors = []
                for make in available_sponsors:
                    if make not in self.sponsors:
                        unassigned_sponsors.append(make)
                    
                # Select random sponsor from those currently unassigned.
                sponsor = random.choice(unassigned_sponsors)
            self.sponsors.append(sponsor)
            self.tournament_record[sponsor] = []

        # Allocate range of budget values.
        budget_range = list(range(low, high + 1, incr))

        # Allocate budget to all teams, either fixed or random.
        for i in range(self.nteams):
            if fixed_budget is not None and low <= fixed_budget <= high:
                self.budget.append(fixed_budget)
            else:
                random_budget = random.choice(budget_range)
                self.budget.append(random_budget)

    def generate_teams(self):
        """Populates tournament with Team objects."""
        self.teams = []

        for i in range(self.nteams):
            sponsor = self.sponsors[i]
            budget = self.budget[i]
            team = self.Team(sponsor, budget, self)
            self.teams.append(team)

    class Team:
        def __init__(self, sponsor, budget, tournament):
            """Initialises team with various parameters.
        
            Parameters:
            sponsor: The sponsor of the team.
            budget: The budget available for the team.
            tournament: A reference to the tournament object.
            """
            
            self.sponsor = sponsor
            self.budget = budget
            self.inventory = []
            self.active = True
            self.performance_record = {
                'wins': 0,
                'losses': 0,
                'score': 0,
                'num_of_cars_used': 0
            }
            self.tournament = tournament

        def __str__(self):
            """Returns a string representation of Team.
        
            Returns:
            str: Information about a team such as sponsor, budget, and amount of cars.
            """
            
            return f"Team sponsored by {self.sponsor} with ${self.budget:,.2f} available and {len(self.inventory)} cars"

    def buy_cars(self):
        """Function to allow a team to purchase inventory.
    
        Returns:
        list: List of teams who have purchased inventory.
        """
        
        for team in self.teams:
            self._purchase_inventory(team)
        return self.teams

    def _purchase_inventory(self, team):
        """Function using a greedy approach to purchase inventory for a team.
    
        Parameters:
        team: The team that is purchasing the inventory.
        """
        
        # Get indices of columns required.
        make_index = self.headers.index('Make')
        model_index = self.headers.index('Model')
        mpgh_index = self.headers.index('MPG-H')
        price_index = self.headers.index('Price')
        
        # Filter cars from the sponsor.
        sponsor_cars = []
        for row in self.data:
            if row[make_index] == team.sponsor:
                sponsor_cars.append(row)
        
        # MPG-H to float.
        cars_by_efficiency = []
        for car in sponsor_cars:
            mpgh_value = float(car[mpgh_index])
            cars_by_efficiency.append((car, mpgh_value))
        
        # Sort cars by MPG-H for greedy selection (highest MPG-H first).
        cars_by_efficiency.sort(key=lambda item: item[1], reverse=True)
        
        # Get models already in inventory to avoid duplicates.
        current_models = []
        for car in team.inventory:
            current_models.append(car[model_index])
        
        # Buy cars using the greedy method.
        budget_remaining = team.budget
        for row, _ in cars_by_efficiency:
            # Skip if model already in inventory.
            if row[model_index] in current_models:
                continue
            
            # Get car price and check if team can afford it.
            price = float(row[price_index])
            if price <= budget_remaining:
                # Purchase car, and add to inventory, then update budget.
                team.inventory.append(row)
                budget_remaining -= price
                # Add model to current_models to prevent duplicate purchases.
                current_models.append(row[model_index])
        
        team.budget = budget_remaining

    def hold_event(self):
        """Function to execute a tournament and perform calculations to
        determine a winner.
        """
        
        # Get MPG-H index.
        mpgh_index = self.headers.index('MPG-H')
        
        # Initialise the win record with sponsor names.
        self.win_record = {team.sponsor: [] for team in self.teams}

        active_teams = self.teams.copy()

        # While loop to keep game active until one team is remaining.
        while len(active_teams) > 1:
            next_round_teams = []

            for i in range(0, len(active_teams), 2):
                team1 = active_teams[i]
                team2 = active_teams[i + 1]

                # Calculate scores of teams based on their MPG-H sum.
                team1_score = sum(float(car[mpgh_index]) for car in team1.inventory)
                team2_score = sum(float(car[mpgh_index]) for car in team2.inventory)

                # Update "num_of_cars_used" statistic in performance record.
                team1.performance_record['num_of_cars_used'] += len(team1.inventory)
                team2.performance_record['num_of_cars_used'] += len(team2.inventory)

                # Calculate winner and loser of the tournament.
                winner = team1 if team1_score > team2_score else team2
                loser = team2 if winner == team1 else team1

                # Update performance records with required statistics.
                winner.performance_record['wins'] += 1
                winner.performance_record['score'] += max(team1_score, team2_score)
                loser.performance_record['losses'] += 1
                loser.performance_record['score'] += min(team1_score, team2_score)

                # Record W/L statistics.
                self.win_record[winner.sponsor].append("W     ")
                self.win_record[loser.sponsor].append("L     ")

                # Give prize of $50,000 for winner.
                winner.budget += 50000

                # Let winner purchase more inventory.
                self._purchase_inventory(winner)

                # Advance winner to next round.
                next_round_teams.append(winner)

            active_teams = next_round_teams

        # Calculate champion of tournament.
        if active_teams:
            self.champion = active_teams[0]
            return self.champion
        return None

    def show_win_record(self):
        """Function to print a visual display of a tournament."""
        for team_name, results in self.win_record.items():
            print(f"{team_name:>15}: {results}")

class Tournament_optimised(Tournament):
    def _purchase_inventory(self, team):
        """Function using a dynamic approach to purchase inventory for a team
        rather than using a greedy approach.
    
        Parameters:
        team: The team that is purchasing the inventory.
        """
        
        # Get indices of columns required.
        make_index = self.headers.index('Make')
        model_index = self.headers.index('Model')
        mpgh_index = self.headers.index('MPG-H')
        price_index = self.headers.index('Price')
        
        # Filter cars from the sponsor.
        sponsor_cars = []
        for row in self.data:
            if row[make_index] == team.sponsor:
                sponsor_cars.append(row)

        # Get already existing models to avoid dupes.
        current_models = []
        for car in team.inventory:
            current_models.append(car[model_index])

        # Create required lists.
        available_cars = []
        mpgh_values = []
        prices = []

        # Filter cars that are not in the inventory.
        for car in sponsor_cars:
            if car[model_index] not in current_models:
                available_cars.append(car)
                mpgh_values.append(float(car[mpgh_index]))
                prices.append(int(float(car[price_index])))

        # Setup DP table to solve 0/1 knapsack.
        # "Capacity" is the max budget.
        # "n" is number of available cars.
        capacity = int(team.budget)
        n = len(available_cars)

        # Initialise DP table.
        dp = []
        for i in range(n + 1):
            dp.append([])
            for j in range(capacity + 1):
                dp[i].append(0)
        
        # Fill in the DP table.
        for i in range(1, n + 1):
            for j in range(capacity + 1):
                if prices[i-1] <= j:
                    # Function to determine whether to purchase car (if can purchase).
                    include_val = mpgh_values[i-1] + dp[i-1][j-prices[i-1]]
                    exclude_val = dp[i-1][j]
                    dp[i][j] = max(include_val, exclude_val)
                else:
                    # If can't afford car, disregard.
                    dp[i][j] = dp[i-1][j]
        
        # Backtrack to determine which cars to buy.
        picked_cars = []
        remain_budget = capacity
        
        i = n
        while i > 0 and remain_budget > 0:
            if dp[i][remain_budget] != dp[i-1][remain_budget]:
                picked_cars.append(available_cars[i-1])
                remain_budget -= prices[i-1]
            i -= 1
        
        # Update inventory and budget for team.
        for car in picked_cars:
            team.inventory.append(car)
            team.budget -= float(car[price_index])