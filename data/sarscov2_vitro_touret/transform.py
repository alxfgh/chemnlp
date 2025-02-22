import pandas as pd
import yaml
from tdc.single_pred import HTS


def get_and_transform_data():
    # get raw data
    splits = HTS(name="SARSCoV2_Vitro_Touret").get_split()
    df_train = splits["train"]
    df_valid = splits["valid"]
    df_test = splits["test"]
    df_train["split"] = "train"
    df_valid["split"] = "valid"
    df_test["split"] = "test"
    df = pd.concat([df_train, df_valid, df_test], axis=0)

    fn_data_original = "data_original.csv"
    df.to_csv(fn_data_original, index=False)
    del df

    # create dataframe
    df = pd.read_csv(
        fn_data_original,
        delimiter=",",
    )  # not necessary but ensure we can load the saved data

    # check if fields are the same
    fields_orig = df.columns.tolist()
    assert fields_orig == ["Drug_ID", "Drug", "Y", "split"]

    # overwrite column names = fields
    fields_clean = ["compound_id", "SMILES", "activity_SARSCoV2", "split"]
    df.columns = fields_clean

    assert not df.duplicated().sum()

    # save to csv
    fn_data_csv = "data_clean.csv"
    df.to_csv(fn_data_csv, index=False)

    # create meta yaml
    meta = {
        "name": "sarscov2_vitro_touret",  # unique identifier, we will also use this for directory names
        "description": """An in-vitro screen of the Prestwick chemical library composed of 1,480
approved drugs in an infected cell-based assay.""",
        "targets": [
            {
                "id": "activity_SARSCoV2",  # name of the column in a tabular dataset
                "description": "whether it is active against SARSCoV2 (1) or not (0).",
                "units": None,  # units of the values in this column (leave empty if unitless)
                "type": "boolean",
                "names": [  # names for the property (to sample from for building the prompts)
                    {"noun": "activity against the Corona virus"},
                    {"noun": "activity against SARSCoV2"},
                    {"noun": "activity against COVID19"},
                    {"adjective": "active against the Corona virus"},
                    {"adjective": "active against SARSCoV2"},
                    {"adjective": "active against COVID19"},
                ],
            },
        ],
        "benchmarks": [
            {
                "name": "TDC",  # unique benchmark name
                "link": "https://tdcommons.ai/",  # benchmark URL
                "split_column": "split",  # name of the column that contains the split information
            },
        ],
        "identifiers": [
            {
                "id": "SMILES",  # column name
                "type": "SMILES",  # can be "SMILES", "SELFIES", "IUPAC", "Other"
                "description": "SMILES",  # description (optional, except for "Other")
            },
        ],
        "license": "CC BY 4.0",  # license under which the original dataset was published
        "links": [  # list of relevant links (original dataset, other uses, etc.)
            {
                "url": "https://doi.org/10.1038/s41598-020-70143-6",
                "description": "corresponding publication",
            },
            {
                "url": "https://tdcommons.ai/single_pred_tasks/hts/#sars-cov-2-in-vitro-touret-et-al",
                "description": "Data source",
            },
        ],
        "num_points": len(df),  # number of datapoints in this dataset
        "bibtex": [
            """@article{Touret2020,
doi = {10.1038/s41598-020-70143-6},
url = {https://doi.org/10.1038/s41598-020-70143-6},
year = {2020},
month = aug,
publisher = {Springer Science and Business Media LLC},
volume = {10},
number = {1},
author = {Franck Touret and Magali Gilles and Karine Barral and  Antoine Nougairede
and Jacques van Helden and Etienne Decroly and Xavier de Lamballerie and Bruno Coutard},
title = {In vitro screening of a FDA approved chemical library reveals potential inhibitors of
SARS-CoV-2 replication},
journal = {Scientific Reports}""",
        ],
    }

    def str_presenter(dumper, data):
        """configures yaml for dumping multiline strings
        Ref: https://stackoverflow.com/questions/8640959/how-can-i-control-what-scalar-form-pyyaml-uses-for-my-data
        """
        if data.count("\n") > 0:  # check for multiline string
            return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
        return dumper.represent_scalar("tag:yaml.org,2002:str", data)

    yaml.add_representer(str, str_presenter)
    yaml.representer.SafeRepresenter.add_representer(
        str, str_presenter
    )  # to use with safe_dum
    fn_meta = "meta.yaml"
    with open(fn_meta, "w") as f:
        yaml.dump(meta, f, sort_keys=False)

    print(f"Finished processing {meta['name']} dataset!")


if __name__ == "__main__":
    get_and_transform_data()
