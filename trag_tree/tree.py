from trag_tree.node import EntityNode
from queue import Queue


class EntityTree:

    def __init__(self, root_entity, data):

        self.root = EntityNode(root_entity)
        self.edges = {}
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
        while not temp_queue.empty():
            front = temp_queue.get()
            vis[front.get_entity()] = 1

            for sub_node in self.edges[front.get_entity()]:
                if sub_node is not None and sub_node != front.get_entity():
                    if front.get_parent() is None or ( front.get_parent() is not None \
                            and sub_node != front.get_parent().get_entity()):
                        if sub_node in vis:  # 无向有环图，不是树
                            self.root = None
                            return
                        new_node = EntityNode(sub_node)
                        front.add_children(new_node)
                        temp_queue.put(new_node)

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
        temp_queue = Queue()
        temp_queue.put(self.root)
        while not temp_queue.empty():
            front = temp_queue.get()
            if front.get_entity() == entity:
                return front
            for sub_node in front.get_children():
                if sub_node is not None:
                    temp_queue.put(sub_node)
        return None
