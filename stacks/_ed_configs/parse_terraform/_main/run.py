def run(stackargs):

    # instantiate authoring stack
    stack = newStack(stackargs)

    # query parameters
    stack.parse.add_required(key="src_resource_type")

    stack.parse.add_optional(key="match",default="null") 

    stack.parse.add_optional(key="src_resource_name",default="null") 
    stack.parse.add_optional(key="id",default="null") 
    stack.parse.add_optional(key="vpc",default="null")
    stack.parse.add_optional(key="must_exists",default=True) 
    stack.parse.add_optional(key="provider",default="null") 

    # get inputs to insert
    stack.parse.add_required(key="resource_type")

    stack.parse.add_optional(key="filter_names",default="null")
    stack.parse.add_optional(key="mode",default="null")

    # Initialize 
    stack.init_variables()

    if stack.filter_names:
        filter_names = [ _name.strip() for _name in stack.filter_names.split(",") ]
        stack.set_variable("filter_names",filter_names)

    # get terraform resource
    if stack.match: 
        match = stack.match
    else:
        match = {"must_exists":stack.must_exists}
        match["resource_type"] = stack.src_resource_type
        if stack.src_resource_name: match["name"] = stack.src_resource_name
        if stack.id: match["id"] = stack.id
        if stack.provider: match["provider"] = stack.provider
        if stack.vpc: match["vpc"] = stack.vpc

    _resource_info = list(stack.get_resource(**match))[0]
    data = _resource_info["raw"]["terraform"]

    for resource in data["resources"]:
        for instance in resource["instances"]:

            if stack.resource_type != resource.get("type"): continue
            #if stack.mode != resource.get("mode"): continue
            #if stack.filter_names and resource.get("name") not in stack.filter_names: continue

            values = instance["attributes"]
            if stack.vpc: values["vpc"] = stack.vpc

            _results = { "values":values }

            if stack.provider: 
                _results["values"]["provider"] = stack.provider
                _results["provider"] = stack.provider

            if hasattr(stack,"cluster"): 
                _results["values"]["cluster"] = stack.cluster
                _results["cluster"] = stack.cluster
                
            if hasattr(stack,"instance"): 
                _results["values"]["instance"] = stack.instance
                _results["instance"] = stack.instance

            if hasattr(stack,"schedule_id"): 
                _results["values"]["schedule_id"] = stack.schedule_id
                _results["schedule_id"] = stack.schedule_id

            if hasattr(stack,"job_instance_id"): 
                _results["values"]["job_instance_id"] = stack.job_instance_id
                _results["job_instance_id"] = stack.job_instance_id

            if hasattr(stack,"run_id"): 
                _results["values"]["run_id"] = stack.run_id
                _results["run_id"] = stack.run_id

            stack.add_resource(**_results)

    # resource add resource_type=credentials \
    # name=test_credentials provider=self \
    # cred_type=test_type \
    # values='{"USERNAME":"test_user","PASSWORD":"test_password"}'

    return stack.get_results()
