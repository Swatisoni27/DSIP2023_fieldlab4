from franz.openrdf.connect import ag_connect
from franz.openrdf.sail.allegrographserver import AllegroGraphServer
import requests
import json
from cedar.utils.searcher import search_instances_of
from cedar.utils.getter import get_resource

# get metadata instances from cedar

cedar_api_key = 'apiKey f1b9368fb41c87452d4a6d65524bde5137870db4ec456d6882546ef8d427c183'


# try for one instance:
template_instance_id = "https://repo.metadatacenter.org/template-instances/358040b9-4139-4750-baf6-28b74615766a"
template_instance_id = "https://repo.metadatacenter.org/template-instances/ec9e2252-79c5-4d2f-b830-d888b58e0e1e"
template_instance_id = "https://repo.metadatacenter.org/template-instances/39010703-2d69-473d-80ea-ddf2c1612163"
document = get_resource(cedar_api_key, template_instance_id)
# print(document)


# get all instances from our template
template_id = "https://repo.metadatacenter.org/templates/77db0ef8-f5d2-4c01-be28-1c182a755c53"
url_search = 'https://resource.metadatacenter.org/search?version=all&publication_status=all&is_based_on=https%3A%2F%2Frepo.metadatacenter.org%2Ftemplates%2F77db0ef8-f5d2-4c01-be28-1c182a755c53&sort=name&limit=100&sharing=null&mode=null'
template_instances_ids = search_instances_of(url_search, cedar_api_key , template_id)
i = 0
print(len(template_instances_ids))
for id in template_instances_ids:
    document = get_resource(cedar_api_key, id)

    # upload to allegrograph
    username = 'esthervandijk'
    pw = 'fitbitwearabletest'
    with ag_connect('DSIP_fieldlab4', user=username, password=pw) as conn:
        conn.addData(document)
        print(i)
        i += 1



# # document that works (datetime error)
# document = json.load(open('instance_test.json'))

# # upload to allegrograph
# username = 'esthervandijk'
# pw = 'fitbitwearabletest'
# with ag_connect('DSIP_test2', user=username, password=pw) as conn:
#     conn.addData(document)

# server = AllegroGraphServer(host="localhost", port=8080,
#                             user=username, password=pw)


