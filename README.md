# sublime-surround

Sublime-surround is a [SublimeText 2](http://www.sublimetext.com/) plugin for adding, deleting and modifying text around the cursor or selection.

It makes it easy to do things like:

 * Change single quotes to double quotes
 * Change parentheses to square brackets
 * Change `<div id="my-custom-oldschool-header">lorem ipsum</div>` to `<header>lorem ipsum</header>`

It's a loving homage to [Tim Pope](https://github.com/tpope)'s [vim-surround](https://github.com/tpope/vim-surround), the yawning gap in my workflow when I switched from vim to SublimeText 2. While not a note-perfect port, I think it's a pretty nice translation of the concepts and functionality of the vim plugin to the sublime context.

The major piece missing is vim-surround compatible mappings for [Vintage](http://www.sublimetext.com/docs/2/vintage.html). I haven't worked out how to do that yet, but it's top of the todo list.

## Installation

### Using Git

Go to your Sublime Text 2 `Packages` directory and clone the repository using the command below:

`$ git clone https://github.com/jcartledge/sublime-surround.git`

### Download Manually

Download the files using the .zip download option.  
Unzip the files.  
Copy the folder to your Sublime Text 2 Packages directory.

### Package Control

This plugin is not yet available in the Package Control repository but I have submitted a pull request to have it added there and will update these instructions if/when that happens.

If you really can't wait, [here are instructions](http://wbond.net/sublime_packages/package_control/usage) (under **Add Repository**) for using Package Control to install plugins which are not in the official repository.

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

As in vim-surround, specifying the opening symbol in a pair as surround text will add inner whitespace around the wrapped text. If you don't want whitespace use the closing symbol.

Opening and closing items are interchangeable when specified as the text to replace or delete.

#### Examples:

**Changing `James Cartledge jcartledge@gmail.com`  
to `James Cartledge <jcartledge@gmail.com>`**

* Select the email address
* Invoke the Command Palette (`CTRL-SHIFT-P`/`CMD-SHIFT-P`)
* Select **Surround: surround selection**
* Type `>` and press enter

Note we use the closing symbol so no internal whitespace is added.

***

**Changing `if (a > 100) doSomething();`  
to `if (a > 100) { doSomething(); }`**

* Select the text `doSomething();`
* Invoke the Command Palette (`CTRL-SHIFT-P`/`CMD-SHIFT-P`)
* Select **Surround: surround selection**
* Type `{` and press enter

Note here that use of the opening symbol results in addition of internal whitespace.

***

**Changing `if (a > 100) { doSomething(); }`  
to `if (a > 100) doSomething();`**

* Place the cursor within the text `doSomething();`
* Invoke the Command Palette (`CTRL-SHIFT-P`/`CMD-SHIFT-P`)
* Select **Surround: delete surround**
* Type `{` or `}` and press enter

Note that when used as a search pattern rather than a replacement pattern the opening and closing symbols are interchangeable.

***

### Tag-aware

HTML/XML tags with attributes are supported, but slightly differently to vim-surround.

#### Examples

**Changing `Email me for more information`  
to `<a href="mailto:jcartledge@gmail.com">Email me</a> for more information`**

* Select the text `Email me`
* Invoke the Command Palette (`CTRL-SHIFT-P`/`CMD-SHIFT-P`)
* Select **Surround: surround selection**
* Type the opening tag including attributes: `<a href="mailto:jcartledge@gmail.com">` and press enter

***

**Changing `<div class="my-custom-header">lorem ipsum</div>`  
to `<header>lorem ipsum</header>`**

* Place the cursor within the text `lorem ipsum`
* Invoke the Command Palette (`CTRL-SHIFT-P`/`CMD-SHIFT-P`)
* Select **Surround: change surround**
* Type the opening tag to replace: `<div>` and press enter
* Type the replacement tag: `<header>`

Note it's not necessary to specify attributes for the tag you're trying to match - by not specifying attributes you're telling the command to match that tag with no or any attributes. If you specify attributes only a tag with the exact attributes you specify will be matched.

We don't specify any attributes for the replacement `header` tag here, but if we wanted to that would work fine just as in the mailto example above.

***

### Regular expressions

Any search text in change/delete which is not a recognised pair or tag and is longer than a single character is treated as a regular expression.

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
