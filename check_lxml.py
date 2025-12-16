import sys

print("sys.executable:", sys.executable)

print("\nTesting lxml import...")
try:
    import lxml
    print("lxml OK, version:", getattr(lxml, "__version__", "unknown"))
except Exception as e:
    print("lxml import failed:", type(e).__name__, e)

print("\nTesting BeautifulSoup + lxml...")
try:
    from bs4 import BeautifulSoup
    print("bs4 OK")
    print("BeautifulSoup with lxml:", BeautifulSoup("<p>ok</p>", "lxml").p.string)
except Exception as e:
    print("BeautifulSoup+lxml FAILED:", e)

