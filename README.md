# cf-docs-search

A Sublime Text 3 plugin for retrieving and displaying ColdFusion documentation for built-in functions and tags. Documentation is pulled from the repository behind [CFDocs.org](http://cfdocs.org) which can be found [https://github.com/foundeo/cfdocs/](here). Currently, all documentation is retrieved through an HTTP request, with no caching or offline functionality.

## Installation

To install, simply clone this repo to your Packages folder. This can be done by opening your terminal or command prompt to the Packages directory, and executing the following command:

```
git clone https://github.com/justinashleylawii/cf-docs-search.git
```

Sublime will automatically detect the plugin, and if nothing went wrong you should be able to start using it right away.

## Use

Select a ColdFusion tag or function (Usually double-clicking is the easiest way to do this). Then right click, and from the context menu, select either `ColdFusion Docs (in Pane)` or `ColdFusion Docs (in Browser)`.

### ColdFusion Docs (in Pane)

This searches the currently selected function or tag for a corresponding page in CFDocs. If it finds one, it will format the response using markdown, and display it in a pane to the right of the main code pane. Currently, this interferes with layouts other than single-pane layouts. This command works really well if you have a Markdown plugin installed which lets you preview the formatted markdown in the browser.

![Documentation pane screenshot with Material Solarized Dark color scheme](https://github.com/justinashleylawii/cf-docs-search/images/pane-screenshot.png)

You can close this pane like any other pane. To return to a single pane layout, in Sublime, go to `View -> Layout -> Single` or use the shortcut (by Default: `Alt+Shift+1`).

If documentation couldn't be found, a status message is displayed at the bottom of Sublime to indicate this.

### ColdFusion Docs (in Browser)

This command attempts to open your browser (or a tab of your browser) to the online CFDocs page for the selected function or tag.

## Known Issues

+ Plugin requires the tag name or function name to be highlighted in full, and without any extraneous characters (including spaces)
+ Requires a connection to the internet to work
+ Documentation pane doesn't play nice with layouts other than "single"
