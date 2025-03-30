def handle_arguments(argums: str) -> list[str]:
    args = argums[1].split(' ')
    META_FILE=''
    SAVE_PATH=''
    DATASET_PATH=''
    INTRUSIVE_EVAL=''
    for index in range(0, len(args)):
        arg = args[index]
        match arg:
            case '--meta_file':
                META_FILE = args[index + 1]
            case '--dataset_path':
                DATASET_PATH = args[index + 1]
            case '--save_path':
                SAVE_PATH = args[index + 1]
            case '--intrusive_eval':
                INTRUSIVE_EVAL = args[index + 1]
            case _:
                continue

    return META_FILE, DATASET_PATH, SAVE_PATH, INTRUSIVE_EVAL