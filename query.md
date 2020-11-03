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
      "nodes": {
        "n0": {
          "type": "gene",
          "curie": "ENSEMBL:ENSG00000132155"
        },
        "n1": {
          "type": "chemical_substance",
          "curie": "CHEMBL:CHEMBL88"
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
      "edges": [
        {
          "id": "e0",
          "type": "gene_to_disease_association",
          "source_id": "n0",
          "target_id": "n2"
        },
        {
          "id": "e1",
          "type": "chemical_to_disease_or_phenotypic_feature_association",
          "source_id": "n1",
          "target_id": "n2"
        },
        {
          "id": "e2",
          "type": "disease_to_phenotypic_feature_association",
          "source_id": "n2",
          "target_id": "n3",
          "properties": {
            "qualifier": ">=",
            "value": 500
          }
        }
      },
      "nodes": [
        {
          "id": "n0",
          "type": "gene",
          "curie": "ENSEMBL:ENSG00000132155"
        },
        {
          "id": "n1",
          "type": "chemical_substance",
          "curie": "CHEMBL:CHEMBL88"
        },
        {
          "id": "n2",
          "type": "disease",
          "curie": "MONDO:0007254"
        },
        {
          "id": "n3",
          "type": "phenotypic_feature",
          "curie": "EFO:0000714"
        }
      ]
    },
    "knowledge_graph": {
      "edges": [
        {
          "id": "cff35aa2-3a95-4e84-aa33-18ef576025e8",
          "type": "gene_to_disease_association",
          "source_id": "7c89d32e-2a6e-4cbc-9ece-2ca07c6a458e",
          "target_id": "1f5fa86b-ffa7-437c-9033-74d17c3f4795"
        },
        {
          "id": "51cc7d6b-c63e-458a-b4f4-53c3a6210b05",
          "type": "chemical_to_disease_or_phenotypic_feature_association",
          "source_id": "298b0b61-7e43-4334-9516-898c10708019",
          "target_id": "1f5fa86b-ffa7-437c-9033-74d17c3f4795"
        },
        {
          "id": "08cf0382-a43f-4a5b-a556-7b934dc7eb36",
          "type": "disease_to_phenotypic_feature_association",
          "source_id": "1f5fa86b-ffa7-437c-9033-74d17c3f4795",
          "target_id": "4110a6b6-6178-4321-9c12-f4b253b2727c",
          "properties": {
            "qualifier": ">=",
            "value": 500
          },
          "has_confidence_level": 0.999718157375553
        }
      ],
      "nodes": [
        {
          "id": "7c89d32e-2a6e-4cbc-9ece-2ca07c6a458e",
          "type": "gene",
          "curie": "ENSEMBL:ENSG00000132155",
          "name": "RAF1"
        },
        {
          "id": "298b0b61-7e43-4334-9516-898c10708019",
          "type": "chemical_substance",
          "curie": "CHEMBL:CHEMBL88",
          "name": "CYTOXAN"
        },
        {
          "id": "1f5fa86b-ffa7-437c-9033-74d17c3f4795",
          "type": "disease",
          "curie": "MONDO:0007254"
        },
        {
          "id": "4110a6b6-6178-4321-9c12-f4b253b2727c",
          "type": "phenotypic_feature",
          "curie": "EFO:0000714"
        }
      ]
    },
    "results": {
      "node_bindings": [],
      "edge_bindings": [
        {
          "qg_id": "e2",
          "kg_id": "08cf0382-a43f-4a5b-a556-7b934dc7eb36"
        }
      ]
    }
  }
}
```

## Error Response

TODO
