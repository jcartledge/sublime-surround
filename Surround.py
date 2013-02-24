import sublime
import sublime_plugin
import re

class SurroundWindowCommand(sublime_plugin.WindowCommand):
    """ Base class for surround window commands """

    def input_panel(self, caption, callback):
        self.window.show_input_panel(caption, '', callback, None, None)


class SurroundSelectionWindowCommand(SurroundWindowCommand):
    """ Surround the current selection(s) with something
    """

    def run(self):
        self.input_panel('Surround with:', self.callback)

    def callback(self, surround):
        self.window.active_view().run_command('surround_selection_text', {"surround": surround})


class SurroundTextCommand(sublime_plugin.TextCommand):
    """ Base class for surround text commands
    """

    def __init__(self, _):
        self.settings = sublime.load_settings('surround.sublime-settings')
        super(SurroundTextCommand, self).__init__(_)

    def pairs_for_replacement(self, surround):
        pairs = self.settings.get('surround_pairs_for_replacement')
        return self.pair(surround, pairs)

    def pair(self, surround, pairs):
        if surround[0] in pairs:
            return pairs[surround[0]]
        else:
            return surround

    def tags_for_replacement(self, surround):
        matches = re.search(r"<([\S]+)[^>]*>", surround[0])
        if matches:
            return [surround[0], "</" + matches.group(1) + ">"]
        else:
            return surround

    def preprocess_replacement(self, surround):
        surround = [surround, surround]
        surround = self.pairs_for_replacement(surround)
        surround = self.tags_for_replacement(surround)
        return surround


class SurroundSelectionTextCommand(SurroundTextCommand):
    """ Surround the current selection(s) with something
    """

    def run(self, edit, surround):
        view = self.view
        surround = self.preprocess_replacement(surround)
        for region in reversed(view.sel()):
            view.insert(edit, region.end(), surround[1])
            view.insert(edit, region.begin(), surround[0])


class SurroundChangeTextCommand(SurroundTextCommand):
    """ Change something surrounding the current insertion point(s) to something else
    """

    def run(self, edit):
        self.run_surround('Match:', self.replace_with)

    def replace_with(self, surround):
        self.surround = surround
        window = self.view.window()
        window.show_input_panel(
            'Replace with:', '', self.replace_surround, None, None)

    def replace_surround(self, replacement):
        search = self.search_patterns_for_surround(self.surround)
        replacement = self.preprocess_replacement(replacement)
        view = self.view
        edit = view.begin_edit()
        try:
            for region in reversed(view.sel()):
                end = self.find_end(region.end(), search)
                if end:
                    start = self.find_start(region.begin(), search)
                    if start:
                        self.view.replace(edit, end, replacement[1])
                        self.view.replace(edit, start, replacement[0])
        except RuntimeError as err:
            sublime.error_message(str(err))
        finally:
            view.end_edit(edit)

    def find_start(self, to_pos, search):
        matches = self.find_between(0, to_pos, search)
        if len(matches) is 0:
            raise RuntimeError('Starting pair not found: ' + search[0])
        previous = matches.pop()
        # balance pairs
        close_search = [search[1], search[0], search[2]]
        count_pairs = len(self.find_between(previous.end(), to_pos, close_search))
        if count_pairs % 2 is 0:
            return previous
        else:
            return self.find_start(previous.begin(), search)

    def find_end(self, from_pos, search):
        next = self.view.find(search[1], from_pos, search[2])
        if next is None:
            raise RuntimeError('Ending pair not found: ' + search[1])
        # balance pairs
        count_pairs = len(self.find_between(from_pos, next.begin(), search))
        if count_pairs % 2 is 0:
            return next
        else:
            return self.find_end(next.end(), search)

    def find_between(self, from_pos, to_pos, search):
        return [find for find in self.view.find_all(search[0], search[2])
            if find.end() <= to_pos
            and find.begin() >= from_pos]

    def search_patterns_for_surround(self, surround):
        surround = [surround, surround]
        surround = self.pairs_for_search(surround)
        surround = self.tags_for_search(surround)
        if len(surround[0]) <= 1:
            flag = sublime.LITERAL
        else:
            flag = 0
        surround.append(flag)
        return surround

    def pairs_for_search(self, surround):
        pairs = self.settings.get('surround_pairs_for_search')
        return self.pair(surround, pairs)

    def tags_for_search(self, surround):
        matches = re.search(r"<([\S]+)([^>]*)>", surround[0])
        if matches:
            attrs = matches.group(2)
            if len(attrs) == 0:
                attrs = '([\s]+[^>]*)?'
            open_tag = str("<" + matches.group(1) + attrs + ">")
            close_tag = str("</" + matches.group(1) + ">")
            return [open_tag, close_tag]
        else:
            return surround


class SurroundDeleteTextCommand(SurroundChangeTextCommand):
    """ Delete something surrounding current insertion point(s)
    """

    def run(self, edit):
        self.run_surround('Delete:', self.delete_surround)

    def delete_surround(self, surround):
        self.surround = surround
        self.replace_surround('')
