# vidhi_chatbot
# Set up Python Virtual Environment and Install Required Packages

# Step 1: Create a Virtual Environment
python3.11 -m venv venv

# Step 2: Activate the Virtual Environment
source venv/bin/activate

# Step 3: Upgrade pip, setuptools, and wheel
pip install --upgrade pip setuptools wheel

# Step 4: Install Required Packages
pip install pandas numpy sentence-transformers scikit-learn torch

# Step 5: Deactivate the Virtual Environment (when needed)
deactivate