import torch
import socket
import logging


def map_to_cuda(args, device=None, **kwargs):
    if isinstance(args, (list, tuple)):
        return [map_to_cuda(arg, device, **kwargs) for arg in args]
    elif isinstance(args, dict):
        return {k: map_to_cuda(v, device, **kwargs) for k, v in args.items()}
    elif isinstance(args, torch.Tensor):
        return args.cuda(device, **kwargs)
    else:
        raise TypeError("unsupported type for cuda migration")


def map_to_list(model_params):
    for k in model_params.keys():
        model_params[k] = model_params[k].detach().numpy().tolist()
    return model_params


def mapping_processes_to_gpus(gpu_config, process_id, worker_number):
    if gpu_config == None:
        device = torch.device("cpu")
        logging.info(device)
        # return gpu_util_map[process_id][1]
        return device
    else:
        logging.info(gpu_config)
        gpu_util_map = {}
        i = 0
        for host, gpus_util_map_host in gpu_config.items():
            for gpu_j, num_process_on_gpu in enumerate(gpus_util_map_host):
                for _ in range(num_process_on_gpu):
                    gpu_util_map[i] = (host, gpu_j)
                    i += 1
        logging.info("Process: %d" % (process_id))
        logging.info("host: %s" % (gpu_util_map[process_id][0]))
        logging.info("gethostname: %s" % (socket.gethostname()))
        logging.info("gpu: %d" % (gpu_util_map[process_id][1]))
        assert i == worker_number

        device = torch.device(
            "cuda:" + str(gpu_util_map[process_id][1])
            if torch.cuda.is_available() else "cpu")
        logging.info(device)
        # return gpu_util_map[process_id][1]
        return device
