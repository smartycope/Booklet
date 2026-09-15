# Dev docs

## Pages
To avoid circular imports, Page classes are generated dynamically from strings returned by event functions (name of the class - the 'Page' suffix).
Abstract pages can be imported directly.

In order to handle async constructors (for example in the case that a page needs to make an async API call in order to load the initial data for the page), I've added an `aobject` class, which simply allows (requires) the \_\_init__ function to be marked as async.

The `Page` class is *not* an aobject, but all of the classes which inherit from it should be (with the exception of `StaticTextPage`). The reason the Page class itself is not an aobject is so we can have an ErrorPage that can be called syncronously (due to how the error handling works).

Remember to await any construction of a Page class!
