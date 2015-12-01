# dot = Dot("images/topics")
# graph = Graph("images/topics")
# print graph
# print dot
import sys


def convert(name):
    target = open("cFinder/" + name + ".nt", 'w')
    for line in open('images/' + name + '.gv'):
        if "--" in line or "->" in line:
            target.write(" ".join([edge.strip() for edge in line.replace("\n", "").replace("->", "--").split("--")]) + "\n")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "usage: " + sys.argv[0] + " <filenameWithoutGV>"
        exit()
    for name in sys.argv[1:]:
        convert(name)
