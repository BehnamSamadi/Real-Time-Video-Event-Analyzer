def parse_stream_prop(request):
    keys = ['id', 'address', 'sample_duration', 'sample_size', 'active_delay', 'sensitivity']
    for key in keys:
        if key not in request.keys():
            return
    return request
    

def parse_stream_id(request):
    if 'stream_id' not in request.keys():
        return
    return int(request['stream_id'])
    