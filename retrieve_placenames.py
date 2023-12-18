import argparse
import csv

def main():
    
    parser = argparse.ArgumentParser("Placename retriever", description="Retrieves placenames that are approved by a given user input list")
    parser.add_argument("gml_filepath", help=".txt file converted from .gml containing placename data")
    parser.add_argument("approved_filepath", help=".txt file containing approved name object types, one per line")
    parser.add_argument("csv_filepath", help=".csv file for storing the approved placenames")

    args = parser.parse_args()
    gml_filepath = args.gml_filepath
    approved_filepath = args.approved_filepath
    csv_filepath = args.csv_filepath

    all_lines = []

    with open(gml_filepath, 'r', encoding='utf-8') as file:
        for line in file:
            all_lines.append(line.strip())

    feature_members = []

    i = 0
    while i < len(all_lines):
        if all_lines[i] == "<gml:featureMember>":
            combined_string = ""
            combined_string += all_lines[i]

            i += 1

            while all_lines[i] != "</gml:featureMember>":
                combined_string += all_lines[i]
                i += 1

            combined_string += all_lines[i]

            feature_members.append(combined_string)

        else:
            feature_members.append(all_lines[i])

        i += 1

    approved_tags = []

    with open(approved_filepath, 'r', encoding='utf-8') as file:
        for line in file:
            approved_tags.append("<app:navneobjekttype>" + line.strip() + "</app:navneobjekttype>")

    placenames = []

    for feature_member in feature_members:
        if feature_member.startswith("<gml:featureMember><app:Sted") and any(tag in feature_member for tag in approved_tags):
            name_start_tag = "<app:komplettskrivemåte>"
            name_end_tag = "</app:komplettskrivemåte>"
            pos_start_tag = "<gml:pos>"
            pos_end_tag = "</gml:pos>"

            name_start_indices = [index for index in range(len(feature_member)) if feature_member.startswith(name_start_tag, index)]
            pos_start_indices = [index for index in range(len(feature_member)) if feature_member.startswith(pos_start_tag, index)]

            for name_start_index in name_start_indices:
                name_end_index = feature_member.find(name_end_tag, name_start_index)
                pos_start_index = next((index for index in pos_start_indices if index > name_start_index), pos_start_indices[-1])
                pos_end_index = feature_member.find(pos_end_tag, pos_start_index)

                name = feature_member[name_start_index + len(name_start_tag):name_end_index]
                pos = feature_member[pos_start_index + len(pos_start_tag):pos_end_index]

                pos = pos.split()
                name = name.replace("Å", "Aa").replace("å", "aa")

                placenames.append([name, pos[0], pos[1]])

    with open(csv_filepath, mode='w', newline='', encoding='utf-8') as file:
        csv_writer = csv.writer(file)

        csv_writer.writerows(placenames)

if __name__ == "__main__":
    main()