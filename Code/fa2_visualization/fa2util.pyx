# cython: language_level=3
from libc.math cimport sqrt

cdef class Node:
    cdef public double mass
    cdef public double old_dx
    cdef public double old_dy
    cdef public double dx
    cdef public double dy
    cdef public double x
    cdef public double y

    def __init__(self):
        self.mass = 0.0
        self.old_dx = 0.0
        self.old_dy = 0.0
        self.dx = 0.0
        self.dy = 0.0
        self.x = 0.0
        self.y = 0.0

cdef class Edge:
    cdef public int node1
    cdef public int node2
    cdef public double weight

    def __init__(self):
        self.node1 = -1
        self.node2 = -1
        self.weight = 0.0

cpdef linRepulsion(Node n1, Node n2, double coefficient=0):
    cdef double xDist = n1.x - n2.x
    cdef double yDist = n1.y - n2.y
    cdef double distance2 = xDist * xDist + yDist * yDist  # Distance squared
    cdef double factor

    if distance2 > 0:
        factor = coefficient * n1.mass * n2.mass / distance2
        n1.dx += xDist * factor
        n1.dy += yDist * factor
        n2.dx -= xDist * factor
        n2.dy -= yDist * factor

cpdef linRepulsion_region(Node n, Region r, double coefficient=0):
    cdef double xDist = n.x - r.massCenterX
    cdef double yDist = n.y - r.massCenterY
    cdef double distance2 = xDist * xDist + yDist * yDist
    cdef double factor

    if distance2 > 0:
        factor = coefficient * n.mass * r.mass / distance2
        n.dx += xDist * factor
        n.dy += yDist * factor

cpdef linGravity(Node n, double g):
    cdef double xDist = n.x
    cdef double yDist = n.y
    cdef double distance = sqrt(xDist * xDist + yDist * yDist)
    cdef double factor

    if distance > 0:
        factor = n.mass * g / distance
        n.dx -= xDist * factor
        n.dy -= yDist * factor

cpdef strongGravity(Node n, double g, double coefficient=0):
    cdef double xDist = n.x
    cdef double yDist = n.y
    cdef double factor

    if xDist != 0 and yDist != 0:
        factor = coefficient * n.mass * g
        n.dx -= xDist * factor
        n.dy -= yDist * factor

cpdef linAttraction(Node n1, Node n2, double e, bint distributedAttraction, double coefficient=0):
    cdef double xDist = n1.x - n2.x
    cdef double yDist = n1.y - n2.y
    cdef double factor

    if not distributedAttraction:
        factor = -coefficient * e
    else:
        factor = -coefficient * e / n1.mass

    n1.dx += xDist * factor
    n1.dy += yDist * factor
    n2.dx -= xDist * factor
    n2.dy -= yDist * factor

cpdef apply_repulsion(list[Node] nodes, double coefficient):
    cdef int i = 0, j
    cdef Node n1, n2

    for n1 in nodes:
        j = i
        for n2 in nodes:
            if j == 0:
                break
            linRepulsion(n1, n2, coefficient)
            j -= 1
        i += 1

cpdef apply_gravity(list[Node] nodes, double gravity, double scalingRatio, bint useStrongGravity=False):
    cdef Node n
    for n in nodes:
        if not useStrongGravity:
            linGravity(n, gravity)
        else:
            strongGravity(n, gravity, scalingRatio)

cpdef apply_attraction(list[Node] nodes, list[Edge] edges, bint distributedAttraction, double coefficient, double edgeWeightInfluence):
    cdef Edge edge
    
    if edgeWeightInfluence == 0:
        for edge in edges:
            linAttraction(nodes[edge.node1], nodes[edge.node2], 1, distributedAttraction, coefficient)
    elif edgeWeightInfluence == 1:
        for edge in edges:
            linAttraction(nodes[edge.node1], nodes[edge.node2], edge.weight, distributedAttraction, coefficient)
    else:
        for edge in edges:
            linAttraction(nodes[edge.node1], nodes[edge.node2], pow(edge.weight, edgeWeightInfluence), distributedAttraction, coefficient)

