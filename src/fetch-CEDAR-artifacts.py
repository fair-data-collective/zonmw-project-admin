import requests
import json
import os
from pathlib import Path


def _detect_artifact(artifact_id):
    """Detects type of artifact based on artifact URL.

    Parameters
    ----------
    artifact_id : str
        String in form of resolvable URL

    Returns
    -------
    artifact_type : str
        String representing artifact type, it can be ['field',element', 'template' or 'instance template']
    artifact_url_str : str
        Unique string from the artifact id representing artifact_type
    """

    artifact_type = {
        "field": "/template-fields/",
        "element": "/template-elements/",
        "template": "/templates/",
        "instance": "/template-instances/",
    }
    if artifact_id.find(artifact_type["field"]) != -1:
        return "field", artifact_type["field"].replace("/", "")
    if artifact_id.find(artifact_type["element"]) != -1:
        return "element", artifact_type["element"].replace("/", "")
    if artifact_id.find(artifact_type["template"]) != -1:
        return "template", artifact_type["template"].replace("/", "")
    if artifact_id.find(artifact_type["instance"]) != -1:
        return "instance", artifact_type["instance"].replace("/", "")
    else:
        raise ValueError(
            "artifact_id does not contain information about CEDAR artifact."
        )


def _get_api_url(artifact_id):
    """Gets artifact URL and artifact UUID for curl command.

    Parameters
    ----------
    artifact_id : str
        String in form of resolvable URL

    Returns
    -------
    api_url : str
        URL structured according to the CEDAR API for curl get command
    artifact_uuid : str
        Universally unique identifier of the CEDAR artifact
    """
    base_url = "https://resource.metadatacenter.org/artifact_str/https%3A%2F%2Frepo.metadatacenter.org%2Fartifact_str%2F"
    artifact_type, artifact_url_str = _detect_artifact(artifact_id)

    base_url = base_url.replace("artifact_str", artifact_url_str)
    url_drop = "https://repo.metadatacenter.org/artifact_str/".replace(
        "artifact_str", artifact_url_str
    )
    artifact_uuid = artifact_id.replace(url_drop, "")

    return artifact_uuid, base_url + artifact_uuid


def _get_artifact(artifact_id, api_key):

    artifact_type, artifact_url_str = _detect_artifact(artifact_id)
    artifact_uuid, api_url = _get_api_url(artifact_id)

    headers = {
        "Accept": "application/json",
        "Authorization": "apiKey " + api_key,
    }

    artifact_json = requests.get(api_url, headers=headers).json()
    artifact_name = artifact_json["schema:name"]

    return artifact_name, artifact_type, artifact_uuid, artifact_json


def store_artifact(artifact_id, api_key, base_path="./cedar-assets/"):
    artifact_name, artifact_type, artifact_uuid, artifact_json = _get_artifact(
        artifact_id, api_key
    )

    dir_path = os.path.dirname(base_path + artifact_type.capitalize() + "s/")
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)

    file_name = artifact_name + "_" + artifact_uuid[-6:] + ".json"
    file_path = dir_path + "/" + file_name

    with open(file_path, "w") as json_file:
        json.dump(artifact_json, json_file, indent=4)


CEDAR_API = os.environ["CEDAR_API"]

HEADER = {
    "Accept": "application/json",
    "Authorization": "apiKey " + CEDAR_API,
}

FOLDER_CMD = "contents?version=all&publication_status=all&sort=name"

uuid_templates = "50b3f988-1443-454f-9f4a-365844e49ef1"  # Project Template Templates
uuid_elements = "8c5c1001-1864-46df-8888-8f60b9e96deb"  # Project Template Element

folder_url_templates = (
    "https://resource.metadatacenter.org/folders/https%3A%2F%2Frepo.metadatacenter.org%2Ffolders%2F"
    + uuid_templates
    + "/"
)
folder_url_elements = (
    "https://resource.metadatacenter.org/folders/https%3A%2F%2Frepo.metadatacenter.org%2Ffolders%2F"
    + uuid_elements
    + "/"
)


folder_content = requests.get(folder_url_templates + FOLDER_CMD, headers=HEADER).json()

for artifact in folder_content["resources"]:
    if artifact["resourceType"] != "instance" and artifact["resourceType"] != "folder":
        store_artifact(artifact["@id"], CEDAR_API)

folder_content = requests.get(folder_url_elements + FOLDER_CMD, headers=HEADER).json()

for artifact in folder_content["resources"]:
    if artifact["resourceType"] != "instance" and artifact["resourceType"] != "folder":
        store_artifact(artifact["@id"], CEDAR_API)

