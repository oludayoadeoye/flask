import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pickle

# Load the dataset
data = pd.read_csv("roulette_data.csv")

# Separate features (X) and target labels (y)
X = data.drop(columns=["Target"])  # Features: Spins, distances, etc.
y = data["Target"]  # Target: Next predicted number

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize the LightGBM model
model = LGBMClassifier(random_state=42, n_estimators=100, learning_rate=0.1)

# Train the LightGBM model
print("Training LightGBM model...")
model.fit(X_train, y_train)

# Evaluate the model
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy:.2f}")

# Save the trained model to a file
with open("model.pkl", "wb") as f:
    pickle.dump(model, f)
    print("Model saved as 'model.pkl'")
