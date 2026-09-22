# %%
import shelve

# %%
shelf = shelve.open('/home/zeke/hello/Booklet/booklet')
print(list(shelf.keys()))
print(dict(shelf))
