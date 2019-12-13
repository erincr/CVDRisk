# CVD Risk

Class project aiming to predict 10-year probability of cardiovascular disease, and to incorporate zip codes. 

In this repo you'll find

    .
    ├── README.md
    |       └─ # This doc
    ├── PhenotypeDefinitionsAndHelpers.py
    |       └─ # Define comorbidities and medications of interest.
    ├── PrepareData.py
    |       └─ # Load data, define columns of interest, perform a train/validation/test split.
    ├── ClusterZipCodes.py, kmedioids.py
    |       └─ # Draw Kaplan-Meier curves, compute pairwise distances and cluster zip codes
    ├── HyperparameterSearch.py
    |       └─ # Run the hyperparameter search; write performance metrics to a .csv.
    └── Analysis
            └─ # Run the full pipelin
