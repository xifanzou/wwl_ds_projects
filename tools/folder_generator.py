import os


def create_paths(module_name=str) -> str:
    data_folder = os.path.abspath(os.path.join(str(module_name), 'data'))
    data_raw_pa = os.path.abspath(os.path.join(data_folder, 'raw'))
    data_pro_pa = os.path.abspath(os.path.join(data_folder, 'processed'))
    data_exp_pa = os.path.abspath(os.path.join(data_folder, 'export'))
    
    print(data_raw_pa)
    print(data_pro_pa)

    return [data_folder, data_raw_pa, data_pro_pa, data_exp_pa]

def create_folder(module_name=str):
    res = create_paths(module_name)
    for x in res:
        if not os.path.exists(x): os.makedirs(x)
    
    