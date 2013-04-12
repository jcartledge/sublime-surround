import sublime
import sublime_plugin
import re


class SurroundWindowCommand(sublime_plugin.WindowCommand):
    """ Base class for surround window commands """

    def run(self, sel=None):
        self.sel = sel
        self.window.show_input_panel(
            self.caption(), "", self.callback, None, None)


class SurroundSelectionWindowCommand(SurroundWindowCommand):
    """ Surround the current selection(s) with something """

    def caption(self):
        return "Surround with:"

    def callback(self, surround):
        args = {"surround": surround, "sel": self.sel}
        self.window.active_view().run_command("surround_selection", args)


class SurroundChangeCommand(SurroundWindowCommand):
    """ Change the surrounding of the current selection """

    def caption(self):
        return "Match"

    def callback(self, match):
        self.match = match
        self.window.show_input_panel(
            "Replace with:", "", self.replace_callback, None, None)

    def replace_callback(self, replacement):
        args = {"match": self.match, "replacement": replacement}
        self.window.active_view().run_command("surround_change_text", args)


class SurroundDeleteCommand(SurroundWindowCommand):
    """ Delete something surrounding something """

    def caption(self):
        return "Delete:"

    def callback(self, match):
        args = {"match": match, "replacement": ""}
        self.window.active_view().run_command("surround_change_text", args)


class SurroundTextCommand(sublime_plugin.TextCommand):
    """ Base class for surround text commands """

    def __init__(self, _):
        self.settings = sublime.load_settings("surround.sublime-settings")
        super(SurroundTextCommand, self).__init__(_)

    def pairs_for_replacement(self, surround):
        pairs = self.settings.get("surround_pairs_for_replacement")
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
        return self.tags_for_replacement(
            self.pairs_for_replacement([surround, surround]))


class SurroundSelectionCommand(SurroundTextCommand):
    """ Surround the current selection(s) with something """

    def run(self, edit, surround=None, sel=None):
        view = self.view

        # Vintage needs a text command for `ys<motion>`
        if(surround is None):
            sel = [[region.begin(), region.end()] for region in view.sel()]
            args = {"sel": sel}
            return view.window().run_command("surround_selection_window", args)

        if(sel is None):
            sel = view.sel()
        else:
            sel = [
                sublime.Region(int(region[0]), int(region[1]))
                for region in sel
            ]

        surround = self.preprocess_replacement(surround)
        for region in reversed(sel):
            view.insert(edit, region.end(), surround[1])
            view.insert(edit, region.begin(), surround[0])


class SurroundChangeTextCommand(SurroundTextCommand):
    """ Change something surrounding the current insertion point(s) to something else """

    def run(self, edit, match, replacement):
        search = self.search_patterns_for_surround(match)
        replacement = self.preprocess_replacement(replacement)
        view = self.view
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

    def find_start(self, to_pos, search):
        matches = self.find_between(0, to_pos, search)
        if len(matches) is 0:
            raise RuntimeError("Starting pair not found: " + search[0])
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
            raise RuntimeError("Ending pair not found: " + search[1])
        # balance pairs
        count_pairs = len(self.find_between(from_pos, next.begin(), search))
        if count_pairs % 2 is 0:
            return next
        else:
            return self.find_end(next.end(), search)

    def find_between(self, from_pos, to_pos, search):
        return [
            find for find in self.view.find_all(search[0], search[2])
            if find.end() <= to_pos
            and find.begin() >= from_pos
        ]

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
        pairs = self.settings.get("surround_pairs_for_search")
        return self.pair(surround, pairs)

    def tags_for_search(self, surround):
        matches = re.search(r"<([\S]+)([^>]*)>", surround[0])
        if matches:
            attrs = matches.group(2)
            if len(attrs) == 0:
                attrs = "([\s]+[^>]*)?"
            open_tag = str("<" + matches.group(1) + attrs + ">")
            close_tag = str("</" + matches.group(1) + ">")
            return [open_tag, close_tag]
        else:
            return surround
