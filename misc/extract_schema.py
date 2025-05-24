import json

import requests


def extract_scheme_nav():
    # URL of the NAV data
    url = "https://www.amfiindia.com/spages/NAVAll.txt"

    # Fetch the content directly into memory
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to fetch data from the URL.")
        return

    # Split the content into lines
    lines = response.text.splitlines()

    # Prepare the output files
    tsv_output_file = "scheme_nav.tsv"
    json_output_file = "scheme_nav.json"

    # Initialize a list to store data for JSON
    json_data = []

    with open(tsv_output_file, "w") as tsv_file:
        # Write the header for the TSV file
        tsv_file.write("Scheme Name\tNet Asset Value\n")

        # Process each line
        for line in lines:
            # Skip lines that don't start with a numeric Scheme Code
            if not line.strip() or not line.split(";")[0].isdigit():
                continue

            # Split the line into fields
            fields = line.split(";")
            if len(fields) < 5:
                continue

            # Extract Scheme Name and NAV
            scheme_name = fields[3]
            nav = fields[4]

            # Write to the TSV file
            tsv_file.write(f"{scheme_name}\t{nav}\n")

            # Append to the JSON data list
            json_data.append({"Scheme Name": scheme_name, "Net Asset Value": nav})

    # Write the JSON data to a file
    with open(json_output_file, "w") as json_file:
        json.dump(json_data, json_file, indent=4)

    print(
        f"Extraction complete. Data saved to {tsv_output_file} and {json_output_file}"
    )


if __name__ == "__main__":
    extract_scheme_nav()
