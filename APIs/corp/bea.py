
import os
import requests
import pandas as pd
import httpx
from corp.utils import *
from dotenv import load_dotenv


load_dotenv()
api_key = os.environ.get("BUREAU_API_KEY")
base = "https://apps.bea.gov/api/data/?&UserID=" + api_key+ "&format=json"


def get_datasets() -> list[str]:
    """Fetches and prints available BEA datasets.
    
    Returns:
        list[str]: List of dataset names available from the BEA API
    """
    response = httpx.get(f"{base}&method=GETDATASETLIST").json()
    datasets = [dataset['DatasetName'] 
               for dataset in response["BEAAPI"]["Results"]['Dataset']]
    
    print(f"There are {len(datasets)} datasets available:")
    for dataset in datasets:
        print(f"• {dataset}")
        
    return datasets

    
    
def get_dataset_parameters(datasets: list[str], output_file: str = 'bea_parameters.txt') -> list:
    """Fetches and writes parameters for each BEA dataset.
    
    Args:
        datasets: List of dataset names to get parameters for
        output_file: Path to output file to write parameters to
        
    Returns:
        list: Combined parameters from all datasets
    """
    all_parameters = []
    with open(output_file, 'w') as f:
        for dataset_name in [d for d in datasets if d != 'apidatasetmetadata']:
            f.write(f"\n=== Parameters for {dataset_name} ===\n")
    #        print(f"\n=== Parameters for {dataset_name} ===")
            
            dataset = f"&datasetname={dataset_name}"
            method_get_params = "&method=GETPARAMETERLIST"
            
            try:
                r2 = httpx.get(f"{base}{method_get_params}{dataset}&ResultFormat=json").json()
                parameters = [(x['ParameterName'], x["ParameterDataType"], 
                              x['ParameterDescription'], x['ParameterIsRequiredFlag'], x['MultipleAcceptedFlag']) 
                             for x in r2["BEAAPI"]["Results"]['Parameter']]
                all_parameters.extend(parameters)

                # Sort parameters by required flag (1 first, then 0)
                sorted_params = sorted(parameters, key=lambda x: x[3], reverse=True)
                for p in sorted_params:
                    if p[3] == '1':  # Required parameter
                        line = f"[Required] {p[0]:<15} {p[1]:<10} {p[2]:<50} {p[3]} {p[4]}"
                        f.write(line + "\n")
   #                     print(line)
                    else:  # Optional parameter
                        line = f"• {p[0]:<15} {p[1]:<10} {p[2]:<50} {p[3]} {p[4]}"
                        f.write(line + "\n")
   #                     print(line)
            except Exception as e:
                error_msg = f"Error getting parameters for {dataset_name}: {str(e)}"
                f.write(error_msg + "\n")
                print(error_msg)
                
    return all_parameters