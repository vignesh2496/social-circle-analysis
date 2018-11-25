import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def similarity(u, v):
    attribute_matrix = np.vstack([u.attributes, v.attributes])
    #print(cosine_similarity(attribute_matrix)[0][1])
    return cosine_similarity(attribute_matrix)[0][1]

def IoU_score(circle1, circle2):
    I = len(circle1.nodes.intersection(circle2.nodes))
    U = len(circle1.nodes.union(circle2.nodes))
    return I / U

class Node:
    def __init__(self, id, attributes, membership):
        self.id = id
        self.membership = membership
        self.attributes = attributes

class Circle:
    def __init__(self, id, nodes):
        self.id = id
        self.nodes = nodes
        self.num_nodes = len(nodes)

class Edge:
    def __init__(self, u_id, v_id):
        self.u_id = u_id
        self.v_id = v_id
        self.w = 0

class Graph:
    def __init__(self, nodes, edges, adjlist, circles):
        self.nodes = nodes
        self.edges = edges
        self.adjlist = adjlist
        self.circles = circles
        self.update_edge_weights()

    def randomized_add(self, node_id, circle_id):
        # print('add')
        node = self.nodes[node_id]
        circle = self.circles[circle_id]
        similarities = list(map(lambda id: \
                           similarity(node, self.nodes[id]), \
                                      circle.nodes))
        avg_similarity = sum(similarities) / len(similarities)
        prob = avg_similarity
        print(prob)
        flip = np.random.binomial(1, prob, 1)
        if flip == 1:
            node.membership.add(circle.id)
            circle.nodes.add(node.id)

    def union(self, u_id, v_id):
        u = self.nodes[u_id]
        v = self.nodes[v_id]
        u_diff_v = u.membership.difference(v.membership)
        for circle_id in u_diff_v:
            pass#self.randomized_add(v.id, circle_id)

        v_diff_u = u.membership.difference(v.membership)
        for circle_id in v_diff_u:
            pass#self.randomized_add(u.id, circle_id)

    def circle_formation(self):
        print('circle form')
        i=0
        for edge in self.edges:
            self.union(edge.u_id, edge.v_id)
            i+=1
            print('union' + str(i))

    def label_propagation(self, alpha):
        print('label prop')
        nodes_temp = self.nodes.copy()
        for node_id, node in self.nodes.items():
            neighbor_attributes = [self.nodes[neighbor_id].attributes for neighbor_id in self.adjlist[node_id]]
            neighbor_attributes = np.array(neighbor_attributes)
            neighbor_avg = np.average(neighbor_attributes, axis=0)
            nodes_temp[node_id].attributes = alpha * node.attributes + (1 - alpha) * neighbor_avg
        self.nodes = nodes_temp

    def dissolve_circles(self, threshold):
        print('dissolve')
        circles = self.circles.values()
        print(type(circles))
        for iter, circle1 in enumerate(circles):
            for circle2 in circles[iter + 1: ]:
                iou = IoU_score(circle1, circle2)
                if iou > threshold:
                    for node_id in circle2.nodes:
                        node = self.nodes[node_id]
                        node.membership.remove(circle2.id)
                        node.membership.add(circle1.id)
                        circle1.nodes.add(node_id)
                    del self.circles[circle2.id]

    def update_edge_weights(self):
        print('update')
        for edge in self.edges:
            u_id = edge.u_id
            v_id = edge.v_id
            edge.w = similarity(self.nodes[u_id], self.nodes[v_id])