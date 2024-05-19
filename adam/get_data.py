# Function to filter URLs
def filter_urls(input_file, output_file):
    with open(input_file, 'r') as file:
        urls = file.readlines()
    
    # Filter out URLs ending with "Champions-League"
    filtered_urls = [url for url in urls if not url.strip().endswith("Champions-League")]
    
    with open(output_file, 'w') as file:
        file.writelines(filtered_urls)

# Input and output file paths
input_file = 'urls/matchday_reports_pl.txt'
output_file = 'urls/matchday_reports_pl_updated.txt'

# Call the function
filter_urls(input_file, output_file)
