class EntityNode:

    def __init__(self, entity):
        self.entity = entity  # 实体名称
        self.bitset = 0  # BF

        self.parent = None  # 父节点
        self.children = []  # 子节点

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