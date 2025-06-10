import pandas as pd

# Load your dataset
df = pd.read_csv("newjosaa2024.csv")  # Replace with your actual file


# Convert rank columns to numeric (if not already)
df['Opening Rank'] = pd.to_numeric(df['Opening Rank'], errors='coerce')
df['Closing Rank'] = pd.to_numeric(df['Closing Rank'], errors='coerce')

# Drop rows with missing ranks
df.dropna(subset=["Opening Rank", "Closing Rank"], inplace=True)

# Group by unique combinations and aggregate min opening rank and max closing rank
df_grouped = df.groupby(["Institute", "Academic Program Name", "Quota", "Seat Type", "Gender"], as_index=False).agg({
    "Opening Rank": "min",
    "Closing Rank": "max"
})

# Save the reduced dataset
df_grouped.to_csv("reduced_josaa2024.csv", index=False)

print("Dataset reduced successfully!")
