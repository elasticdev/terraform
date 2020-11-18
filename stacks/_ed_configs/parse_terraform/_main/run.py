def _get_subnet_ids(vpc_info,subnet_names=None):

    if not subnet_names: subnet_names = "private_prod,private"
    subnet_names = [ sg.strip() for sg in subnet_names.split(",") ]

    if not subnet_ids: return 
    
    return ",".join(subnet_ids)

def run(stackargs):

    # instantiate authoring stack
    stack = newStack(stackargs)

    stack.parse.add_required(key="resource_type")

    stack.parse.add_optional(key="resource_name",default="null") # e.g. managed
    stack.parse.add_optional(key="mode",default="null")
    stack.parse.add_optional(key="vpc",default="null")
    stack.parse.add_optional(key="must_exists",default=True) 
    stack.parse.add_optional(key="provider",default="null") 

    # Initialize 
    stack.init_variables()

    # get vpc info
    _lookup = {"must_exists":stack.must_exists}
    _lookup["resource_type"] = stack.resource_type
    if stack.provider: _lookup["provider"] = stack.provider
    if stack.vpc: _lookup["vpc"] = stack.vpc
    _resource_info = list(stack.get_resource(**_lookup))[0]

    data = _resource_info["raw"]["terraform"]

    results = []

    for resource in data["resources"]:
        for instance in resource["instances"]:

            if stack.resource_type != resource["type"]: continue
            if stack.resource_name and stack.resource_name != resource["name"]: continue
            if stack.mode and stack.mode != resource["mode"]: continue
            if stack.resource_name and stack.resource_name != resource["name"]: continue
            _results = instance["attributes"]

            results.append(_results)

    return stack.get_results()
