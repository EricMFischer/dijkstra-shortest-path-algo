'''
The file contains an adjacency list representation of an undirected weighted graph with 200
vertices labeled 1 to 200. Each row consists of the node tuples that are adjacent to that
particular vertex along with the length of that edge. For example, the 6th row has 6 as the first
entry indicating that this row corresponds to the vertex labeled 6. The next entry of this row
"141,8200" indicates that there is an edge between vertex 6 and vertex 141 that has length 8200.
The rest of the pairs of this row indicate the other vertices adjacent to vertex 6 and the lengths
of the corresponding edges.

Your task is to run Dijkstra's shortest-path algorithm on this graph, using 1 (the first vertex)
as the source vertex, and to compute the shortest-path distances between 1 and every other vertex
of the graph. If there is no path between a vertex vv and vertex 1, we'll define the shortest-path
distance between 1 and vv to be 1000000.

You should report the shortest-path distances to the following ten vertices, in order:
7,37,59,82,99,115,133,165,188,197. You should encode the distances as a comma-separated string of
integers. So if you find that all ten of these vertices except 115 are at distance 1000 away from
vertex 1 and 115 is 2000 distance away, then your answer should be
1000,1000,1000,1000,1000,2000,1000,1000,1000,1000. Remember the order of reporting DOES MATTER.

IMPLEMENTATION NOTES: This graph is small enough that the straightforward O(mn) time
implementation of Dijkstra's algorithm should work fine. OPTIONAL: For those of you seeking an
additional challenge, try implementing the heap-based version. Note this requires a heap that
supports deletions, and you'll probably need to maintain some kind of mapping between vertices and
their positions in the heap.
'''
import pprint
import time


# input: file name
# output: object with vertex keys and their neighbors with weights
# e.g. ['2,20', '3,12']
def preprocess_adj_list(filename):
    graph = {}
    with open(filename) as f_handle:
        for line in f_handle:
            v_arr = line.split()
            k = v_arr[0]
            graph[k] = v_arr[1:]
    return graph


# input: object with vertex keys and their neighbors with weights
# output: Graph instantiated with input graph object
def create_graph(graph_obj):
    G = Graph()
    for v_k in graph_obj:
        v = Vertex(int(v_k))
        for nbr in graph_obj[v_k]:
            w_k, edge = nbr.split(',')
            v.add_nbr(int(w_k), int(edge))
        G.add_v(v)
    return G


# Vertex class for undirected graphs
class Vertex():
    def __init__(self, key):
        self._key = key
        self._nbrs = {}

    def __str__(self):
        return '{' + "'key': {}, 'nbrs': {}".format(
            self._key,
            self._nbrs
        ) + '}'

    def add_nbr(self, nbr_key, weight=1):
        if (nbr_key):
            self._nbrs[nbr_key] = weight

    def has_nbr(self, nbr_key):
        return nbr_key in self._nbrs

    def get_nbr_keys(self):
        return list(self._nbrs.keys())

    def remove_nbr(self, nbr_key):
        if nbr_key in self._nbrs:
            del self._nbrs[nbr_key]

    def get_e(self, nbr_key):
        if nbr_key in self._nbrs:
            return self._nbrs[nbr_key]


