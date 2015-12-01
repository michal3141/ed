# dot = Dot("images/topics")
# graph = Graph("images/topics")
# print graph
# print dot
import sys


def convert(name):
    target = open("cFinder/" + name + ".nt", 'w')
    lines = {}
    for line in open('images/' + name + '.gv'):
        if "--" in line or "->" in line:
            leftRight = tuple(
                sorted([edge.strip() for edge in line.replace("\n", "").replace("->", "--").split("--")], key=str.lower)
            )
            if leftRight in lines:
                lines[leftRight] += 1
            else:
                lines[leftRight] = 1

    target.write("\n".join(["%s %s %s" % (leftRight[0], leftRight[1], float(weight))  for (leftRight, weight) in lines.items()]))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "usage: " + sys.argv[0] + " <filenameWithoutGV>"
        exit()
    for name in sys.argv[1:]:
        convert(name)
