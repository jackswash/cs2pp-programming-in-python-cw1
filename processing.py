import csv
import os
import statistics
from collections import Counter

makes_to_remove = [
    'Ford',
    'Kia',
    'Lotus'
]

columns_to_remove = [
    'Engine Fuel Type',
    'Market Category',
    'Number of Doors',
    'Vehicle Size'
]

renamed_columns = {
    'Engine HP': 'HP',
    'Engine Cylinders': 'Cylinders',
    'Transmission Type': 'Transmission',
    'Driven Wheels': 'Drive Mode',
    'highway MPG': 'MPG-H',
    'city mpg': 'MPG-C',
    'MSRP': 'Price'
}

def process_csv(file_name='./data/cardata.csv'):
    """Method for processing and transforming a CSV file into a modified
    version based on set requirements, and then comparing the outputs of
    both functions.

    Parameters:
    file_name (str): Directory path to the CSV file.

    Returns:
    list: Contains statistics of both original and modified data
    """
    
    with open(file_name, 'r', newline='') as file:
        reader = csv.reader(file)
        original_headers = next(reader)
        original_data = list(reader)
        
    output_path = './data/cardata_modified.csv'

    original_stats = {}
    modified_stats = {}
    modified_headers = []
    modified_data = []

    def calculate_avg_price(data, model_name, model_index, price_index):
        """Method for calculating the average price of a car model.
        Subfunction since I need to call it multiple times rather
        than hardcoding it.
    
        Parameters:
        data (list): List of rows with car data
        model_name (str): Gets the name of model
        model_index (int): Gets the index of model column
        price_index (int): Gets the index of price column
    
        Returns:
        str: The average price to 2dp using bankers rounding, or returns 0 if
        no valid entries.
        """
    
        prices = [float(row[price_index]) for row in data
                if row[model_index] == model_name and row[price_index]]
        if prices:
            mean_price = statistics.mean(prices)
            rounded_price = round(mean_price, 2)
            return f'{rounded_price:.2f}'
        return '0.00'

    def calculate_original_stats():
        """Method for calculating the original stats of cardata.csv to return
        and output later. Subfunction of process_csv.
        """

        # Get number of rows and columns.
        original_stats['rows'] = len(original_data)
        original_stats['columns'] = len(original_headers)

        # Get indices of columns required.
        original_make_index = original_headers.index('Make')
        original_year_index = original_headers.index('Year')
        original_model_index = original_headers.index('Model')
        original_price_index = original_headers.index('MSRP')
        original_size_index = original_headers.index('Vehicle Size')

        # Get number of unique "makes".
        original_makes = set(row[original_make_index] for row in original_data)
        original_stats['unique_makes'] = len(original_makes)

        # Get number of cars in the year 2009.
        original_stats['entries_2009'] = sum(
            1 for row in original_data if row[original_year_index] == '2009')
        
        # Get average price for Impala and Integra models using "calculate_avg_price".
        original_stats['avg_price_impala'] = calculate_avg_price(
            original_data, 'Impala', original_model_index, original_price_index)
        original_stats['avg_price_integra'] = calculate_avg_price(
            original_data, 'Integra', original_model_index, original_price_index)

        # Get model with fewest number of "midsize" cars.
        original_midsize_models = [row[original_model_index] for row in original_data 
                                  if row[original_size_index] == 'Midsize']
        
        if original_midsize_models:
            original_midsize_counter = Counter(original_midsize_models)
            original_stats['fewest_midsize_model'] = min(original_midsize_counter, key=original_midsize_counter.get)
        else:
            original_stats['fewest_midsize_model'] = 'N/A'

    def transform_modified_data():
        """Method for modifying the dupe and transforming it with the required
        transformations in the documentation. Ordered step by step for
        convenience and clarity.
    
        Returns:
        tuple: modified_headers and modified_data which has the transformations
        within.
        """
        
        modified_headers = original_headers.copy()
        modified_data = [row.copy() for row in original_data]

        # Remove columns from list as required.
        columns_to_keep = [i for i, col in enumerate(original_headers) if
                           col not in columns_to_remove]
        modified_headers = [modified_headers[i] for i in columns_to_keep]
        modified_data = [[row[i] for i in columns_to_keep] for row in
                         modified_data]

        # Remove specific makes from data.
        make_index = modified_headers.index('Make')
        modified_data = [row for row in modified_data if
                         row[make_index] not in makes_to_remove]

        # Remove duplicate entries from data.
        non_dupes = []
        seen = set()
        for row in modified_data:
            row_tuple = tuple(row)
            if row_tuple not in seen:
                seen.add(row_tuple)
                non_dupes.append(list(row))
        modified_data = non_dupes

        # Rename column headers as required.
        for old, new in renamed_columns.items():
            if old in modified_headers:
                modified_headers[modified_headers.index(old)] = new

        # Calculate HP median for missing values using existing values.
        hp_index = modified_headers.index('HP')
        present_hp_values = [float(row[hp_index]) for row in modified_data if
                           row[hp_index]]
        median_hp = statistics.median(present_hp_values)

        for row in modified_data:
            if not row[hp_index]:
                row[hp_index] = str(median_hp)

        # Remove rows that contain missing values.
        modified_data = [row for row in modified_data if
                         all(cell != '' for cell in row)]

        # Create a new column named "HP_Type" and transform based on requirements.
        modified_headers.append('HP_Type')
        for row in modified_data:
            hp = float(row[hp_index])
            if hp >= 300:
                row.append('high')
            else:
                row.append('low')

        # Create a new column named "Price_Class" and transform based on requirements.
        price_index = modified_headers.index('Price')
        modified_headers.append('Price_class')
        for row in modified_data:
            price = float(row[price_index])
            if price >= 50000:
                row.append('high')
            elif price >= 30000:
                row.append('mid')
            else:
                row.append('low')

        # Round "price" values to the nearest 100 dollars.
        for row in modified_data:
            price = float(row[price_index])
            row[price_index] = str(round(price / 100) * 100)

        # Remove all cars made BEFORE the year 2000.
        year_index = modified_headers.index('Year')
        modified_data = [row for row in modified_data if
                         int(row[year_index]) > 2000]

        # Keep car "makes" with more than 55 entries, but less than 300.
        makes_count = Counter(row[make_index] for row in modified_data)
        valid_makes = {make for make, count in makes_count.items() if
                       55 < count < 300}
        modified_data = [row for row in modified_data if
                         row[make_index] in valid_makes]

        # Write file with modified changes.
        with open(output_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(modified_headers)
            writer.writerows(modified_data)

        return modified_headers, modified_data

    # Calculate modified stats after all transformations
    def calculate_modified_stats():
        """Method for calculating the modified stats of cardata_modified.csv to return
        and output later. Subfunction of process_csv.
        """
        
        # Get number of rows and columns.
        modified_stats['rows'] = len(modified_data)
        modified_stats['columns'] = len(modified_headers)

        # Get indices of columns required.
        make_index = modified_headers.index('Make')
        year_index = modified_headers.index('Year')
        model_index = modified_headers.index('Model')
        price_index = modified_headers.index('Price')

        # Get number of unique "makes".
        modified_makes = set(row[make_index] for row in modified_data)
        modified_stats['unique_makes'] = len(modified_makes)

        # Get number of cars in the year 2009.
        modified_stats['entries_2009'] = sum(
            1 for row in modified_data if row[year_index] == '2009')

        # Get average price for Impala and Integra models using "calculate_avg_price".
        modified_stats['avg_price_impala'] = calculate_avg_price(
            modified_data, 'Impala', model_index, price_index)
        modified_stats['avg_price_integra'] = calculate_avg_price(
            modified_data, 'Integra', model_index, price_index)

        modified_stats['fewest_midsize_model'] = 'N/A'

    calculate_original_stats()
    modified_headers, modified_data = transform_modified_data()
    calculate_modified_stats()

    return [
        [
            original_stats['rows'],
            original_stats['columns'],
            original_stats['unique_makes'],
            original_stats['entries_2009'],
            original_stats['avg_price_impala'],
            original_stats['avg_price_integra'],
            original_stats['fewest_midsize_model']
        ],
        [
            modified_stats['rows'],
            modified_stats['columns'],
            modified_stats['unique_makes'],
            modified_stats['entries_2009'],
            modified_stats['avg_price_impala'],
            modified_stats['avg_price_integra'],
            modified_stats['fewest_midsize_model']
        ]
    ]