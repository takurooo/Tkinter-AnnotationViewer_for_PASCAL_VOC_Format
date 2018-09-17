# Tkinter-AnnotationViewer_for_PASCAL_VOC_Format
Annotation Viewer for PASCAL VOC Format.

# Requirement
- OpneCV

# Usage
```
python annotation_viewer.py
```

Push「Dir」menu.
Select your directory that includes 「img」 and 「annotation」 directory.

If you have directory structure below, you can select 「data」 directory.
```
current_dir/  
     ├ annotation_viewer.py  
     │
     ├ data/  
     │  ├ img/
     │  │   └ xxxx.jpg
     │  │
     │  └ annotation/
     │      └ xxxx.xml
     │
```
After you select 「data」 directory, annotation_viewer shows first image of 「img」 directory with annotation data.