cdef class Region:
    cdef public double mass, massCenterX, massCenterY, size
    cdef public list[Node] nodes
    cdef public list[Region] subregions

    def __init__(self, list[Node] nodes):
        self.mass = 0.0
        self.massCenterX = 0.0
        self.massCenterY = 0.0
        self.size = 0.0
        self.nodes = nodes
        self.subregions = []
        self.updateMassAndGeometry()

    cpdef updateMassAndGeometry(self):
        cdef double massSumX = 0
        cdef double massSumY = 0
        cdef double distance
        cdef Node n

        if len(self.nodes) > 1:
            self.mass = 0

            for n in self.nodes:
                self.mass += n.mass
                massSumX += n.x * n.mass
                massSumY += n.y * n.mass

            self.massCenterX = massSumX / self.mass
            self.massCenterY = massSumY / self.mass

            self.size = 0.0
            for n in self.nodes:
                distance = sqrt((n.x - self.massCenterX) ** 2 + (n.y - self.massCenterY) ** 2)
                self.size = max(self.size, 2 * distance)

    cpdef buildSubRegions(self):
        cdef list[Node] topleftNodes = []
        cdef list[Node] bottomleftNodes = []
        cdef list[Node] toprightNodes = []
        cdef list[Node] bottomrightNodes = []
        cdef Node n
        cdef Region subregion

        if len(self.nodes) > 1:
            for n in self.nodes:
                if n.x < self.massCenterX:
                    if n.y < self.massCenterY:
                        bottomleftNodes.append(n)
                    else:
                        topleftNodes.append(n)
                else:
                    if n.y < self.massCenterY:
                        bottomrightNodes.append(n)
                    else:
                        toprightNodes.append(n)
        
            if len(topleftNodes) > 0:
                if len(topleftNodes) < len(self.nodes):
                    subregion = Region(topleftNodes)
                    self.subregions.append(subregion)
                else:
                    for n in topleftNodes:
                        subregion = Region([n])
                        self.subregions.append(subregion)
        
            if len(bottomleftNodes) > 0:
                if len(bottomleftNodes) < len(self.nodes):
                    subregion = Region(bottomleftNodes)
                    self.subregions.append(subregion)
                else:
                    for n in bottomleftNodes:
                        subregion = Region([n])
                        self.subregions.append(subregion)
        
            if len(toprightNodes) > 0:
                if len(toprightNodes) < len(self.nodes):
                    subregion = Region(toprightNodes)
                    self.subregions.append(subregion)
                else:
                    for n in toprightNodes:
                        subregion = Region([n])
                        self.subregions.append(subregion)
        
            if len(bottomrightNodes) > 0:
                if len(bottomrightNodes) < len(self.nodes):
                    subregion = Region(bottomrightNodes)
                    self.subregions.append(subregion)
                else:
                    for n in bottomrightNodes:
                        subregion = Region([n])
                        self.subregions.append(subregion)
            
            for subregion in self.subregions:
                subregion.buildSubRegions()

    cpdef applyForce(self, Node n, double theta, double coefficient=0):
        cdef double distance
        cdef Region subregion

        if len(self.nodes) < 2:
            linRepulsion(n, self.nodes[0], coefficient)
        else:
            distance = sqrt((n.x - self.massCenterX) ** 2 + (n.y - self.massCenterY) ** 2)
            if distance * theta > self.size:
                linRepulsion_region(n, self, coefficient)
            else:
                for subregion in self.subregions:
                    subregion.applyForce(n, theta, coefficient)

    cpdef applyForceOnNodes(self, list[Node] nodes, double theta, double coefficient=0):
        cdef Node n
        for n in nodes:
            self.applyForce(n, theta, coefficient)

cpdef adjustSpeedAndApplyForces(list[Node] nodes, double speed, double speedEfficiency, double jitterTolerance):
    cdef double totalSwinging = 0.0
    cdef double totalEffectiveTraction = 0.0
    cdef double swinging
    cdef Node n

    for n in nodes:
        swinging = sqrt((n.old_dx - n.dx) * (n.old_dx - n.dx) + (n.old_dy - n.dy) * (n.old_dy - n.dy))
        totalSwinging += n.mass * swinging
        totalEffectiveTraction += 0.5 * n.mass * sqrt(
            (n.old_dx + n.dx) * (n.old_dx + n.dx) + (n.old_dy + n.dy) * (n.old_dy + n.dy))
    
    cdef double estimatedOptimalJitterTolerance = 0.05 * sqrt(len(nodes))
    cdef double minJT = sqrt(estimatedOptimalJitterTolerance)
    cdef double maxJT = 10
    cdef double jt

    jt = jitterTolerance * max(minJT,
                               min(maxJT, estimatedOptimalJitterTolerance * totalEffectiveTraction / (len(nodes) * len(nodes))))

    cdef double minSpeedEfficiency = 0.05
    # Return calculated jitter tolerance or any other required values

    if totalEffectiveTraction and totalSwinging / totalEffectiveTraction > 2.0:
        if speedEfficiency > minSpeedEfficiency:
            speedEfficiency *= 0.5
        jt = max(jt, jitterTolerance)

    cdef double targetSpeed
    if totalSwinging == 0:
        targetSpeed = float('inf')
    else:
        targetSpeed = jt * speedEfficiency * totalEffectiveTraction / totalSwinging

    if totalSwinging > jt * totalEffectiveTraction:
        if speedEfficiency > minSpeedEfficiency:
            speedEfficiency *= 0.7
    elif speedEfficiency < 1000:
        speedEfficiency *= 1.3

    cdef double maxRise = .5
    speed = speed + min(targetSpeed - speed, maxRise * speed)

    cdef double factor
    cdef dict values = {}

    for n in nodes:
        swinging = n.mass * sqrt((n.old_dx - n.dx) * (n.old_dx - n.dx) + (n.old_dy - n.dy) * (n.old_dy - n.dy))
        factor = speed / (1.0 + sqrt(speed * swinging))
        n.x += n.dx * factor
        n.y += n.dy * factor

    values['speed'] = speed
    values['speedEfficiency'] = speedEfficiency
    return values