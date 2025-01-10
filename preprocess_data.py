import pandas as pd
import numpy as np

# Load raw dataset (replace 'data.csv' with your actual file)
data = pd.read_csv("feed1.csv")  # Ensure the file contains a 'number' column

# Prepare features and labels
features = []
labels = []
for i in range(len(data) - 12):
    last_12_numbers = data['number'][i:i+12].tolist()
    distances = [abs(last_12_numbers[j] - last_12_numbers[j+1]) for j in range(len(last_12_numbers) - 1)]
    features.append(last_12_numbers + distances)  # Combine numbers and distances
    labels.append(data['number'][i+12])  # The next number is the label

# Convert to NumPy arrays
X = np.array(features)
y = np.array(labels)

# Save the processed dataset
np.save("features.npy", X)
np.save("labels.npy", y)
print("Dataset saved: features.npy, labels.npy")