# Undirected graph class
class Graph():
    def __init__(self):
        self._vertices = {}

    # 'x in graph' will use this containment logic
    def __contains__(self, key):
        return key in self._vertices

    # 'for x in graph' will use this iter() definition, where x is a vertex in an array
    def __iter__(self):
        return iter(self._vertices.values())

    def __str__(self):
        output = '\n{\n'
        vertices = self._vertices.values()
        for v in vertices:
            graph_key = "{}".format(v._key)
            v_str = "\n   'key': {}, \n   'nbrs': {}".format(
                v._key,
                v._nbrs
            )
            output += ' ' + graph_key + ': {' + v_str + '\n },\n'
        return output + '}'

    def add_v(self, v):
        if v:
            self._vertices[v._key] = v
        return self

    def get_v(self, key):
        try:
            return self._vertices[key]
        except KeyError:
            return None

    def get_v_keys(self):
        return list(self._vertices.keys())

    # removes vertex as neighbor from all its neighbors, then deletes vertex
    def remove_v(self, key):
        if key in self._vertices:
            nbr_keys = self._vertices[key].get_nbr_keys()
            for nbr_key in nbr_keys:
                self.remove_e(nbr_key, key)
            del self._vertices[key]

    def add_e(self, from_key, to_key, weight=1):
        if from_key not in self._vertices:
            self.add_v(Vertex(from_key))
        if to_key not in self._vertices:
            self.add_v(Vertex(to_key))

        self._vertices[from_key].add_nbr(to_key, weight)
        self._vertices[to_key].add_nbr(from_key, weight)

    def get_e(self, from_key, to_key):
        if from_key and to_key in self._vertices:
            return self.get_v(from_key).get_e(to_key)

    # adds the weight for an edge if it exists already, with a default of 1
    def increase_e(self, from_key, to_key, weight=1):
        if from_key not in self._vertices:
            self.add_v(Vertex(from_key))
        if to_key not in self._vertices:
            self.add_v(Vertex(to_key))

        weight_u_v = self.get_v(from_key).get_e(to_key)
        new_weight_u_v = weight_u_v + weight if weight_u_v else weight

        weight_v_u = self.get_v(to_key).get_e(from_key)
        new_weight_v_u = weight_v_u + weight if weight_v_u else weight

        self._vertices[from_key].add_nbr(to_key, new_weight_u_v)
        self._vertices[to_key].add_nbr(from_key, new_weight_v_u)

    def has_e(self, from_key, to_key):
        if from_key in self._vertices:
            return self._vertices[from_key].has_nbr(to_key)

    def remove_e(self, from_key, to_key):
        if from_key in self._vertices:
            self._vertices[from_key].remove_nbr(to_key)
        if to_key in self._vertices:
            self._vertices[to_key].remove_nbr(from_key)

    def for_each_v(self, cb):
        for v in self._vertices:
            cb(v)


