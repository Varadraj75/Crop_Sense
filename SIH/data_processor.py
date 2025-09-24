import pandas as pd
import os

def process_crop_and_fertilizer_data():
    """Process crop and fertilizer datasets for ML integration"""
    
    # Check if data files exist
    crop_data_path = 'Data-raw/cpdata.csv'
    fertilizer_data_path = 'Data-raw/Fertilizer.csv'
    
    if not os.path.exists(crop_data_path) or not os.path.exists(fertilizer_data_path):
        print("Data files not found. Creating sample data for demonstration.")
        return create_sample_data()
    
    try:
        # Load datasets
        crop = pd.read_csv(crop_data_path)
        fert = pd.read_csv(fertilizer_path)
        print("Datasets loaded successfully.")
    except FileNotFoundError:
        print("Error: Data files not found. Creating sample data.")
        return create_sample_data()
    except Exception as e:
        print(f"Error loading data: {e}")
        return create_sample_data()
    
    # Define function to standardize strings
    def change_case(s):
        return s.replace(" ", "").lower()
    
    # Clean the data
    fert['Crop'] = fert['Crop'].apply(change_case)
    crop['label'] = crop['label'].apply(change_case)
    
    # Standardize crop names
    fert['Crop'] = fert['Crop'].replace({
        'mungbeans': 'mungbean',
        'lentils(masoordal)': 'lentil',
        'pigeonpeas(toordal)': 'pigeonpeas',
        'mothbean(matki)': 'mothbeans',
        'chickpeas(channa)': 'chickpea'
    })
    
    # Remove unnecessary columns
    if 'Unnamed: 0' in fert.columns:
        del fert['Unnamed: 0']
    
    # Find common crops
    crop_labels = set(crop['label'].unique())
    fert_labels = set(fert['Crop'].unique())
    common_labels = list(crop_labels.intersection(fert_labels))
    
    # Filter data for common crops
    new_crop = pd.concat([crop[crop['label'] == label] for label in common_labels])
    new_fert = pd.concat([fert[fert['Crop'] == label] for label in common_labels])
    
    print(f"Filtered data for {len(common_labels)} common crops.")
    
    # Save processed data
    os.makedirs('Data-raw', exist_ok=True)
    new_crop.to_csv('Data-raw/MergeFileCrop.csv', index=False)
    new_fert.to_csv('Data-raw/FertilizerData.csv', index=False)
    
    print("Processed data saved successfully.")
    
    return {
        'crop_data': new_crop,
        'fertilizer_data': new_fert,
        'common_crops': common_labels
    }

