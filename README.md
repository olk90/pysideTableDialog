# pysideTableDialog

This repository serves as a template for table based applications written in
Python and PySide6. The theming is provided
by _[PyQtDarkTheme-fork](https://pypi.org/project/PyQtDarkTheme-fork/)_.

**Note that this repository does not provide a functional app on its own!**

## General Structure

All dialogs are initially loaded by UI files, as implemented in the file
`views/helpers.py`:

```python
def load_ui_file(filename):
    ui_file = QFile(filename)
    if not ui_file.open(QFile.ReadOnly):
        print("Cannot open {}: {}".format(filename, ui_file.errorString()))
        sys.exit(-1)
    return ui_file
```

All UI files are stored in the directory `ui`, while their Python
counterparts are to be found in the `views` folder.

The `logic` package contains the basic data model (s. `model.py`). The
persistence is managed by [SQLite](https://www.sqlite.org/index.html).
Furthermore, some helpers to access the database and other conveniences are
available in this package:

* `config.py` contains everything around the app itself, local settings
  about the database, locale or theme, etc.
* `queries.py` defines the queries that provide the information behind the
  table dialogs
* `table_models.py` is an assembly point for custom extensions
  of `QSqlQueryModel`. The general base class here provides a search 
  functionality that is connected to the search line of each table dialog (s.
  `ui/tableView.py`)

## Projects

These are projects, that are based on the structure provided by this repository:

* [pyIM](https://github.com/olk90/pyIM): An inventory management tool (Work
  in progress)
* [shift](https://github.com/olk90/shift): Planning tool for working schedules
  in the medical field

## Disclaimer

Since I've learned using PySide basically only "by doing", there might be
some best practices, I'm not aware of. So, if you have some suggestions or
improvements, feel free to share them!
