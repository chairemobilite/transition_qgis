# Contributing to pyTransition

Transition-QGIS is a QGIS plugin designed to interact with the public API of the open-source transit planning application Transition, developed by the Chaire Mobilité research group of Polytechnique Montréal. It is an evolving platform.

## How can I contribute

There are many ways to contribute to the development of Transition-QGIS. Here's a few.

### Asking a question

You can use the [issue tracker](https://github.com/chairemobilite/transition_qgis/issues) of this GitHub project to ask a question. You can label it as a `question`. Before asking, make sure a similar question has not been asked before.

### Reporting bugs

If you use Transition-QGIS and encounter a bug, first make sure a similar issue has not been reported already. If not, you can file an issue in this project. Please provide all information required to reproduce the bug, and state the actual and expected behavior. Screenshots can greatly help visualize the issue.

### Requesting features and ideas

If there's something you would like to see in Transition-QGIS, no matter how big or small a change it may seem, you may start a discussion in the issue tracker [here](https://github.com/chairemobilite/transition_qgis/issues). Members of the community can join in the discussion.

### Developing the platform

If you want to start getting involved in the development of the Transition-QGIS plugin, a good idea is to contact the current development team, through an issue describing the bug you want to fix or the feature you want to implement.

Here are some development tips andprocedures to respect :

#### Cloning the repository for local development and installing dependencies
To contribute to the Transition-QGIS plugin, you can clone this reponsitory in `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`. The plugin should then be added to your installed plugins and can be visible in the plugin bar.

![alt text](docs/screenshots/plugin_icons.png)

In order to contribute to the project, you need to install the project dependencies. To do that, run the command :
```bash
pip install -r requirements.txt
``` 
You can then add or edit the code and see it reflected in QGIS. It is recommended to install the `plugin_reloader` plugin in QGIS in order to be able to easily reload the Transition-QGIS plugin when files have been edited.

#### Translating the plugin
All text visible by the user needs to be translated. To allow this, they need to be wrapped in a `self.tr` clause. For example :
```python
QLabel(self.tr("Departure or arrival time"))
```
The files that need to be translated need to be specified in the `i18n/transition_qgis.pro`. Once all the files are added to the .pro file, you need to run the followind command in the `i18n` directory :
```bash
pylupdate5 transition_qgis.pro
```
This command will update the `transition_qgis_fr.ts` file and add all text that needs to be translated to it with the correct line number. The command should be ran every time new visible text is added to the plugin.

After that, you can open the `transition_qgis_fr.ts` file in QT Linguist, write the translation of each field and save your changes.  This does not automatically delete older versions of the text but marks them as **obsolete** in the `transition_qgis_fr.ts`. The obsolete fields can be manually removed. 
Once that is done, run the following command in the `i18n` directory :
```bash
lrelease transition_qgis_fr.ts
```
This command will generate a new `transition_qgis_fr` binary file with the new translations.

#### Publishing the plugin
In order to publish the plugin, the `plugin_upload.py` script is used. You simply have to run the script. It will prompt you to enter your OSGEO credentials. The script will first zip the source code into a zip file, then attempt to publish it to QGIS,and lastly delete the zip file.\
To upgrade the version number for the new release, you must change the `version` property in the `metadata.txt` file and document your changes in the `changelog` section of the same file.
