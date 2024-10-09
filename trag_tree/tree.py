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
        self.all_nodes = {}

        while not temp_queue.empty():
            front = temp_queue.get()
            vis[front.get_entity()] = 1
            current_layer.append(front)
            self.all_nodes[front.get_entity()] = front

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
                for node in current_layer:
                    if node.get_children():                     # 每个节点，有该节点的所有子节点的BloomFilter
                        node.set_bloom_filter(node.get_all_descendants())
                current_layer = next_layer
                next_layer = []
        self.build_layer_filters()

    def build_layer_filters(self):
        # 获取到每一层的节点
        node_layers = {}
        for node in self.all_nodes.values():
            level = self.get_node_level(node)
            if level not in node_layers:
                node_layers[level] = []
            node_layers[level].append(node)

        # 将每一层的节点以及子节点放入layer_filters2
        max_level = max(node_layers.keys())
        for level in range(max_level, -1, -1):  # 从下往上逆序遍历，这样可以服用下层的bloomfilter信息
            layer_bloom_filter = BloomFilter(capacity=1000)
            for node in node_layers[level]:
                for entity in node.get_all_descendants():
                    layer_bloom_filter.add(entity)
                layer_bloom_filter.add(node.get_entity())
            self.layer_filters.insert(0, layer_bloom_filter)

    def get_node_level(self, node):
        """计算当前节点的层级深度"""
        level = 0
        while node.get_parent() is not None:
            level += 1
            node = node.get_parent()
        return level

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

    def bfs_search(self, entity):
        if self.root is None:
            return None
        temp_queue = Queue()
        temp_queue.put(self.root)
        while not temp_queue.empty():
            front = temp_queue.get()
            print(f"front: {front.get_entity()}")
            if front.get_entity() == entity:
                return front

             # if front.get_children() and entity not in front.get_bloom_filter():
                # return None  
            # 不能在这里直接服用bfs逻辑+用bloomfilter判断，因为该节点的子节点没有，不代表这一层其余节点的子节点也没有
            # 判断的信息不够完整，会出现有时对有时错的情况，且无法知道该层还剩多少节点，因此有两种方案
            # 1. bfs保持不变，修改BloomFilter，将node的BloomFilter设置为子节点+同一层的剩余兄弟节点，但这和层序遍历的BloomFilter几乎重合，且更奇怪，暂时抛弃
            # 2. BloomFilter保持不变，不采用bfs，改用层序遍历，这样可以通过遍历这一层所有节点，判断这一层所有节点的子节点是否存在目标节点，不会有信息遗漏
            #    缺点：和原层序遍历方案的思想几乎重合，还没有它方便，因为原方案直接判断这一层以及下面的子节点中是否存在，比一个一个去判断每个节点的下面子节点存在方便
            #    优点：如果树比较大，那么原方案这一层以及下面的子节点构成的BloomFilter可能过大，会不会出问题、以及速度过慢，每个节点的子节点构成的BloomFIlter更轻量
           
            for sub_node in front.get_children():
                if sub_node is not None:
                    temp_queue.put(sub_node)
        return None
     
    def layer_search(self, entity):
        if self.root is None:
            return None
        layer_index = 0
        temp_queue = Queue()
        temp_queue.put(self.root)

        while not temp_queue.empty():
            current_layer_size = temp_queue.qsize()
            if entity not in self.layer_filters[layer_index]:  # 一定不存在
                return None

            for _ in range(current_layer_size):  # 可能存在
                front = temp_queue.get()
                if front.get_entity() == entity: 
                    return front 
                
                for sub_node in front.get_children(): 
                    if sub_node is not None:
                        temp_queue.put(sub_node)

            layer_index += 1
        return None