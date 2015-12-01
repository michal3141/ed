# dot = Dot("images/topics")
# graph = Graph("images/topics")
# print graph
# print dot
import sys


def convert(name):
    target = open("cFinder/" + name + "_gt1.nt", 'w')
    lines = {}
    for line in open('images/' + name + '.gv'):
        if "--" in line or "->" in line:
            leftRight = tuple(
                sorted([edge.strip() for edge in line.replace("\n", "").replace("->", "--").split("--")], key=str.lower)
            )
            leftRight = tuple([vertex.replace(" ", "_").replace("\"", "").replace("(", "").replace(")", "") for vertex in leftRight])
            if leftRight in lines:
                lines[leftRight] += 1
            else:
                lines[leftRight] = 1

    target.write("\n".join(["%s %s %s" % (leftRight[0], leftRight[1], weight)  for (leftRight, weight) in lines.items() if weight > 1]))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "usage: " + sys.argv[0] + " <filenameWithoutGV>"
        exit()
    for name in sys.argv[1:]:
        convert(name)
