import pandas as pd
import yaml
from tdc.single_pred import ADME


def get_and_transform_data():
    # get raw data
    target_subfolder = "BBB_Martins"
    splits = ADME(name=target_subfolder).get_split()
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
    fields_clean = ["compound_name", "SMILES", "penetrate_BBB", "split"]
    df.columns = fields_clean

    # data cleaning
    # remove leading and trailing white space characters
    df.compound_name = df.compound_name.str.strip()
    df = df.dropna()
    assert not df.duplicated().sum()

    # save to csv
    fn_data_csv = "data_clean.csv"
    df.to_csv(fn_data_csv, index=False)

    # create meta yaml
    meta = {
        "name": "blood_brain_barrier_martins_et_al",  # unique identifier, we will also use this for directory names
        "description": """As a membrane separating circulating blood and brain extracellular
fluid, the blood-brain barrier (BBB) is the protection layer that blocks most
foreign drugs. Thus the ability of a drug to penetrate the barrier to deliver
to the site of action forms a crucial challenge in development of drugs for the
central nervous system.""",
        "targets": [
            {
                "id": "penetrate_BBB",  # name of the column in a tabular dataset
                "description": "The ability of a drug to penetrate the blood brain barrier (1) or not (0)",
                "units": None,  # units of the values in this column (leave empty if unitless)
                "type": "boolean",
                "names": [  # names for the property (to sample from for building the prompts)
                    {"noun": "blood brain barrier penetration"},
                    {"noun": "ADME blood-brain barrier penetration"},
                    {"verb": "penetrates the blood brain barrier to reach the brain"},
                    {"verb": "penetrates the blood brain barrier"},
                ],
                "uris": None,
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
                "type": "SMILES",
                "description": "SMILES",  # description (optional, except for "Other")
            },
            {
                "id": "compound_name",  # column name
                "type": "Other",
                "names": [
                    {"noun": "compound name"},
                    {"noun": "drug name"},
                    {"noun": "generic drug name"},
                ],
                "description": "compound name",  # description (optional, except for "Other")
            },
        ],
        "license": "CC BY 4.0",  # license under which the original dataset was published
        "links": [  # list of relevant links (original dataset, other uses, etc.)
            {
                "url": "https://doi.org/10.1021/ci300124c",
                "description": "corresponding publication",
            },
            {
                "url": "https://rb.gy/0xx91v",
                "description": "corresponding publication",
            },
            {
                "url": "https://tdcommons.ai/single_pred_tasks/adme/#bbb-blood-brain-barrier-martins-et-al",
                "description": "data source",
            },
        ],
        "num_points": len(df),  # number of datapoints in this dataset
        "bibtex": [
            """@article{Martins2012,
doi = {10.1021/ci300124c},
url = {https://doi.org/10.1021/ci300124c},
year = {2012},
month = jun,
publisher = {American Chemical Society (ACS)},
volume = {52},
number = {6},
pages = {1686--1697},
author = {Ines Filipa Martins and Ana L. Teixeira and Luis Pinheiro
and Andre O. Falcao},
title = {A Bayesian Approach to in Silico Blood-Brain Barrier Penetration Modeling},
journal = {Journal of Chemical Information and Modeling}""",
            """@article{Wu2018,
doi = {10.1039/c7sc02664a},
url = {https://doi.org/10.1039/c7sc02664a},
year = {2018},
publisher = {Royal Society of Chemistry (RSC)},
volume = {9},
number = {2},
pages = {513--530},
author = {Zhenqin Wu and Bharath Ramsundar and Evan~N. Feinberg and Joseph
Gomes and Caleb Geniesse and Aneesh S. Pappu and Karl Leswing and Vijay Pande},
title = {MoleculeNet: a benchmark for molecular machine learning},
journal = {Chemical Science}""",
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
