![Viper](https://viper-framework.readthedocs.io/en/latest/_images/viper.png)

This is a fork of the Viper-Framework repository. It has been designed to address a number of design changes which may not be accepted by the original developers. The key focus of these changes is to increase the robustness and automation of the framework so that it may be used on a larger scale more reliably - including better support for a Postgresql database backend.  Specifically:

**v2.0-rc12**
This is a minor release candidate, focussing on normalising the database and implementing better Project support for non-SQLite databases.
* Changed the Malware parent-child relationship back to an Adjacency list - similar to the main repository, but with an additional relationship to store a collection of children.
* Replaced the Project table with a singular String field within the Malware table
* Modified the Database find() function to search the current project by default, with an optional parameters to search all projects.
& Modified the /core/ui/cmd/find command to work with the new Database find() command (with the -a flag).

**v2.0-rc11**
* Binary storage indexing removed (all Malware is now stored in the root 'binaries' directory for each Project)
* The 'parent' field in the Malware table has been replaced with a Child Relation bridge table.
* Checks have been implemented to prevent cyclical hierarchy when adding a parent or child.
* Database().delete_analysis() has been implemented
* The 'report' command has been implemented - to show all notes and analysis for a sample.
* Modules will now run automatically when Malware is stored, depending on the mimetype. This is controlled by data/mime.conf
* A 'Project' table was added, allowing logical segmentation of Malware in Projects when using a singular database.
