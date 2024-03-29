import json
import os
import random
import io
import requests
from PIL import Image
from bs4 import BeautifulSoup

def save_upazila_names(geojson_path, output_path):
    with open(geojson_path) as f:
        geojson = json.load(f)

    feature_ids = []
    for feature in geojson['features']:
        id_parts = [str(feature['properties']['NAME_{}'.format(i)]) for i in range(1, 5)]
        feature_id = '-'.join(id_parts)
        feature_ids.append(feature_id)

    with open(output_path, 'w') as f:
        f.write('\n'.join(feature_ids))

def save_district_names(geojson_path, output_path):
    with open(geojson_path) as f:
        geojson = json.load(f)

    feature_ids = []
    for feature in geojson['features']:
        # id_parts = [str(feature['properties']['NAME_{}'.format(i)]) for i in range(1, 4)]
        # feature_id = '-'.join(id_parts)
        feature_id = str(feature['properties']['NAME_3'])
        feature_ids.append(feature_id)

    with open(output_path, 'w') as f:
        f.write('\n'.join(feature_ids))

def sort_lines_alphabetically(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
        lines.sort()
    with open(file_path, 'w') as f:
        f.writelines(lines)

def sort_unique_lines_alphabetically(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
        unique_lines = set(lines)
        sorted_lines = sorted(unique_lines)
    with open(file_path, 'w') as f:
        f.writelines(sorted_lines)

def save_json_districts(file_path):
    with open(file_path, encoding='utf-8') as f:
        # Ensure json.load can load unicode characters
        districts = json.load(f)
        # for each object in district, create a list of strings with the "name" field
        district_names = [district['name'] for district in districts['districts']]
        # sort the list
        district_names.sort()
        # write the list to a file
    with open('data/json_districts.txt', 'w') as f:
        f.write('\n'.join(district_names))

def generate_district_data(file_path):
    with open(file_path, encoding='utf-8') as f:
        # Ensure json.load can load unicode characters
        districts = json.load(f)
        # sort the districts by the "name" field
        districts['districts'].sort(key=lambda x: x['name'])
        # for each district object, generate the following fields and add them to the object
        """
        historicalData: { 
            'timeRange': "1974-2020",
            'meanTemperature' : a value between 26 and 27.5 with two decimal figures
            'nCdd' : an integer value between 5100 to 6300
            'nHotDays40': a value between 2 and 48 with two decimal figures
        },
        futureData: {
            'timeRange': "2030-2050",
            'meanTemperature' : a random value between 26 and 27.5 with two decimal figures
            'nCdd' : a random integer value between 5100 to 6300
            'nHotdays40': a random value between 2 and 48 with two decimal figures
        }
        """
        for district in districts['districts']:
            district['historicalData'] = {
                'timeRange': "1974-2020",
                'meanTemperature': round(random.uniform(24.5, 26), 2),
                'nCdd': random.randint(4300, 5200),
                'nHotDays40': round(random.uniform(1, 32), 2)
            }
            district['futureData'] = {
                'timeRange': "2030-2050",
                'meanTemperature': round(random.uniform(26, 27.5), 2),
                'nCdd': random.randint(5100, 6300),
                'nHotDays40': round(random.uniform(2, 48), 2)
            }

        with open('data/generated_districts.json', 'w') as f:
            json.dump(districts, f, indent=4)


def generate_headlines_and_images(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)

    for district, urls in data.items():
        if isinstance(urls, list):
            for i, url in enumerate(urls):
                try:
                    response = requests.get(url)
                    response.raise_for_status()

                    # Obtain the website's title
                    title = get_website_title(response.text)
                    # Save the thumbnail image
                    image_path = f"data/images/{district}_{i+1}.jpg"
                    image = save_thumbnail_image(response.content, image_path)
                    # Replace the URL entry with the new object
                    urls[i] = {
                        'headline': title,
                        'image': image,
                        'url': url
                    }

                except (requests.RequestException, ValueError) as e:
                    print(f"Error occurred for {url}: {e}")

    with open("data/new_climate_stories.json", 'w') as f:
        json.dump(data, f, indent=4)

def get_website_title(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup.title.string

def save_thumbnail_image(content, image_path):
        # Parse the HTML content
    soup = BeautifulSoup(content, 'html.parser')

    # Find the <meta> tag with the thumbnail information
    thumbnail_meta_tag = soup.find('meta', property='og:image')

    if thumbnail_meta_tag:
        # Extract the thumbnail URL from the 'content' attribute of the <meta> tag
        thumbnail_url = thumbnail_meta_tag['content']
        t_response = requests.get(thumbnail_url)
        if t_response.status_code == 200:
            with open(image_path, 'wb+') as file:
                file.write(t_response.content)
            print(f"Image downloaded successfully as {image_path}")
        else:
            print("Failed to download the image")
        return image_path
    else:
        # If no thumbnail meta tag found, return None or handle accordingly
        return ""
    
def convert_tsv_to_json(file_path):
    """
    This function converts a TSV file to a JSON file
    Where the first row specifies the column headers
    """
    with open(file_path, 'r') as f:
        # Read the first line of the file
        headers = f.readline().strip().split('\t')
        # Read the rest of the lines
        lines = f.readlines()
        # Create an empty list to store the data
        data = []
        # Iterate over the lines
        for line in lines:
            # Split the line into a list of values
            values = line.strip().split('\t')
            # Create an empty dictionary to store the row
            row = {}
            # Iterate over the headers and values
            for header, value in zip(headers, values):
                # Add the value to the row dictionary using the header as the key
                row[header] = value
            # Add the row to the data list
            data.append(row)
        # Create a dictionary with the data list
        data_dict = {'data': data}
        # Write the dictionary to a JSON file
        with open('data/test.json', 'w') as f:
            json.dump(data_dict, f, indent=4)


def write_from_csv_to_json(csv_path, json_path):
    """
    Given a CSV of this format
    Name,Historic,New,Delta
    Bagerhat,22.4,23.87777778,1.477777778
    Bandarban,21.68,23.13714286,1.457142857

    Load the csv file first, then

    Load the given json of json_path of format
    {
    "districts": [
        {
            "id": "55",
            "division_id": "4",
            "name": "Bagerhat",
            "bn_name": "\u09ac\u09be\u0997\u09c7\u09b0\u09b9\u09be\u099f",
            "lat": "22.651568",
            "long": "89.785938",
            "historicalData": {
                "timeRange": "1995-2014",
                "maxTemperature": 31.5,
                "minTemperature": 22.4,
                "nHotDays40": 28.59
            },
            "futureData": {
                "timeRange": "2050",
                "maxTemperature": 32.92,
                "minTemperature": 23.88,
                "nHotDays40": 37.17
            }
        },
    }

    Then write the "historic" values of each row in the csv file into the ["historicalData"]["minTemperature"] key
    for which the "Name" field of the csv file matches the "name" field of the json file
    and the "new" values of each district into the ["futureData"]["minTemperature"] key
    """
    with open(csv_path, 'r') as f:
        # Read the first line of the file
        headers = f.readline().strip().split(',')
        # Read the rest of the lines
        lines = f.readlines()
        # Create an empty list to store the data
        data = []
        # Iterate over the lines
        for line in lines:
            # Split the line into a list of values
            values = line.strip().split(',')
            # Create an empty dictionary to store the row
            row = {}
            # Iterate over the headers and values
            for header, value in zip(headers, values):
                # Add the value to the row dictionary using the header as the key
                row[header] = value
            # Add the row to the data list
            data.append(row)
        # Create a dictionary with the data list
        data_dict = {'data': data}
        # Write the dictionary to a JSON file

        """
            Then write the "historic" values of each row in the csv file into the ["historicalData"]["minTemperature"] key
            for which the "Name" field of the csv file matches the "name" field of the json file
            and the "new" values of each district into the ["futureData"]["minTemperature"] key
        """
        with open(json_path, 'r') as file:
            # Read the json file into a dict
            districts = json.load(file)
            # Iterate over the districts in the json file
            for district in districts['districts']:
                for row in data:
                    if district['name'] == row['Name']:
                        district['historicalData']['minTemperature'] = float(row['Historic'])
                        district['futureData']['minTemperature'] = float(row['New'])
            # Save the modified districts into the json_path file
            with open("data/generated_districts3.json", 'w') as file2:
                json.dump(districts, file2, indent=4)

def reloadCentroids(districts_json, new_json):
     with open(new_json, 'r') as read_file:
        data = json.load(read_file)
        centroids = data['features']
        with open(districts_json, 'r', encoding='utf-8') as write_file:
            write_json = json.load(write_file)
            for district in write_json['districts']:
                for centroid in centroids:
                    if district['name'] == centroid['properties']['NAME_3']:
                        district['lat'] = centroid['geometry']['coordinates'][1]
                        district['lon'] = centroid['geometry']['coordinates'][0]
            with open("data/bd_districts3.json", 'w') as file2:
                json.dump(write_json, file2, indent=2)

    

if __name__ == '__main__':
    # save_district_names('data/bd_districts.geojson', 'data/districts.txt')
    # sort_unique_lines_alphabetically('data/districts.txt')
    # save_json_districts('data/bd_districts.json')
    # sort_lines_alphabetically('data/json_districts.txt')
    # generate_district_data('data/bd_districts.json')
    # print(os.getcwd())
    # generate_headlines_and_images('data/climate_stories.json')
    # write_from_csv_to_json('data/sheetData.csv', 'data/generated_districts2.json')
    reloadCentroids('data/bd_districts2.json', 'data/BDDistrictCentroids.geojson')
    