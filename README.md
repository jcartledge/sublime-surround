# sublime-surround

Sublime-surround is a [SublimeText 2](http://www.sublimetext.com/) plugin for adding, deleting and modifying text around the cursor or selection.

It makes it easy to do things like:

 * Change single quotes to double quotes
 * Change parentheses to square brackets
 * Change `<div id="my-custom-oldschool-header">lorem ipsum</div>` to `<header>lorem ipsum</header>`

It's a loving homage to [Tim Pope](https://github.com/tpope)'s [vim-surround](https://github.com/tpope/vim-surround), the yawning gap in my workflow when I switched from vim to SublimeText 2. While not a note-perfect port, I think it's a pretty nice translation of the concepts and functionality of the vim plugin to the sublime context.

The major piece missing is vim-surround compatible mappings for [Vintage](http://www.sublimetext.com/docs/2/vintage.html). I haven't worked out how to do that yet, but it's top of the todo list.

## Installation

*blah*

## Basic use

All functionality is accessed through the SublimeText command palette: `CTRL-SHIFT-P` on Linux and Windows, `CMD-SHIFT-P` on Mac.

There are three commands:

 * **Surround: surround selection**
 * **Surround: change surround**
 * **Surround: delete surround**

**Surround selection** works on the current selection or selections. It prompts for the text to surround the selection with.

**Change surround** works on the current cursor or cursors. It prompts for wrapper text to replace, then for the text to replace it with.

**Delete surround** works on the current cursor or cursors. It prompts for wrapper text to delete. It is a special case of **Change surround** where the replacement is the empty string.

See below for more information about how search and surround text is handled.

## Features

### Pair-aware

Surround understands the following pairs:

 * `{}`
 * `[]`
 * `()`
 * `<>`

As in vim-surround, specifying the opening item in a pair as surround text will add inner whitespace around the wrapped text. If you don't want whitespace use the closing item.

Opening and closing items are interchangeable when specified as the text to replace or delete.

*[example]*

### Tag-aware

HTML/XML tags with attributes are supported, but slightly differently to vim-surround.

#### Tag as search text in Change surround or Delete surround:

*Search for the tag*

#### Tag as surround text in Surround selection or Delete surround:

### Regular expressions

Any search text in change/delete is treated as a regular expression if it's longer than one character. (If everything was treated as a regular expression you'd have to escape things like braces and parentheses.)

*Example of why this is cool.*

### Multiple cursors/selections

Surround *should* support multiple cursors and selections fine, but this hasn't been tested very thoroughly as I don't really use them.

## Mappings

There are no default key mappings; functionality is accessed through the SublimeText command palette.

There's nothing to stop you from creating mappings in your `User/Default.sublime-keymap` file. The commands you can map are:

 * `surround_selection`
 * `change_surround`
 * `delete_surround`

## Contributing

Go nuts. Clean, linted pull requests please :)

## Disclaimer

I have never written Python before in my life (apart from a one-line patch to another SublimeText plugin.) It's a great testament to the design of Python and the SublimeText 2 plugin API that I got this far. You have been warned.

## Prior art

There is (was? It doesn't seem to be on GitHub anymore...) another plugin with similar functionality, but I don't think it's very actively maintained and I was never able to get it to work properly.

## Todo

* vim-surround compatible vintage key mappings (possibly as a separate plugin)
* make repeat (`.`) work
