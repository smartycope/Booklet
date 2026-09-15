# Source - https://stackoverflow.com/a/45364670
# Posted by khazhyk, modified by community. See post 'Timeline' for change history
# Retrieved 2026-09-15, License - CC BY-SA 4.0

class aobject(object):
    async def __new__(cls, *a, **kw):
        instance = super().__new__(cls)
        await instance.__init__(*a, **kw)
        return instance

    async def __init__(self):
        pass
