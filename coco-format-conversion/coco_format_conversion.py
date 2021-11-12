import os
import pathlib
import json
from collections import OrderedDict
import argparse

from manga109 import *

d_info = OrderedDict([
    ("description", "Manga109"),
    ("url", "https://manga109.org"),
])

d_licenses = [OrderedDict([
    ("id", 0),
    ("url", "http://www.manga109.org/en/download.html"),
    ("name", "Manga109"),
])]

d_categories = [
    OrderedDict([
        ("id", 0),
        ("name", "frame"),
        ("supercategory", "frame"),
    ]),
    OrderedDict([
        ("id", 1),
        ("name", "text"),
        ("supercategory", "text"),
    ]),
    OrderedDict([
        ("id", 2),
        ("name", "face"),
        ("supercategory", "character"),
    ]),
    OrderedDict([
        ("id", 3),
        ("name", "body"),
        ("supercategory", "character"),
    ]),
]


def images_annotations(manga109_root_dir, train_val_cutoff, val_test_cutoff):
    images_path = pathlib.Path(manga109_root_dir) / "images"
    ret_images = []
    ret_annotations = []

    ret_images_val = []
    ret_annotations_val = []

    ret_images_test = []
    ret_annotations_test = []

    image_id_base = 0
    annotation_id_base = 0


    titlelist = manga109api.Parser(root_dir=manga109_root_dir).books
    for i_title, title in enumerate(titlelist):
        print("{}...".format(title), flush=True)
        titlepath = images_path / title

        # Images
        filelist = tuple(sorted(os.listdir(titlepath)))
        for i_file, (filename, page) in enumerate(zip(filelist, Book(title, manga109_root_dir).get_page_iter())):
            width, height = page.width, page.height
            id_int = i_file + image_id_base
            image = OrderedDict([
                ("license", 0),
                ("id", id_int),
                ("width", width),
                ("height", height),
                ("file_name", str(pathlib.Path(title) / filename)),
            ])
            (ret_images if i_title < len(titlelist) * train_val_cutoff else
             ret_images_val if i_title < len(titlelist) *
             val_test_cutoff else ret_images_test).append(image)

        # Annotations
        frame_bb_list = tuple(bb_iter(title, manga109_root_dir, categories=["frame"]))
        for i_id, (i_page, i_category, bb) in enumerate(frame_bb_list):
            bb_id = i_id + annotation_id_base
            image_id = i_page + image_id_base
            p1 = bb["@xmin"], bb["@ymin"]
            p2 = bb["@xmin"], bb["@ymax"]
            p3 = bb["@xmax"], bb["@ymax"]
            p4 = bb["@xmax"], bb["@ymin"]
            segmentation = [p1, p2, p3, p4]
            width = (bb["@xmax"] - bb["@xmin"])
            height = (bb["@ymax"] - bb["@ymin"])
            area = width * height
            annotation = OrderedDict([
                ("id", bb_id),
                ("image_id", image_id),
                ("category_id", i_category),
                ("segmentation", segmentation),
                ("area", area),
                ("bbox",  [bb["@xmin"], bb["@ymin"], width, height]),
                ("iscrowd", 0),
            ])
            (ret_annotations if i_title < len(titlelist) * train_val_cutoff
             else ret_annotations_val if i_title < len(titlelist) *
             val_test_cutoff else ret_annotations_test).append(annotation)

        image_id_base += i_file + 1
        annotation_id_base += i_id + 1
    return ret_images, ret_annotations, ret_images_val, ret_annotations_val, ret_images_test, ret_annotations_test

def getcoco(manga109_root_dir, train_val_cutoff, val_test_cutoff):
    (ret_images, ret_annotations,
     ret_images_val, ret_annotations_val,
     ret_images_test, ret_annotations_test) = images_annotations(
         manga109_root_dir, train_val_cutoff, val_test_cutoff)

    data_training = OrderedDict([
        ("info", d_info),
        ("licenses", d_licenses),
        ("images", ret_images),
        ("annotations", ret_annotations),
        ("categories", d_categories)
    ])

    data_val = OrderedDict([
        ("info", d_info),
        ("licenses", d_licenses),
        ("images", ret_images_val),
        ("annotations", ret_annotations_val),
        ("categories", d_categories)
    ])

    data_test = OrderedDict([
        ("info", d_info),
        ("licenses", d_licenses),
        ("images", ret_images_test),
        ("annotations", ret_annotations_test),
        ("categories", d_categories)
    ])

    return data_training, data_val, data_test


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert the Manga109 dataset XML to MSCOCO format.")
    parser.add_argument("manga109_root_dir",
                        type=str,
                        help="The root directory of the Manga109 dataset.")
    parser.add_argument("--outpath",
                        type=pathlib.Path,
                        default=pathlib.Path("./out/"),
                        help="The output directory.")
    parser.add_argument("--train-val-cutoff",
                        type=float,
                        default=0.8,
                        help="Cutoff ratio between the training and the validation datasets.")
    parser.add_argument("--val-test-cutoff",
                        type=float,
                        default=0.9,
                        help="Cutoff ratio between the validation and the testing datasets.")
    args = parser.parse_args()

    manga109_root_dir = pathlib.Path(args.manga109_root_dir)

    data_training, data_val, data_test = getcoco(manga109_root_dir, args.train_val_cutoff, args.val_test_cutoff)

    args.outpath.mkdir(parents=True, exist_ok=True)

    for outname, data_dict in zip(["train", "val", "test"], [data_training, data_val, data_test]):
        coco_json = json.dumps(data_dict)
        with open(str(args.outpath / "instances_{}.json".format(outname)), "wt") as f:
            f.write(coco_json)
