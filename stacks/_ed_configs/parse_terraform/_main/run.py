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
    stack.parse.add_required(key="terraform_type")
    stack.parse.add_required(key="resource_type")

    stack.parse.add_optional(key="filter_names",default="null")
    stack.parse.add_optional(key="terraform_mode",default="null")

    # Initialize 
    stack.init_variables()

    # reference pt
    description = "placehold - empty"
    cmd = 'echo "{}"'.format(description)

    stack.add_external_cmd(cmd=cmd,
                           order_type="empty_stack::shellout",
                           human_description=description,
                           display=False,
                           role="external/cli/execute")

    stack.set_parallel()

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
    main_id = _resource_info.get("_id")
    data = _resource_info["raw"]["terraform"]

    for resource in data["resources"]:
        for instance in resource["instances"]:

            if stack.terraform_type != resource.get("type"): continue
            if stack.terraform_mode and stack.terraform_mode != resource.get("mode"): continue
            if stack.filter_names and resource.get("name") not in stack.filter_names: continue

            values = instance["attributes"]
            values["resource_type"] = stack.resource_type
            if stack.vpc: values["vpc"] = stack.vpc

            _results = {}

            if not values.get("name") and resource.get("name"):
                values["name"] = resource["name"]

            if stack.provider: 
                values["provider"] = stack.provider
                _results["provider"] = stack.provider

            if hasattr(stack,"cluster"): 
                values["cluster"] = stack.cluster
                _results["cluster"] = stack.cluster
                
            if hasattr(stack,"instance"): 
                values["instance"] = stack.instance
                _results["instance"] = stack.instance

            if hasattr(stack,"schedule_id"): 
                values["schedule_id"] = stack.schedule_id
                _results["schedule_id"] = stack.schedule_id

            if hasattr(stack,"job_instance_id"): 
                values["job_instance_id"] = stack.job_instance_id
                _results["job_instance_id"] = stack.job_instance_id

            if hasattr(stack,"run_id"): 
                values["run_id"] = stack.run_id
                _results["run_id"] = stack.run_id

            if values.get("id") and not values.get("_id"):
                values["_id"] = values["id"]

            # AWS specific changes
            if values.get("provider") in [ "aws", "ec2" ] and values.get("arn"):

                if not values.get("region"): 
                    values["region"] = values["arn"].split(":")[3]

                if not values.get("_id"): 
                    values["_id"] = values["arn"].replace(":","_").replace("/","_")

                if values.get("tags"): 
                    if isinstance(values["tags"],dict):
                        values["tags"] = values["tags"].values()
                    else:
                        del values["tags"]

            # get hash for _id if not provided
            if not values.get("_id"): 
                values["_id"] = stack.get_hash_object(values)
           
            if main_id: values["parent"] = main_id

            _results["values"] = values

            stack.add_resource(**_results)

    # resource add resource_type=credentials \
    # name=test_credentials provider=self \
    # cred_type=test_type \
    # values='{"USERNAME":"test_user","PASSWORD":"test_password"}'

    return stack.get_results()
