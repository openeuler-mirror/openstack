import json  
import requests  
  
def get_json_from_pypi(project, version=None):  
    """  
    Retrieve JSON information for a specified project and version from PyPI.  
      
    :param project: The name of the project.  
    :param version: The version of the project, defaults to None, which means the latest version.  
    :return: The JSON information of the project from PyPI.  
    :raises: requests.exceptions.RequestException if the request fails.  
             ValueError if the response status code is not 200 or the returned JSON is invalid.  
    """  
    base_url = 'https://pypi.org/pypi/{project}/'  
    if version and version.lower() != 'latest':  
        url = f'{base_url}{version}/json'  
    else:  
        url = f'{base_url}json'  
    response = requests.get(url.format(project=project))  
    if response.status_code != 200:
        raise Exception("%s-%s doesn't exist on pypi" % (project, version))
    return json.loads(response.content.decode())
  
def get_home_page(pypi_json):  
    """  
    Extract the homepage link of the project from the PyPI JSON information.  
      
    :param pypi_json: The JSON project information retrieved from PyPI.  
    :return: The homepage link of the project, or None if not found.  
    """  
    project_urls = pypi_json.get("info", {}).get("project_urls", {})  
    homepage = project_urls.get("Homepage")  
    if not homepage:  
        # Fallback to the old field if "Homepage" is not found in project_urls.  
        homepage = pypi_json.get("info", {}).get("project_url")  
    return homepage