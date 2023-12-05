import json
import os
import random
import io
import requests
from PIL import Image
from bs4 import BeautifulSoup
from datetime import datetime

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
        if len(urls) > 0:
            for i, url in enumerate(urls):
                try:
                    print(url)
                    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'})
                    response.raise_for_status()

                    # Obtain the website's title if it is not a file on the internet
                    if response.headers.get('content-type', '').startswith('text'):
                        title = get_website_title(response.text)
                    else:
                        title = "PDF"
                    # Save the thumbnail image
                    image_path = f"data/images/{district}_{i+1}.jpg"
                    # image = save_thumbnail_image(response.content, image_path)
                    # Replace the URL entry with the new object
                    urls[i] = {
                        'headline': title,
                        # 'image': image,
                        'url': url,
                        'tag': "news" if title != "PDF" else "Project"
                    }

                except (requests.RequestException, ValueError) as e:
                    print(f"Error occurred for {url}: {e}")
                    urls[i] = {
                        'headline': "<GET_TITLE_MANUALLY>",
                        # 'image': image,
                        'url': url,
                        'tag': "news"
                    }

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

def parse_world_bank_data(original_json, new_json):
    output_data = {}
    with open(original_json, 'r') as read_file:
        read_data = json.load(read_file)["data"]
        climate_variables = read_data.keys()
        for var in climate_variables:
            var_climatology = read_data[var]["climatology"]
            time_ranges = var_climatology.keys()
            for time_range in time_ranges:
                results_dict = {}
                results_dict2 = {}
                time_year_string = f"{time_range.split('-')[0]}-07"
                if time_range == "1995-2014":
                    districts_dict = read_data[var]["climatology"][time_range]["historical"]
                    for district in districts_dict.keys():
                        results_dict[district] = read_data[var]["climatology"][time_range]["historical"][district]["1995-07"]
                    read_data[var]["climatology"][time_range]["historical"] = results_dict
                else:
                    districts_dict = read_data[var]["climatology"][time_range]["ssp245"]
                    for district in districts_dict.keys():
                        results_dict[district] = read_data[var]["climatology"][time_range]["ssp245"][district][time_year_string]
                    read_data[var]["climatology"][time_range]["ssp245"] = results_dict

                    districts_dict = read_data[var]["climatology"][time_range]["ssp370"]
                    for district in districts_dict.keys():
                        results_dict2[district] = read_data[var]["climatology"][time_range]["ssp370"][district][time_year_string]
                    read_data[var]["climatology"][time_range]["ssp370"] = results_dict2

            var_anomaly = read_data[var]["anomaly"]
            time_ranges = var_anomaly.keys()
            for time_range in time_ranges:
                results_dict = {}
                results_dict2 = {}
                time_year_string = f"{time_range.split('-')[0]}-07"
                districts_dict = read_data[var]["anomaly"][time_range]["ssp245"]
                for district in districts_dict.keys():
                    
                    results_dict[district] = read_data[var]["anomaly"][time_range]["ssp245"][district][time_year_string]
                read_data[var]["anomaly"][time_range]["ssp245"] = results_dict

                districts_dict = read_data[var]["anomaly"][time_range]["ssp370"]
                for district in districts_dict.keys():
                    results_dict2[district] = read_data[var]["anomaly"][time_range]["ssp370"][district][time_year_string]
                read_data[var]["anomaly"][time_range]["ssp370"] = results_dict2

    with open(new_json, 'w+') as write_file:
        json.dump(read_data, write_file, indent=2)

def districts_to_division(read_file, write_file):
    """
    This function reads the data/list_of_districts.txt file which has a list of district names separated by newline
    for each district name, it writes a dummy division name "Dhaka" and creates a json list of objects
    For example, if the input text file is:
    
    "
    Bagerhat
    Bandarban
    "

    The output json is
    "
    {
        Bagerhat: Dhaka
        Bandarban: Dhaka
    }
    "
    """
    with open(read_file, 'r') as read_file:
        districts = read_file.readlines()
        districts = [district.strip() for district in districts]
        districts = {district: "Dhaka" for district in districts}
        with open(write_file, 'w') as write_file:
            json.dump(districts, write_file, indent=4)

