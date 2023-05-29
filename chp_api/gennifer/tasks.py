import os
import time
import pandas as pd
import requests 

from celery import shared_task

from .models import Dataset, Gene, InferenceStudy, InferenceResult
from dispacter.models import DispatcherSettings

def normalize_nodes(curies):
    dispatcher_settings = DispatcherSettings.load()
    base_url = dispatcher_settings.sri_node_normalizer_baseurl
    return requests.post(
            f'{base_url}/get_normalized_nodes',
            json={"curies": curies}
            )

def extract_variant_info(gene_id):
    split = gene_id.split('(')
    gene_id = split[0]
    if len(split) > 1:
        variant_info = split[1][:-1]
    else:
        variant_info = None
    return gene_id, variant_info

def save_inference_study(study, status, failed=False):
    study.status = status["task_status"]
    if failed:
        study.message = status["task_result"]
    else:
        # Construct Dataframe from result
        df = pd.DataFrame.from_records(status["task_result"])
        
        # Add study edge weight features
        stats = df["EdgeWeight"].astype(float).describe()
        study.max_study_edge_weight = stats["max"]
        study.min_study_edge_weight = stats["min"]
        study.avg_study_edge_weight = stats["mean"]
        study.std_study_edge_weight = stats["std"]

        # Collect all genes
        genes = set()
        for _, row in df.iterrows():
            gene1, _ = extract_variant_info(row["Gene1"])
            gene2, _ = extract_variant_info(row["Gene2"])
            genes.add(gene1)
            genes.add(gene2)

        # Normalize
        res = normalize_nodes(list(genes))
        
        # Now Extract results
        for _, row in df.iterrows():
            # Construct Gene Objects
            gene1, variant_info1 = extract_variant_info(row["Gene1"])
            gene2, variant_info2 = extract_variant_info(row["Gene2"])
            gene1_obj, created = Gene.objects.get_or_create(
                    name=res[gene1]["id"]["label"],
                    curie=gene1,
                    variant=variant_info1,
                    )
            if created:
                gene1_obj.save()
            gene2_obj, created = Gene.objects.get_or_create(
                    name=res[gene2]["id"]["label"],
                    curie=gene2,
                    variant=variant_info2,
                    )
            if created:
                gene2_obj.save()
            # Construct and save Result
            result = InferenceResult.objects.create(
                    tf=gene1_obj,
                    target=gene2_obj,
                    edge_weight=row["EdgeWeight"],
                    study=study,
                    )
            result.save()
    study.save()
    return True

def get_status(algo, task_id):
    return requests.get(f'{algo.url}/status/{task_id}').json()

@shared_task(name="create_gennifer_task")
def create_task(algorithm, zenodo_id, hyperparameters, user):
    # Initialize dataset instance
    dataset, created = Dataset.objects.get_or_create(
            zenodo_id=zenodo_id,
            upload_user=user,
            )
    if created:
        dataset.save()

    # Send to gennifer app
    gennifer_request = {
            "zenodo_id": zenodo_id,
            "hyperparameters": hyperparameters,
            }
    task["task_id"] = requests.post(f'{algo.url}/run', data=gennifer_request)

    # Get initial status
    status = get_status(algo, task["task_id"])
    
    # Create Inference Study
    study = InferenceStudy.objects.create(
            algorithm=algo,
            user=user,
            dataset=dataset,
            status=status["task_status"],
            )
    # Save initial study
    study.save()

    # Enter a loop to keep checking back in and populate the study once it has completed.
    #TODO: Not sure if this is best practice
    while True:
        # Check in every 2 seconds
        time.sleep(2)
        status = get_status(algo, task["task_id"])
        if status["task_status"] == 'SUCCESS':
            return save_inference_study(study, status)
        if status["task_status"] == "FAILURE":
            return save_inference_study(study, status, failed=True)
        if status["task_status"] != study.status:
            study.status = status["task_status"]
            study.save()
