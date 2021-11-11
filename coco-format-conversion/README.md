# COCO Format Conversion

This script converts the Manga109 XML annotations to MSCOCO's JSON format.

## Usage
Run the following command to execute the conversion. For the `--manga109-root-dir` option, specify the path to the Manga109 dataset root directory (not the "annotations" directory).

```bash
python coco_format_conversion.py --manga109-root-dir YOUR_DIR/Manga109_2017_09_28 --output-dir [out-dir] --train-val-cutoff [cutoff_ratio] --val-test-cutoff [cutoff_ratio]
```

The training-validation cutoff and validation-testing cutoff are set to 0.8 and 0.9 by default, repsectively.

## Output
The annotation will be outputted as three JSON files, each for training, validation, and the testing dataset, together containing all of the annotations in the provided Manga109 dataset.

The `file_name` attribute of each image will be set as `[title]/[page_index].jpg`, so that the `images` directory can be directly specified as the image locations when loaded as an MSCOCO dataset.