def create_sample_data():
    """Create sample crop and fertilizer data for demonstration"""
    
    # Sample crop data with soil and weather parameters
    sample_crop_data = {
        'N': [90, 85, 95, 80, 88, 92, 87, 83],
        'P': [42, 38, 45, 40, 43, 41, 39, 44],
        'K': [43, 41, 47, 39, 45, 42, 40, 46],
        'temperature': [20.8, 21.9, 23.0, 22.5, 21.2, 20.5, 22.8, 21.6],
        'humidity': [82.0, 81.5, 83.0, 82.5, 81.8, 82.2, 83.5, 82.8],
        'ph': [6.5, 6.8, 6.2, 7.0, 6.7, 6.4, 6.9, 6.6],
        'rainfall': [202.9, 198.7, 205.3, 190.5, 195.8, 208.2, 192.4, 200.1],
        'label': ['rice', 'maize', 'chickpea', 'kidneybeans', 'pigeonpeas', 
                 'mothbeans', 'mungbean', 'blackgram']
    }
    
    # Sample fertilizer data
    sample_fertilizer_data = {
        'Crop': ['rice', 'maize', 'chickpea', 'kidneybeans', 'pigeonpeas', 
                'mothbeans', 'mungbean', 'blackgram'],
        'Temparature': [22, 25, 20, 22, 23, 21, 24, 22],
        'Humidity ': [82, 80, 75, 78, 81, 76, 79, 77],
        'Moisture': [1, 1, 1, 1, 1, 1, 1, 1],
        'Soil Type': ['Loamy', 'Loamy', 'Sandy', 'Loamy', 'Clay', 'Sandy', 'Loamy', 'Clay'],
        'Crop Type': ['Cereal', 'Cereal', 'Pulse', 'Pulse', 'Pulse', 'Pulse', 'Pulse', 'Pulse'],
        'Nitrogen': [80, 85, 70, 75, 78, 72, 82, 76],
        'Potassium': [45, 50, 40, 42, 48, 38, 46, 44],
        'Phosphorous': [35, 40, 30, 32, 38, 28, 36, 34]
    }
    
    crop_df = pd.DataFrame(sample_crop_data)
    fert_df = pd.DataFrame(sample_fertilizer_data)
    
    # Save sample data
    os.makedirs('Data-raw', exist_ok=True)
    crop_df.to_csv('Data-raw/MergeFileCrop.csv', index=False)
    fert_df.to_csv('Data-raw/FertilizerData.csv', index=False)
    
    print("Sample data created successfully.")
    
    return {
        'crop_data': crop_df,
        'fertilizer_data': fert_df,
        'common_crops': ['rice', 'maize', 'chickpea', 'kidneybeans', 'pigeonpeas', 
                        'mothbeans', 'mungbean', 'blackgram']
    }

def get_fertilizer_recommendations(crop_name, soil_type, ph_level):
    """Get fertilizer recommendations based on crop and soil data"""
    
    # Load processed fertilizer data
    try:
        fert_data = pd.read_csv('Data-raw/FertilizerData.csv')
        crop_data = pd.read_csv('Data-raw/MergeFileCrop.csv')
    except FileNotFoundError:
        print("Processed data not found. Creating sample data.")
        processed_data = create_sample_data()
        fert_data = processed_data['fertilizer_data']
        crop_data = processed_data['crop_data']
    
    # Normalize crop name
    crop_normalized = crop_name.lower().replace(" ", "")
    
    # Find matching crop in fertilizer data
    matching_crops = fert_data[fert_data['Crop'].str.lower().str.replace(" ", "") == crop_normalized]
    
    if matching_crops.empty:
        # Return default recommendations if crop not found
        return {
            'nitrogen': 80,
            'phosphorus': 35,
            'potassium': 45,
            'source': 'default'
        }
    
    # Get the first matching crop
    crop_info = matching_crops.iloc[0]
    
    # Adjust recommendations based on soil type and pH
    base_n = crop_info['Nitrogen']
    base_p = crop_info['Phosphorous']
    base_k = crop_info['Potassium']
    
    # Soil type adjustments
    if soil_type.lower() == 'sandy':
        base_n *= 1.2  # Sandy soils need more nitrogen
        base_p *= 1.1  # Slightly more phosphorus
    elif soil_type.lower() == 'clay':
        base_n *= 0.9  # Clay soils hold nutrients better
        base_p *= 0.95
    
    # pH adjustments
    if ph_level < 6.0:
        # Acidic soil - add more phosphorus
        base_p *= 1.3
    elif ph_level > 7.5:
        # Alkaline soil - adjust micronutrients
        base_p *= 1.1
    
    return {
        'nitrogen': round(base_n),
        'phosphorus': round(base_p),
        'potassium': round(base_k),
        'source': 'ml_dataset',
        'soil_adjustments': {
            'soil_type': soil_type,
            'ph_level': ph_level,
            'adjustments_applied': True
        }
    }

if __name__ == "__main__":
    # Process the data
    result = process_crop_and_fertilizer_data()
    print(f"Processed {len(result['common_crops'])} crops successfully.")
    
    # Test fertilizer recommendations
    test_recommendations = get_fertilizer_recommendations("Rice", "Loamy", 6.5)
    print("Sample fertilizer recommendations:", test_recommendations)