# Heap class
# input: order is 0 for max heap, 1 for min heap
class Heap():
    def __init__(self, order=1):
        self._heap = []
        self._min_heap = order

    def __str__(self):
        output = '['
        size = len(self._heap)
        for i, v in enumerate(self._heap):
            txt = ', ' if i is not size - 1 else ''
            output += str(v) + txt
        return output + ']'

    # input: parent and child nodes
    def _is_balanced(self, p, c):
        is_min_heap = p <= c
        return is_min_heap if self._min_heap else not is_min_heap

    def _swap(self, i, j):
        self._heap[i], self._heap[j] = self._heap[j], self._heap[i]

    # input: parent and child indices
    def _sift_up(self, p_i, c_i):
        if p_i == -1:
            return
        p = self._heap[p_i]
        c = self._heap[c_i]
        while (not self._is_balanced(p, c)):
            p_i = (c_i - 1) // 2
            self._swap(c_i, p_i)

            c_i = p_i
            if c_i is 0:
                break
            p = self._heap[(c_i - 1) // 2]

    # input: parent and child indices
    def _sift_down(self, p_i, c_i):
        while (c_i and not self._is_balanced(self._heap[p_i], self._heap[c_i])):
            self._swap(p_i, c_i)
            p_i = c_i
            c_i = self._get_swapped_child_index(p_i)

    def get_root(self):
        if self._heap:
            return self._heap[0]

    def get_nodes(self):
        return self._heap

    # inserts node in O(logn) time
    def insert(self, node):
        self._heap.append(node)
        node_i = len(self._heap) - 1
        self._sift_up((node_i - 1) // 2, node_i)

    # input: parent index
    # output: index of smaller or greater child, one index if other DNE, or None
    def _get_swapped_child_index(self, p_i):
        size = len(self._heap)
        i = p_i * 2 + 1
        j = p_i * 2 + 2
        if size <= i:
            return None
        elif size <= j:
            return i

        if self._heap[i] > self._heap[j]:
            return j if self._min_heap else i
        else:
            return i if self._min_heap else j

    def _extract_root(self):
        if self._heap:
            self._swap(0, len(self._heap) - 1)
            root = self._heap.pop()
            self._sift_down(0, self._get_swapped_child_index(0))
            return root

    # extracts minimum value in O(logn) time
    def extract_min(self):
        if not self._min_heap:
            raise ValueError('Only min heaps support extract_min')
        return self._extract_root()

    # extracts maximum value in O(logn) time
    def extract_max(self):
        if self._min_heap:
            raise ValueError('Only max heaps support extract_max.')
        return self._extract_root()

    # deletes node from anywhere in heap in O(logn) time
    # input: key (i.e. index) of node to delete
    def delete(self, key):
        self._swap(key, len(self._heap) - 1)
        removed = self._heap.pop()

        p_i = (key - 1) // 2
        if not self._is_balanced(self._heap[p_i], self._heap[key]):
            self._sift_up(p_i, key)
        else:
            self._sift_down(p_i, key)

        return removed

    # initializes a heap in O(n) time
    def heapify(self):  # to do
        return self._heap


'''
# input: Heap and object with shortest paths and corresponding v-w vertices
# output: updated vertex to heap index mapping
def update_vertex_heap_index_map(heap, shortest_paths):
    v_heap_i_map = {}
    heap = heap.get_nodes()
    for heap_i, path in enumerate(heap):
        w = shortest_paths[path][1]
        v_heap_i_map[w] = heap_i
    return v_heap_i_map
'''


# input: Graph, source key, and vertices to which to find a shortest path
# output: shortest path distances from source to input vertices
def dijkstra_shortest_path(G, source_k, vertices):
    X = {}  # explored vertices
    A = {}  # shortest path distances from source
    X[source_k] = 1
    A[source_k] = 0

    # heap implementation
    # heap = Heap()
    # v_heap_i_map = {}

    G_keys_len = len(G.get_v_keys())
    while len(X.keys()) is not G_keys_len:
        # records shortest path crossing the cut for every explored vertex
        # {100: [2,3]} -> shortest path from 2 is to 3 with distance 100
        shortest_paths = {}

        for v_k in X:
            v = G.get_v(v_k)
            nbr_keys = filter(lambda k: k not in X, v.get_nbr_keys())
            local_paths = {}  # local shortest paths
            for nbr_k in nbr_keys:
                local_paths[nbr_k] = A[v_k] + v.get_e(nbr_k)

            if local_paths:
                min_nbr_k = min(local_paths, key=local_paths.get)
                min_path = local_paths[min_nbr_k]
                # record shortest path for v_k. if v_k = 2, {100: [2,3]}
                shortest_paths[min_path] = [v_k, min_nbr_k]

                # heap implementation
                # insert_i = heap.insert(min_path)
                # v_heap_i_map[min_nbr_k] = insert_i

        # book-keeping for w_k
        v_k, w_k = shortest_paths[min(shortest_paths.keys())]
        X[w_k] = 1

        '''
        heap implementation
        heap_min_path = heap.extract_min()
        v_heap_i_map = update_vertex_heap_index_map(heap, shortest_paths)
        v_k, w_k = shortest_paths[heap_min_path]
        '''

        # in this implementation, we only set the A[w_k] after checking every explored to
        # unexplored vertex, i.e. it will definitively be the shortest path.
        A[w_k] = A[v_k] + G.get_v(v_k).get_e(w_k)

        '''
        heap implementation
        with a heap, we have to update the shortest paths to unexplored vertices (stored as
        Dijkstra greedy scores in the heap) each time we add to X and remove
        from the heap. This allows us to iteratively call extract_min to get the minimum
        Dijkstra greedy score, which is mapped to its vertex in path_v_map.
        w_nbr_keys = G.get_v(w_k).get_nbr_keys()
        for w_nbr_k in w_nbr_keys:
            w_w_nbr_edge = G.get_v(w_k).get_e(w_nbr_k)
            if w_nbr_k not in X:
                if v_heap_i_map.get(w_nbr_k, 0):
                    removed_path = heap.delete(v_heap_i_map[w_nbr_k])
                    w_nbr_k_path = min(removed_path, heap_min_path + w_w_nbr_edge)
                    # record shortest path for v_k. if v_k = 2, {100: [2,3]}
                    shortest_paths[w_nbr_k_path] = [w_k, w_nbr_k]
                    insert_i = heap.insert(w_nbr_k_path)
                    v_heap_i_map[w_nbr_k] = insert_i
        '''

    result = []
    for v_k in vertices:
        path = A[v_k] if A[v_k] else 1000000
        result.append(path)
    return result


def main():
    graph_obj = preprocess_adj_list('dijkstra_shortest_path.txt')
    # pprint.pprint(graph_obj, width=40)
    G = create_graph(graph_obj)
    # print(G)

    start = time.time()
    result = dijkstra_shortest_path(G, 1, [7, 37, 59, 82, 99, 115, 133, 165, 188, 197])
    print('result: ', result)
    print('elapsed time: ', time.time() - start)


main()
