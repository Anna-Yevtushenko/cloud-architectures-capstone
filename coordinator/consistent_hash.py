
import hashlib
import bisect


class ConsistentHashRing:
    def __init__(self, virtual_nodes=64):
        self.virtual_nodes = virtual_nodes
        self.ring = []
        self.nodes = {}

    def _hash(self, value):
        return int(
            hashlib.sha256(value.encode("utf-8")).hexdigest(),
            16
        )

    def add_node(self, node_id):
        if node_id in self.nodes.values():
            return

        for i in range(self.virtual_nodes):
            hash_value = self._hash(f"{node_id}:{i}")
            bisect.insort(self.ring, hash_value)
            self.nodes[hash_value] = node_id

    def get_node(self, key):
        if not self.ring:
            return None

        hash_value = self._hash(key)
        index = bisect.bisect_left(self.ring, hash_value)

        if index == len(self.ring):
            index = 0

        return self.nodes[self.ring[index]]
