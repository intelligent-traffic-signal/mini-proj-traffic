with open("./additional.xml", "w") as routes:
    print("""<additional>""", file=routes)

    for inc in range(250):
        print('\t<laneData id="int_%i" begin="%i" end="%i" excludeEmpty="true" file="./trafficinfo_detailed.xml" />' % (inc, inc, inc + 1), file=routes)

    print("""</additional>""", file=routes)