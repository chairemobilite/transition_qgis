# Transition-QGIS
Transition-QGIS is a QGIS plugin designed to interact with the transit planning application Transition.\
Before using this plugin, users need to install the PYTransition python library that this plugin depends on in order to interact with the application. To install it, use the following command :
```bash
pip install pytransition
```
## Usage (end user)
Install `Transition-QGIS` through the QGIS plugin manager under Plugins > Manage and install plugins.

![alt text](docs/screenshots/manage_plugins.png)

![alt text](docs/screenshots/transition_plugin.png)

The Transition-QGIS plugin will then become available as an option in the "Plugins" tab and as an icon in the "Plugins" section of the QGIS toolbar.

![alt text](docs/screenshots/plugin_icons.png)

When the plugin opens, users are prompted to enter their login credentials to authenticate with the Transition application.

![alt text](docs/screenshots/login_prompt.png)

Users also have to provide the URL to the Transition server. The default value is `http://localhost:8080`, but can it be edited. 
The login process retrieves an authentication token from the Transition application. When the token expires, the user will be prompted to login again to obtain a new one.

After a successful login, the plugin appears as a dockwidget.\
The dockwidget features multiple tabs, each of which is outlined below.

### Home page

![alt text](docs/screenshots/home_page.png)

The home page offers the following functionalities :
- Get all the paths currently loaded in the Transition application.
- Get all the nodes currently loaded in the Transition application.
The results for each request will be displayed as a layer in QGIS.


### Routing page
![alt text](docs/screenshots/routing_page.png)

The routing page allows users to send a calculation request to the Transition application in order to receive a route. Users can choose transit modes, origin and destination points, as well as different parameters for transit, such as departure and waiting time.\
The result will be displayed as a group layer containing a separate layer for each mode.\
Users can also specify a route name to differenciate multiple routes. By default, if the ***Route name*** field is empty, the route name will be **Routing results**. If a new route is requested with the same name, it will replace the existing one.\
For transit, if the ***Calculate with alternatives*** option is checked, multiple alternatives can be returned. When that is the case, the alternative routes will be displayed in a sub-group.

### Accessibility map page
![alt text](docs/screenshots/accessibility_map_page.png)

The accessibility map page allows users to send a calculation request to the Transition application in order to receive an accessibility map. Users can choose the origin point as well as different parameters such as the departure and waiting time.\
Users can also specify an accessibility map name to differenciate multiple accessibility maps. By default, if the ***Accessibility map name*** field is empty, the route name will be **Accessibility map results**. If a new accessibility is requested with the same name, it will replace the existing one.\
If the **Separate polygons into different layers** option is checked, the result will be a group layer containing a separate layer for each polygon. Otherwise, the result will just be one layer containing all the polygons.

### Settings page
![alt text](docs/screenshots/settings_page.png)

The settings page contains read-only fields that display the connected user and the server URL currently being used. This mainly allows users to validate if the current URL is the desired one or if it needs to be changed.\
The page also allows users to log out from the plugin.  

## Contribute

### Clone the repository and install dependencies
To contribute to the Transition-QGIS plugin, you can clone this reponsitory in `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`. The plugin should then be added to your installed plugins and can be visible in the plugin bar.

![alt text](docs/screenshots/plugin_icons.png)

In order to contribute to the project, you need to install the project dependencies. To do that, run the command :
```bash
pip install -r requirements.txt
``` 
You can then add or edit the code and see it reflected in QGIS. It is recommended to install the `plugin_reloader` plugin in QGIS in order to be able to easily reload the Transition-QGIS plugin when files have been edited.

### Translate the plugin
All text visible by the user needs to be translated. To allow this, they need to be wrapped in a `self.tr` clause. For example :
```python
QLabel(self.tr("Departure or arrival time"))
```
The files that need to be translated need to be specified in the `i18n/transition_qgis.pro`. Once all the files are added to the .pro file, you need to run the followind command in the `i18n` directory :
```bash
pylupdate5 transition_qgis.pro
```
This command will update the `transition_qgis_fr.ts` file and add all text that needs to be translated to it with the correct line number. The command should be ran every time new visible text is added to the plugin.

After that, you can open the `transition_qgis_fr.ts` file in QT Linguist, write the translation of each field and save your changes.  This does not automatically delete older versions of the text but marks them as *outdated* in the `transition_qgis_fr.ts`. The outdated fields can be manually removed. 
Once that is done, run the following command in the `i18n` directory :
```bash
lrelease transition_qgis_fr.ts
```
This command will generate a new `transition_qgis_fr` binary file with the new translations.