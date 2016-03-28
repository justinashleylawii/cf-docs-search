import sublime, sublime_plugin
import webbrowser
import urllib
import json

class Settings():
	def __init__(self):

		# Initialize settings
		settings = sublime.load_settings("CfDocsSearch.sublime-settings")

		self.settings = {}

		self.settings["base_html_url"] = "https://cfdocs.org/"
		self.settings["base_json_url"] = "https://github.com/foundeo/cfdocs/raw/master/data/en/"

	def get(self, key):
		return self.settings.get(key, "")
	
class MarkdownStyler():
	def bold(self, content):
		return "**" + str(content) + "**"

	def italicize(self, content):
		return "*" + str(content) + "*"

	def header(self, content, level):
		headerString = ""

		for i in range(0, level):
			headerString += "#"

		return headerString + " " + content + "\n\n"

	def list_item(self, content):
		return "+ " + content

	def code_block(self, content):
		return "`" + content + "`"

	def indent_code_block(self, content):
		return "\t" + content.replace("\n", "\n\t").replace("\r", "")

	def link(self, label, url):
		return "[" + label + "](" + url + ")"

class ViewBuilder():
	def __init__(self):
		self.mdStyler = MarkdownStyler()
		
	def add_line_if_defined(self, base, line, var):
		if var or var != "":
			base += line + "\n"

		return base

	def format_parameter(self, param):
		paramString = ""

		# Parameter type and name
		paramString += param["type"] + " " + self.mdStyler.bold(param["name"]) + "\n"
		paramString += self.mdStyler.italicize("Required:") + " " + str(param["required"]) + "\n"

		# Possible values
		valueString = self.mdStyler.italicize("Values:") + " " + str(param["values"])
		paramString = self.add_line_if_defined(paramString, valueString, param["values"])

		# Default value
		defaultString = self.mdStyler.italicize("Default:") + " " + str(param["default"])
		paramString = self.add_line_if_defined(paramString, defaultString, param["default"])

		# Description
		description = self.mdStyler.italicize("Description:") + "\n" + param["description"].replace("\n", "")
		paramString = self.add_line_if_defined(paramString, description, param["description"])

		return paramString

	def build_view(self, structure):
		viewContent = "\n"

		# Function/Tag name
		viewContent += self.mdStyler.header(structure["name"], 1)
		   
		# Function/Tag description
		viewContent = self.add_line_if_defined(viewContent, structure["description"], structure["description"])

		viewContent += "\n"

		# Syntax block (tag and script syntax)
		viewContent += self.mdStyler.header("Syntax", 2)

		# Tag syntax
		if "syntax" in structure:
			tagCodeString = self.mdStyler.code_block(structure["syntax"])
			tagString = self.mdStyler.list_item("Tag:\t\t" + tagCodeString)
			viewContent = self.add_line_if_defined(viewContent, tagString, structure["syntax"])

		# Script syntax
		if "script" in structure:
			scriptCodeString = self.mdStyler.code_block(structure["script"])
			scriptString = self.mdStyler.list_item("Script:\t" + scriptCodeString)
			viewContent = self.add_line_if_defined(viewContent, scriptString, structure["script"])

		viewContent += "\n"

		# Function parameters and tag attributes
		if "params" in structure and len(structure["params"]):
			if structure["type"] == "tag":
				attrLabel = "Attributes"
			else:
				attrLabel = "Parameters"

			viewContent += self.mdStyler.header(attrLabel, 2)

			for param in structure["params"]:
				viewContent += self.format_parameter(param) + "\n"

		# Links to external resources
		if "links" in structure and len(structure["links"]):
			viewContent += self.mdStyler.header("Links", 2)

			for link in structure["links"]:
				viewContent += self.mdStyler.list_item(self.mdStyler.link(link["title"], link["url"])) + "\n"

			viewContent += "\n"

		if "examples" in structure and len(structure["examples"]):
			viewContent += self.mdStyler.header("Examples", 2)

			for example in structure["examples"]:
				viewContent += self.mdStyler.header(example["title"], 3)

				# Example description
				viewContent = self.add_line_if_defined(viewContent, example["description"].replace("\r", "") + "\n", example["description"])

				# Example code
				viewContent += self.mdStyler.italicize("Code") + "\n\n"
				viewContent += self.mdStyler.indent_code_block(example["code"]) + "\n\n"

				# Example result
				if "result" in example and example["result"]:
					viewContent += self.mdStyler.italicize("Result") + "\n\n"
					viewContent += self.mdStyler.indent_code_block(example["result"])

		return viewContent

