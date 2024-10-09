from pybloom_live import BloomFilter


class EntityNode:

    def __init__(self, entity):
        self.entity = entity  # 实体名称
        self.bitset = 0  # BF

        self.parent = None  # 父节点
        self.children = []  # 子节点

        self.bloom_filter = None

    def set_bitset(self, hash_func):
        self.bitset = hash_func(self.entity)

    def add_children(self, node):
        node.parent = self
        self.children.append(node)

    def get_children(self):
        return self.children

    def get_parent(self):
        return self.parent

    def get_bitset(self):
        return self.bitset

    def get_entity(self):
        return self.entity

    def get_bloom_filter(self):
        return self.bloom_filter

    def set_bloom_filter(self, entities):
        """为当前节点设置 Bloom Filter"""
        self.bloom_filter = BloomFilter(capacity=1000)  # 初始化 Bloom Filter
        for entity in entities:
            self.bloom_filter.add(entity)

    def get_all_descendants(self):
        """递归获取当前节点的所有后代节点"""
        descendants = set()
        for child in self.children:
            descendants.add(child.get_entity())  # 添加直接子节点
            descendants.update(child.get_all_descendants())  # 添加子孙节点
        return descendants