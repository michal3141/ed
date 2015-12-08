# dot = Dot("images/topics")
# graph = Graph("images/topics")
# print graph
# print dot
import sys


def convert(name, minWeight=1):
    target = open("cFinder/%s_gt%d.nt" % (name, int(minWeight)), 'w')
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

    target.write("\n".join(["%s %s %s" % (leftRight[0], leftRight[1], weight) for (leftRight, weight) in lines.items() if weight >= int(minWeight)]))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "usage: " + sys.argv[0] + " <filenameWithoutGV>"
        exit()
    files = [arg for arg in sys.argv[1:] if not arg.startswith("--")]
    options = dict([arg.replace("--", "").split("=") for arg in sys.argv[1:] if arg.startswith("--")])
    for name in files:
        convert(name, **options)
