import manga109api
from PIL import Image, ImageDraw
import argparse

def draw_rectangle(img, x0, y0, x1, y1, annotation_type):
    assert annotation_type in ["body", "face", "frame", "text"]
    color = {"body": "#258039", "face": "#f5be41",
             "frame": "#31a9b8", "text": "#cf3721"}[annotation_type]
    draw = ImageDraw.Draw(img)
    draw.rectangle([x0, y0, x1, y1], outline=color, width=10)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--manga109_root_dir")
    parser.add_argument("--book", default="ARMS")
    parser.add_argument("--page_index", type=int, default=6)
    args = parser.parse_args()

    manga109_root_dir = args.manga109_root_dir
    book = args.book
    page_index = args.page_index

    p = manga109api.Parser(root_dir=manga109_root_dir)
    annotation = p.get_annotation(book=book)
    img = Image.open(p.img_path(book=book, index=page_index))

    for annotation_type in ["body", "face", "frame", "text"]:
        rois = annotation["page"][page_index][annotation_type]
        for roi in rois:
            draw_rectangle(img, roi["@xmin"], roi["@ymin"], roi["@xmax"], roi["@ymax"], annotation_type)

    img.save("out.jpg")