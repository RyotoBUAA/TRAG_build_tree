from trag_tree.node import EntityNode
from queue import Queue
from pybloom_live import BloomFilter


class EntityTree:

    def __init__(self, root_entity, data):
        self.root = EntityNode(root_entity)
        self.edges = {}
        self.layer_filters = []
        for edge in data:
            if edge[0] not in self.edges:
                self.edges[edge[0]] = set()
            if edge[1] not in self.edges:
                self.edges[edge[1]] = set()
            self.edges[edge[0]].add(edge[1])
            self.edges[edge[1]].add(edge[0])

        temp_queue = Queue()
        temp_queue.put(self.root)
        vis = {}
        current_layer = []
        next_layer = []

        while not temp_queue.empty():
            front = temp_queue.get()
            vis[front.get_entity()] = 1
            current_layer.append(front)

            for sub_node in self.edges[front.get_entity()]:
                if sub_node is not None and sub_node != front.get_entity():
                    if front.get_parent() is None or ( front.get_parent() is not None \
                            and sub_node != front.get_parent().get_entity()):
                        if sub_node in vis:  # 无向有环图，不是树
                            self.root = None
                            print("invalid data, cycle exists, cannot build an EntityTree")
                            return
                        new_node = EntityNode(sub_node)
                        front.add_children(new_node)
                        next_layer.append(new_node)
                        temp_queue.put(new_node)

            if temp_queue.empty() and next_layer:
                layer_bloom_filter = BloomFilter(capacity=1000)
                for node in next_layer:
                    layer_bloom_filter.add(node.get_entity())
                self.layer_filters.append(layer_bloom_filter)

                for node in current_layer:
                    if node.get_children():
                        node.set_bloom_filter(node.get_all_descendants())
                current_layer = next_layer
                next_layer = []

    def set_bitset(self, hash_func):
        temp_queue = Queue()
        temp_queue.put(self.root)
        while not temp_queue.empty():
            front = temp_queue.get()
            front.set_bitset(hash_func)
            for sub_node in front.get_children():
                if sub_node is not None:
                    temp_queue.put(sub_node)

    def get_root(self):
        return self.root

    def print_tree(self):
        temp_queue = Queue()
        temp_queue.put(self.root)
        hierarchy = 0
        while not temp_queue.empty():
            print("hierarchy: "+str(hierarchy), end=" ")
            temp_queue_peer = Queue()
            while not temp_queue.empty():
                front = temp_queue.get()
                print(front.get_entity()+" ", end=" ")
                for sub_node in front.get_children():
                    if sub_node is not None:
                        temp_queue_peer.put(sub_node)
            while not temp_queue_peer.empty():
                temp_queue.put(temp_queue_peer.get())
            print("")
            hierarchy += 1

    # we can add bloom filter to judge whether the entity exists and terminates the bfs seatch early.
    # meanwhile, this method only applies in the situation that each node has a bloom filter. If each layer has a bloom filter, we should use layer search instead of bfs search. 
    def bfs_search(self, entity):
        if self.root is None:
            return None
        temp_queue = Queue()
        temp_queue.put(self.root)
        while not temp_queue.empty():
            front = temp_queue.get()
            if front.get_entity() == entity:
                return front
            if entity not in front.get_bloom_filter():
                return None
            for sub_node in front.get_children():
                if sub_node is not None:
                    temp_queue.put(sub_node)
        return None


    # 此函数逻辑上还有问题，需要调整        
    def layer_search(self, entity):
        if self.root is None:
            return None
        layer_index = 0
        temp_queue = Queue()
        temp_queue.put(self.root)

        while not temp_queue.empty():
            current_layer_size = temp_queue.qsize()
            if layer_index < len(self.layer_filters) and entity not in self.layer_filters[layer_index]:
                for _ in range(current_layer_size):
                    temp_queue.get()
                layer_index += 1
                continue
            for _ in range(current_layer_size):
                front = temp_queue.get()
                if front.get_entity() == entity:
                    return front, layer_index
                
                for sub_node in front.get_children():
                    if sub_node is not None:
                        temp_queue.put(sub_node)

            layer_index += 1
        return None, -1