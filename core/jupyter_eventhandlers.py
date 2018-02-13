# -*- coding: utf-8 -*-
"""
Created on Thu Oct  5 17:03:55 2017

@author: a002087
"""

import difflib
import random
import requests
#import ipywidgets as widgets
import core 


def MultiCheckboxWidget(descriptions):
    """ Widget with a search field and lots of checkboxes """
    search_widget = widgets.Text()
    options_dict = {description: widgets.Checkbox(description=description, value=False) for description in descriptions}
    options = [options_dict[description] for description in descriptions]
    options_widget = widgets.VBox(options, layout = widgets.Layout(overflow = 'scroll'))
    multi_select = widgets.VBox([search_widget, options_widget])

    # Wire the search field to the checkboxes
    def on_text_change(change):
        search_input = change['new']
        if search_input == '':
            # Reset search field
            new_options = [options_dict[description] for description in descriptions]
        else:
            # Filter by search field using difflib.
            close_matches = difflib.get_close_matches(search_input, descriptions, cutoff = 0.0)
            new_options = [options_dict[description] for description in close_matches]
        options_widget.children = new_options

    search_widget.observe(on_text_change, names='value')
    return multi_select

## Example of using the widget
#
## Get lots of words for our options
#words_url = 'https://svnweb.freebsd.org/csrg/share/dict/words?view=co&content-type=text/plain'
#response = requests.get(words_url)
#response.raise_for_status()
#words = response.text
#words = set([word.lower() for word in words.splitlines()])
#descriptions = random.sample(words, 100)
#
#multi_checkbox_widget(descriptions)