# Query

Used to submit a query to CHP.

**URL** : `/query/`

**Method** : `POST`

**Auth required** : NO

**Data constraints**

Must be TRAPI compliant message.

**Data example**

Standard Probablistic Query:

```json
{
  "message": {
    "query_graph": {
      "edges": {
        "e0": {
          "type": "gene_to_disease_association",
          "source_id": "n0",
          "target_id": "n2"
        },
        "e1": {
          "type": "chemical_to_disease_or_phenotypic_feature_association",
          "source_id": "n1",
          "target_id": "n2"
        },
        "e2": {
          "type": "disease_to_phenotypic_feature_association",
          "source_id": "n2",
          "target_id": "n3",
          "properties": {
            "qualifier": ">=",
            "value": 500
          }
        }
      },
      "nodes": {
        "n0": {
          "type": "gene",
          "curie": "ENSEMBL:ENSG00000132155"
        },
        "n1": {
          "type": "chemical_substance",
          "curie": "CHEMBL:CHEMBL1201585"
        },
        "n2": {
          "type": "disease",
          "curie": "MONDO:0007254"
        },
        "n3": {
          "type": "phenotypic_feature",
          "curie": "EFO:0000714"
        }
      }
    }
  }
```

## Success Response

**Code** : `200 OK`

**Content example**

```json
{
  "message": {
    "query_graph": {
      "edges": {
        "e0": {
          "type": "gene_to_disease_association",
          "source_id": "n0",
          "target_id": "n2"
        },
        "e1": {
          "type": "chemical_to_disease_or_phenotypic_feature_association",
          "source_id": "n1",
          "target_id": "n2"
        },
        "e2": {
          "type": "disease_to_phenotypic_feature_association",
          "source_id": "n2",
          "target_id": "n3",
          "properties": {
            "qualifier": ">=",
            "value": 500
          }
        }
      },
      "nodes": {
        "n0": {
          "type": "gene",
          "curie": "ENSEMBL:ENSG00000132155"
        },
        "n1": {
          "type": "chemical_substance",
          "curie": "CHEMBL:CHEMBL1201585"
        },
        "n2": {
          "type": "disease",
          "curie": "MONDO:0007254"
        },
        "n3": {
          "type": "phenotypic_feature",
          "curie": "EFO:0000714"
        }
      }
    },
    "knowledge_graph": {
      "edges": {
        "kge0": {
          "type": "gene_to_disease_association",
          "source_id": "ENSEMBL:ENSG00000132155",
          "target_id": "MONDO:0007254"
        },
        "kge1": {
          "type": "chemical_to_disease_or_phenotypic_feature_association",
          "source_id": "CHEMBL:CHEMBL1201585",
          "target_id": "MONDO:0007254"
        },
        "kge2": {
          "type": "disease_to_phenotypic_feature_association",
          "source_id": "MONDO:0007254",
          "target_id": "EFO:0000714",
          "properties": {
            "qualifier": ">=",
            "value": 500
          },
          "has_confidence_level": 1.0
        }
      },
      "nodes": {
        "ENSEMBL:ENSG00000132155": {
          "type": "gene",
          "name": "RAF1"
        },
        "CHEMBL:CHEMBL1201585": {
          "type": "chemical_substance",
          "name": "TRASTUZUMAB"
        },
        "MONDO:0007254": {
          "type": "disease"
        },
        "EFO:0000714": {
          "type": "phenotypic_feature"
        }
      }
    },
    "results": [
      {
        "node_bindings": {
          "n0": {
            "kg_id": "ENSEMBL:ENSG00000132155"
          },
          "n1": {
            "kg_id": "CHEMBL:CHEMBL1201585"
          },
          "n2": {
            "kg_id": "MONDO:0007254"
          },
          "n3": {
            "kg_id": "EFO:0000714"
          }
        },
        "edge_bindings": {
          "e0": {
            "kg_id": "kge0"
          },
          "e1": {
            "kg_id": "kge1"
          },
          "e2": {
            "kg_id": "kge2"
          }
        }
      }
    ]
  }
}
```

## Error Response

TODO
