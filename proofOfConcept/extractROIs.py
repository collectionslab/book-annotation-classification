"""
To be used on the csv file generated from zooniverse. Currently assumes the
zooniverse data and meta data of our annotations are in the same directory.
"""

import pandas as pd
import json

CSV_PATH = "book-annotation-classification-classifications-11June2018.csv"

# ASSUMES FILES ARE .PNG FORMAT
META_DATA_PATH = "books meta data.csv"

# WARNING! CSV file is inconsistent with the key identifier for the key names.
# "filename" "manifest.csv" and "uclaclark_QD25S87_0291.png" are all keys to
# retrieve the file name


def extractROIs(csv_file_path):
    assert csv_file_path
    df = pd.read_csv(csv_file_path, usecols=["annotations", "subject_data",
                                             "subject_ids"])

    # need to add this bit to map file names to the randomized IDs
    df_meta = pd.read_csv(META_DATA_PATH, usecols=["ID", "File Name"])
    name2id = dict()
    for index, row in df_meta.iterrows():
        name2id[row[1].replace(".png", ".jpg")] = str(row[0]) + ".png"

        fileNames = []
        coordinates = []

        # gets all fileNames of images in rows that use "filename" as the key
        for index, row in df.iterrows():

            s_id = str(row["subject_ids"])

            s_data = json.loads(row["subject_data"])

            try:  # if this succeeds, then we can retrieve its annotations

                fn = s_data[s_id]["filename"]

                # name2id to convert file name to our id naming convention
                fileNames.append(name2id[s_data[s_id]["filename"]])

                tasks = json.loads(df.iloc[index]["annotations"])

                imageCoordinates = []

                for t in tasks:

                    if t["task"] == "T1":
                        listOfCoordinates = t["value"]

                        for coord in listOfCoordinates:
                            formattedCoord = int(
                                coord["x"]), int(
                                coord["y"]), int(
                                coord["width"]), int(
                                coord["height"])
                            imageCoordinates.append(formattedCoord)

                coordinates.append(imageCoordinates)
            except BaseException:
                try:  # if this succeeds, then get all the clark images

                    fn = s_data[s_id]["manifest.csv"]

                    fileNames.append(s_data[s_id]["manifest.csv"])

                    tasks = json.loads(df.iloc[index]["annotations"])

                    imageCoordinates = []

                    for t in tasks:

                        if t["task"] == "T1":
                            listOfCoordinates = t["value"]

                            for coord in listOfCoordinates:
                                formattedCoord = int(
                                    coord["x"]), int(
                                    coord["y"]), int(
                                    coord["width"]), int(
                                    coord["height"])
                                imageCoordinates.append(formattedCoord)

                    coordinates.append(imageCoordinates)
                except BaseException:
                    try:  # if this succeeds, then get all the remaining images

                        fn = s_data[s_id]["uclaclark_QD25S87_0291.png"]

                        fileNames.append(
                            s_data[s_id]["uclaclark_QD25S87_0291.png"])

                        tasks = json.loads(df.iloc[index]["annotations"])

                        imageCoordinates = []

                        for t in tasks:

                            if t["task"] == "T1":
                                listOfCoordinates = t["value"]

                                for coord in listOfCoordinates:
                                    formattedCoord = int(
                                        coord["x"]), int(
                                        coord["y"]), int(
                                        coord["width"]), int(
                                        coord["height"])
                                    imageCoordinates.append(formattedCoord)

                        coordinates.append(imageCoordinates)
                    except BaseException:
                        pass

        duplicatedRegionData = list(zip(fileNames, coordinates))

        d = dict()

        # Some of the annotations that zooniverse users made did not fit with
        # our definition of an annotation (e.g. a stray mark)
        falsePositives = [
            "2032.png",
            "2269.png",
            "2512.png",
            "2565.png",
            "2710.png",
            "2736.png",
            "uclaclark_AY751Z71673_0061.png",
            "uclaclark_AY751Z71673_0119.png",
            "uclaclark_AY751Z71673_0124.png",
            "uclaclark_QL955H34_0068.png",
            "uclaclark_QL955H34_0071.png",
            "uclaclark_QL955H34_0077.png",
            "uclaclark_QL955H34_0108.png",
            "uclaclark_QL955H34_0113.png",
            "uclaclark_QL955H34_0125.png",
            "uclaclark_QL955H34_0126.png",
            "uclaclark_QL955H34_0139.png",
            "uclaclark_QL955H34_0156.png",
            "uclaclark_QL955H34_0160.png",
            "uclaclark_QL955H34_0178.png",
            "uclaclark_QL955H34_0193.png",
            "uclaclark_QL955H34_0223.png",
            "uclaclark_QL955H34_0316.png",
            "uclaclark_QL955H34_0316.png",
            "uclaclark_QL955H34_0321.png"]

        region_count = 0
        for pair in duplicatedRegionData:

            # skin unannotated regions
            if pair[0] in falsePositives or not pair[1]:
                continue

            if pair[0] in d:
                d[pair[0]] += pair[1]
            else:
                d[pair[0]] = pair[1]

        regions = []
        for rl in d.values():
                region_count += len(rl)
                print(rl)
            for r in rl:
                regions.append(r)

        print('yo ' + len(regions))


        print("There are {} regions of interest".format(region_count))

        return d


def convertToMaskRCNN(regionImageData: dict):

    # apparently zooniverse annotators were able to mark places
    # outside of the image boundaries offset values are debatable but 15 px
    # seems to ensure all coordinates are within image boundaries.
    OFFSET_X = 15
    OFFSET_Y = 15

    # the actual JSON
    regionDataFormatted = dict()

    for img, regions in regionImageData.items():

        regionDataFormatted[img] = dict()

        regionValue = dict()  # the region is itself a dictionary
        for i in range(len(regions)):

            someD = dict()

            # x2 and y2 are such that the pixel coordinates are hopefully
            # within range of image without losing too much information
            x1 = regions[i][0]
            x2 = x1 + regions[i][2] - OFFSET_X

            y1 = regions[i][1]
            y2 = y1 + regions[i][3] - OFFSET_Y

            # four (x,y) points are needed to create a bounding box
            someD["shape_attributes"] = {
                "name": "polygon", "all_points_x": [
                    x1, x2, x2, x1], "all_points_y": [
                    y1, y1, y2, y2]}

            regionValue[str(i)] = dict()
            regionValue[str(i)] = someD

        regionDataFormatted[img]["filename"] = img
        regionDataFormatted[img]["regions"] = regionValue

    return regionDataFormatted


regionData = extractROIs(CSV_PATH)

for img in sorted(regionData.keys()):
    print(img)
regionDataFormatted = convertToMaskRCNN(regionData)

print(regionDataFormatted)

# the line below to be used for checking individual images and their ROIs
# print(regionDataFormatted["196.png"])
# print(regionDataFormatted['uclaclark_QD25S87_0150.png'])

print("There are {} elements in our zooniverse list".format(
    sum(1 for _ in regionData)))
