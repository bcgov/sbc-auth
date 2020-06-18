class SessionStorage:
    """Browser session storage."""

    def __init__(self, driver):
        """Init class."""
        self.driver = driver

    def __len__(self):
        """Get session storage item count."""
        return self.driver.execute_script('return window.sessionStorage.length;')

    def items(self):
        """Get session storage items."""
        return self.driver.execute_script(
            'var ls = window.sessionStorage, items = {}; '
            'for (var i = 0, k; i < ls.length; ++i) '
            '  items[k = ls.key(i)] = ls.getItem(k); '
            'return items; ')

    def keys(self):
        """Get session storage keys."""
        return self.driver.execute_script(
            'var ls = window.sessionStorage, keys = []; '
            'for (var i = 0; i < ls.length; ++i) '
            '  keys[i] = ls.key(i); '
            'return keys; ')

    def get(self, key):
        """Get session storage item by key."""
        return self.driver.execute_script('return window.sessionStorage.getItem(arguments[0]);', key)

    def has(self, key):
        """Return true if session storage has item."""
        return key in self.keys()

    def __getitem__(self, key):
        """Get session storage item by key."""
        value = self.get(key)
        if value is None:
            raise KeyError(key)
        return value

    def __contains__(self, key):
        """Return true if session storage has item."""
        return key in self.keys()

    def __iter__(self):
        return self.items().__iter__()

    def __repr__(self):
        return self.items().__str__()
