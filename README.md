# Tkinter-AnnotationViewer_for_PASCAL_VOC_Format
Annotation Viewer for PASCAL VOC Format.

![image](https://user-images.githubusercontent.com/35373553/45608179-5a6bc480-ba8c-11e8-8e4b-b9efe9a258cd.png)


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
