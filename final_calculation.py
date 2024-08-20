import pandas as pd
import os

def analyze_energy_data(directory):
    # File paths
    estimated_time_file = os.path.join(directory, "estimated_time.txt")
    output_file = os.path.join(directory, "trail_energy_analysis.txt")
    
    # Load the estimated time data
    estimated_times = {}
    with open(estimated_time_file, 'r') as file:
        for line in file:
            parts = line.strip().split()
            trail_name = parts[0]
            estimated_time = float(parts[1])
            estimated_times[trail_name] = estimated_time
    
    # Process each CSV file in the directory
    output_lines = []
    for filename in os.listdir(directory):
        if filename.endswith("_matched_adjusted_energy_data.csv"):
            trail_name = filename.replace("_matched_adjusted_energy_data.csv", "")
            csv_file = os.path.join(directory, filename)
            
            # Load the CSV file
            df = pd.read_csv(csv_file)
            
            # Calculate the sum of the energy column
            total_energy = df['energy'].sum()
            
            # Get the corresponding estimated time
            if trail_name in estimated_times:
                estimated_time = estimated_times[trail_name]
                # Calculate the result
                energy_per_minute = total_energy / estimated_time
                output_lines.append(f"{trail_name}: Total Energy = {total_energy:.1f}, Energy per Minute = {energy_per_minute:.2f}")
            else:
                output_lines.append(f"{trail_name}: No estimated time found.")
    
    # Write the output to a text file
    with open(output_file, 'w') as file:
        for line in output_lines:
            file.write(line + "\n")
    
    print(f"Analysis complete. Results saved to {output_file}")

# Example usage: replace 'your_directory_path' with the path to the directory containing the CSV and TXT files
directory_path = "./RESULT"  # Replace with your actual directory path
analyze_energy_data(directory_path)