def generateMinMax(data_file, out_file):
    with open(data_file, 'r') as read_file:
        data = json.load(read_file)
        climateVarMinMax = {}
        for climate_var in data:
            climateVarMinMax[climate_var] = {
                # First number is min, second is max
                "climatology": [9999999, -9999999],
                "anomaly": [9999999, -9999999],
                "variableAvg": 0,
            }
            currentCumulative = 0
            currentCount = 0

            for time_range in data[climate_var]["climatology"].keys():
                if time_range == "1995-2014":
                    
                    for district in data[climate_var]["climatology"][time_range]["historical"].keys():
                        currentVal = data[climate_var]["climatology"][time_range]["historical"][district]
                        currentCumulative += currentVal
                        currentCount += 1
                        if (currentVal < climateVarMinMax[climate_var]["climatology"][0]):
                            climateVarMinMax[climate_var]["climatology"][0] = currentVal
                        elif (currentVal > climateVarMinMax[climate_var]["climatology"][1]):
                            climateVarMinMax[climate_var]["climatology"][1] = currentVal
                            

                else:

                    for district in data[climate_var]["climatology"][time_range]["ssp245"].keys():
                        currentVal = data[climate_var]["climatology"][time_range]["ssp245"][district]
                        currentCumulative += currentVal
                        currentCount += 1
                        if (currentVal < climateVarMinMax[climate_var]["climatology"][0]):
                            climateVarMinMax[climate_var]["climatology"][0] = currentVal
                        if (currentVal > climateVarMinMax[climate_var]["climatology"][1]):
                            climateVarMinMax[climate_var]["climatology"][1] = currentVal

                    for district in data[climate_var]["climatology"][time_range]["ssp370"].keys():
                        currentVal = data[climate_var]["climatology"][time_range]["ssp370"][district]
                        currentCumulative += currentVal
                        currentCount += 1
                        if (currentVal < climateVarMinMax[climate_var]["climatology"][0]):
                            climateVarMinMax[climate_var]["climatology"][0] = currentVal
                        if (currentVal > climateVarMinMax[climate_var]["climatology"][1]):
                            climateVarMinMax[climate_var]["climatology"][1] = currentVal
            
                climateVarMinMax[climate_var]["variableAvg"] = currentCumulative / currentCount

            # Anomaly minmaxes
            for time_range in data[climate_var]["anomaly"].keys():
                for ssp in data[climate_var]["anomaly"][time_range].keys():
                    for district in data[climate_var]["anomaly"][time_range][ssp].keys():
                        currentVal = data[climate_var]["anomaly"][time_range][ssp][district]

                        if (currentVal < climateVarMinMax[climate_var]["anomaly"][0]):
                            climateVarMinMax[climate_var]["anomaly"][0] = currentVal
                        if (currentVal > climateVarMinMax[climate_var]["anomaly"][1]):
                            climateVarMinMax[climate_var]["anomaly"][1] = currentVal
        
        with open(out_file, 'w') as write_file:
            json.dump(climateVarMinMax, write_file, indent=4)

def parse_ngo_list_to_json(read_file, out_file):
    with open(read_file, 'r') as read_file:
        outputData = []
         # Read the first line of the file
        headers = read_file.readline().split('\t')

        # Read the rest of the lines
        lines = read_file.readlines()

        # Iterate over the lines
        for line in lines:
            splitLine = line.strip("\n").split('\t')

            # convert splitLine[6] which is a date string in 10-Dec-2013 format to a datetime object
           
            renewalDate = datetime.strptime(splitLine[6], '%d-%b-%Y')
            if (renewalDate > datetime.now()):
                line_json = {
                    "serialNum": splitLine[0],
                    "name": splitLine[1],
                    "address": splitLine[2],
                    "regNum": splitLine[3],
                    "regDate": splitLine[4],
                    "validUntil": splitLine[6],
                    "district": splitLine[7],
                    "country": splitLine[8],
                }
                outputData.append(line_json)
            
        print(len(outputData))
        with open(out_file, 'w') as write_file:
            json.dump(outputData, write_file, indent=4)


if __name__ == '__main__':
    # save_district_names('data/bd_districts.geojson', 'data/districts.txt')
    # sort_unique_lines_alphabetically('data/districts.txt')
    # save_json_districts('data/bd_districts.json')
    # sort_lines_alphabetically('data/json_districts.txt')
    # generate_district_data('data/bd_districts.json')
    # print(os.getcwd())
    # generate_headlines_and_images('data/climate_stories.json')
    # write_from_csv_to_json('data/sheetData.csv', 'data/generated_districts2.json')
    # reloadCentroids('data/bd_districts2.json', 'data/BDDistrictCentroids.geojson')
    # parse_world_bank_data('data/world_bank_data.json', 'data/world_bank_data2.json')
    generateMinMax('data/world_bank_data2.json', 'data/minMax.json')
    # parse_ngo_list_to_json('data/ngo_list.tsv', 'data/ngo_list.json')
    