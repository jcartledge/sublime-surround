import sublime
import sublime_plugin
import re

import pprint
pp = pprint.PrettyPrinter()

# Clone of surround.vim for SublimeText 2


class SurroundCommand(sublime_plugin.TextCommand):
    def surround_pairs_for_addition(self, surround):
        pairs = {
            '{': ['{ ', ' }'],
            '}': ['{', '}'],
            '[': ['[ ', ' ]'],
            ']': ['[', ']'],
            '(': ['( ', ' )'],
            ')': ['(', ')'],
            '<': ['< ', ' >'],
            '>': ['<', '>']
        }
        return self.surround_pairs(surround, pairs)

    def surround_pairs(self, surround, pairs):
        if surround[0] in pairs:
            return pairs[surround[0]]
        else:
            return surround

    def surround_tags_for_addition(self, surround):
        matches = re.search(r"<([\S]+)[^>]*>", surround[0])
        if matches:
            return [surround[0], "</" + matches.group(1) + ">"]
        else:
            return surround

    def surround_addition(self, surround):
        surround = [surround, surround]
        surround = self.surround_pairs_for_addition(surround)
        surround = self.surround_tags_for_addition(surround)
        return surround

    def run_surround(self, edit, caption, callback):
        self.edit = edit
        window = self.view.window()
        window.show_input_panel(caption, '', callback, None, None)


class SurroundSelectionCommand(SurroundCommand):
    """
    Surround the current selection(s) with something
    """

    def run(self, edit):
        self.run_surround(edit, 'Surround with:', self.surround_selection)

    def surround_selection(self, surround):
        view = self.view
        surround = self.surround_addition(surround)
        for region in reversed(view.sel()):
            view.insert(self.edit, region.end(), surround[1])
            view.insert(self.edit, region.begin(), surround[0])


class SurroundChangeCommand(SurroundCommand):
    """
    Change something surrounding the current insertion points to something else
    """

    def run(self, edit):
        self.run_surround(edit, 'Match:', self.replace_with)

    def replace_with(self, surround):
        self.surround = surround
        window = self.view.window()
        window.show_input_panel(
            'Replace with:', '', self.replace_surround, None, None)

    def replace_surround(self, replacement):
        search = self.surround_search_patterns(self.surround)
        replacement = self.surround_addition(replacement)

        view = self.view
        for region in reversed(view.sel()):

            # find end
            end = view.find(search[1], region.end(), search[2])
            if end:

                # find start
                start = None
                possible_starts = view.find_all(search[0], search[2])
                for possible_start in reversed(possible_starts):
                    if possible_start.begin() < region.begin():
                        start = possible_start
                        break

                if start:
                    view.replace(self.edit, end, replacement[1])
                    view.replace(self.edit, start, replacement[0])

    def surround_search_patterns(self, surround):
        surround = [surround, surround]
        surround = self.surround_pairs_for_search(surround)
        surround = self.surround_tags_for_search(surround)

        if len(surround[0]) <= 1:
            flag = sublime.LITERAL
        else:
            flag = 0
        surround.append(flag)
        return surround

    def surround_pairs_for_search(self, surround):
        pairs = {
            '{': [u'{', u'}'],
            '}': [u'{', u'}'],
            '[': [u'[', u']'],
            ']': [u'[', u']'],
            '(': [u'(', u')'],
            ')': [u'(', u')'],
            '<': [u'<', u'>'],
            '>': [u'<', u'>']
        }
        return self.surround_pairs(surround, pairs)

    def surround_tags_for_search(self, surround):
        matches = re.search(r"<([\S]+)([^>]*)>", surround[0])
        if matches:
            attrs = matches.group(2)
            if len(attrs) == 0:
                attrs = '[^>]*'
            open_tag = unicode("<" + matches.group(1) + attrs + ">")
            close_tag = unicode("</" + matches.group(1) + ">")
            return [open_tag, close_tag]
        else:
            return surround


class SurroundDeleteCommand(SurroundChangeCommand):
    """
    Delete something surrounding current insertion point(s)
    """

    def run(self, edit):
        self.run_surround(edit, 'Delete:', self.delete_surround)

    def delete_surround(self, surround):
        self.surround = surround
        self.replace_surround('')
