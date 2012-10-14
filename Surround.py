import sublime
import sublime_plugin
import re

surround_settings = sublime.load_settings('surround.sublime-settings')


class SurroundCommand(sublime_plugin.TextCommand):
    def surround_pairs_for_addition(self, surround):
        pairs = surround_settings.get('surround_pairs_for_addition')
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

    def run_surround(self, caption, callback):
        window = self.view.window()
        window.show_input_panel(caption, '', callback, None, None)


class SurroundSelectionCommand(SurroundCommand):
    """
    Surround the current selection(s) with something
    """

    def run(self, edit):
        # If this is called from Vintage the selection will be reset as soon as
        # the method returns, but we need it in the callback so we copy it here.
        self.sel = [sel for sel in self.view.sel()]
        self.run_surround('Surround with:', self.surround_selection)

    def surround_selection(self, surround):
        view = self.view
        surround = self.surround_addition(surround)
        edit = view.begin_edit()
        try:
            for region in reversed(self.sel):
                view.insert(edit, region.end(), surround[1])
                view.insert(edit, region.begin(), surround[0])
        finally:
            view.end_edit(edit)


class SurroundChangeCommand(SurroundCommand):
    """
    Change something surrounding the current insertion point(s) to something else
    """

    def run(self, edit):
        self.run_surround('Match:', self.replace_with)

    def replace_with(self, surround):
        self.surround = surround
        window = self.view.window()
        window.show_input_panel(
            'Replace with:', '', self.replace_surround, None, None)

    def replace_surround(self, replacement):
        search = self.surround_search_patterns(self.surround)
        replacement = self.surround_addition(replacement)
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
        count_closing_pairs = len(self.find_between(previous.end(), to_pos, close_search))
        if count_closing_pairs % 2 is 0:
            return previous
        else:
            return self.find_start(previous.begin(), search)

    def find_end(self, from_pos, search):
        next = self.view.find(search[1], from_pos, search[2])
        if next is None:
            raise RuntimeError('Ending pair not found: ' + search[1])
        # balance pairs
        count_opening_pairs = len(self.find_between(from_pos, next.begin(), search))
        if count_opening_pairs % 2 is 0:
            return next
        else:
            return self.find_end(next.end(), search)

    def find_between(self, from_pos, to_pos, search):
        found = []
        possible_finds = self.view.find_all(search[0], search[2])
        for possible_find in possible_finds:
            if possible_find.end() <= to_pos and possible_find.begin() >= from_pos:
                found.append(possible_find)
        return found

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
        pairs = surround_settings.get('surround_pairs_for_search')
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
        self.run_surround('Delete:', self.delete_surround)

    def delete_surround(self, surround):
        self.surround = surround
        self.replace_surround('')