class CfDocsSearch():
	def __init__(self, view):
		self.view = view

	def get_selection_from_cursor(self, edit):
		selections = self.view.sel()

		if selections:
			cursor = self.view.substr(selections[0])

			if len(cursor) == 0:
				# TODO get word containing cursor
				print("CfDocsSearch: Please select some text and try again.")
				return ""
			else:
				return cursor

	def create_pane(self, edit, title, content):
		# Update the layout to have two panes side by side
		# TODO We might want to change this to give the user more choice
		window = self.view.window()
		window.run_command("set_layout", {"cols": [0.0,0.5,1.0],"rows": [0.0,1.0],  "cells": [[0,0,1,1],[1,0,2,1]]})
		window.focus_group(1)

		# Create the new file to hold the content
		new_view = window.new_file()
		new_view.erase(edit, sublime.Region(0, new_view.size()))          
		new_view.insert(edit, 0, content)

		# File settings
		new_view.set_name(title)

		# TODO Put this stuff into settings
		new_view.settings().set("word_wrap", "true")
		new_view.settings().set("syntax", "Packages/Markdown/Markdown.sublime-syntax")

		# Scratch tells sublime not to try and save when we close the tab
		new_view.set_scratch(True)
		window.focus_view(new_view)

class CfDocsBrowserCommand(sublime_plugin.TextCommand):
	def __init__(self, view):
		self.settings = Settings()
		self.docSearch = CfDocsSearch(view)
		self.view = view
		
	def build_url(self, search_text):
		url = self.settings.get("base_html_url") + search_text.lower()

		# urlencode the constructed url
		return urllib.parse.urlparse(url).geturl()

	def launch_browser(self, url):
		webbrowser.open(url)

	def run(self, edit):
		cursor = self.docSearch.get_selection_from_cursor(edit)

		if cursor:
			url = self.build_url(cursor)
			self.launch_browser(url)

class CfDocsPaneCommand(sublime_plugin.TextCommand):
	def __init__(self, view):
		self.settings = Settings()
		self.docSearch = CfDocsSearch(view)
		self.view = view
		self.viewBuilder = ViewBuilder()

	def build_url(self, search_text):
		url = self.settings.get("base_json_url") + search_text.lower() + ".json"
		return urllib.parse.urlparse(url).geturl()

	def get_response_data(self, url):
		try:
			responseData = urllib.request.urlopen(url).read().decode("utf-8", "replace").replace("\r", "")
			return responseData
		except:
			sublime.status_message("No data found for " + url)
			return ""

	def build_view(self, structure):
		# Take deserialized JSON structure and build view
		viewContent = self.viewBuilder.build_view(structure)
		return viewContent

	def display_output(self, edit, title, output):
		self.docSearch.create_pane(edit, title, output)

	def run(self, edit):
		cursor = self.docSearch.get_selection_from_cursor(edit)
	
		if cursor:
			url = self.build_url(cursor)
			responseJSON = self.get_response_data(url)

			if responseJSON:
				responseStructure = json.loads(responseJSON)
				viewContent = self.build_view(responseStructure)
				self.display_output(edit, "CfDocs: " + cursor, viewContent)
			else:
				sublime.message_dialog("No documentation found for \"" + cursor + "\"")