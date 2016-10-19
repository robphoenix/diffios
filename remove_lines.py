import os

files_dir = os.path.join(os.getcwd(), "jon_comparison")


for config_file in os.listdir(files_dir):
    output = []
    with open(os.path.join(files_dir, config_file)) as fin:
        print("\nAccessing:\t{}".format(config_file))
        # content = fin.readlines()
        previous_line = ""
        for line in fin.readlines():
            if previous_line.startswith("end"):
                break
            else:
                output.append(line)
                previous_line = line
    with open(os.path.join(files_dir, config_file), 'w') as fout:
        print("Writing:\t{}".format(config_file))
        fout.writelines(output)
