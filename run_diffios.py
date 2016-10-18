from diffios import DiffiosFile
from diffios import DiffiosDiff

# def diffios_diff_to_csv():
# anchor_directory = os.path.join(os.getcwd(), "anchor")
# candidate_filename = "10.145.63.91.conf"
# candidate_file = os.path.join(anchor_directory, candidate_filename)

# partitioned_candidate_file = partition_ignored_lines(candidate_file)
# candidate = partitioned_candidate_file['recorded']
# candidate_ignored = partitioned_candidate_file['ignored']
# candidate_hn = fetch_hostname(remove_invalid_lines(candidate_file))

# with open("diffs.csv", 'a') as csvfile:
    # csvwriter = csv.writer(csvfile, lineterminator='\n')
    # csvwriter.writerow([
        # "Case File", "Case Hostname", "Candidate File", "Additional", "Missing"
    # ])
    # i = 1
    # for fin in os.listdir(anchor_directory):
        # print("{0}:\t{1}".format(i, fin))
        # case_file = os.path.join(anchor_directory, fin)
        # partitioned_case_file = partition_ignored_lines(case_file)
        # case = partitioned_case_file['recorded']
        # case_ignored = partitioned_case_file['ignored']
        # case_hn = fetch_hostname(remove_invalid_lines(case_file))
        # content = diff_to_csv_format(diff(candidate, case))
        # csvwriter.writerow([fin, case_hn, candidate_filename] + content)
        # i += 1

